#==============================================================
# Course Name : Information Retrieval
# Course Code : CZ4034
# Title       : Information Retrieval Assignment (Group Project)
# Topic       : Stock Search
#==============================================================
# Django-related libraries
from django.shortcuts import render                             # Allow rendering of UI
from django.http import HttpResponse, request                   # POST/GET http operations

# Local packages
from .models import Tweet                                       # Get Model Data
from .tests import Test                                         # It is use for evaluate query given a set of testcases

## (Internal) Libraries
import json                                                     # Allow read/write JSON file
import time                                                     # Allow Search Record Timing
import os                                                       # Manipulate local files
import random                                                   # Random suggestion

## (External) Libraries
# Preprocessing
from spellchecker import SpellChecker                           # Use for suggestion features (No way to select which is the best suggestion)
from nltk.corpus import stopwords                               # Remove unnecessary commoner words that has low relevance to the query
from nltk.tokenize import word_tokenize                         # Tokenize a words
import spacy                                                    # Entity extractor (names)
import pycountry                                                # Entity extractor (countries)
from difflib import get_close_matches                           # Return a list of good enough matches use for selecting suggestion candidates
# SOLR
import pysolr                                                   # Allow Query with SOLR

# [Model] Load model for named entity recognition
nlp = spacy.load("en_core_web_sm") 

# [Configure] - Use stop_words on english domain
stop_words = set(stopwords.words('english'))                    

# [Configure] - Spell Corrector is based on Peter Norvig's spell-corrector in English format.
# Utilize word statistics in order to find the most probable candidate. 
#spl = SpellCorrector(corpus="english") 
spell = SpellChecker(language='en')

# SOLR server connection integrity checks
try:
    solr = pysolr.Solr('http://localhost:8984/solr/test_server/', always_commit=True)
    # Do a health check.
    solr.ping()
    connection = True
except Exception as e:
    connection = False
    print('[WARNING]',e)   


# !----Configuration-----------------------------------------------------------------------------------------------------------------------
addDataOp = False              # A toggle to add static crawled data into SOLR in JSON format
debug = False                  # This remove unnecessary debugging statement in compiled code to maintain efficient query
fileName = 'tweets_v7_final'   # Select the file name use to read the data locally at mysite/static/data directory
testMode = False               # This generate a csv that contain all the test cases based on a given fixed inputs for testing and analysis uses
optmiseQuery = True            # Default - (Query the tweet SOLR) , Optimize - (Query with other feature/configuration SOLR has to offer)
# !----------------------------------------------------------------------------------------------------------------------------------------

# Cache variables
cacheInput = ''

# Display current dir path
if(debug == True):
    print("Path at terminal when executing this file")
    print(os.getcwd() + "\n")

# Render Template (HTML)
def index(request):

    # Run Test Cases list
    if(testMode == True):
        testResult = []
        testStock = Test(debug = debug)
        testCaseList = testStock.getTestCases()
        
        for testCase in testCaseList:
            # Start Timer
            startTime = time.time()
            # Preprocessing user inputs
            queryData, wordCount = preprocessing(debug = debug, data = testCase)
            queryData, queryMode, suggestMode = queryOpt(debug = debug, data = queryData, tokenCount = wordCount)
            suggestList = suggestionData(debug = debug, data = testCase, suggestMode = suggestMode)
            result , resultCount, polarity = fetchExternalData(debug = debug, queryData= queryData, queryMode= queryMode, start = 1)
            # Stop Timer
            stopTime = time.time()
            timeTaken = stopTime - startTime
            if(debug == True):
                print('Time Taken: ', timeTaken, 's')
            testResult.append([testCase ,result, resultCount, timeTaken,polarity,suggestList]) 
        
        testStock.writeResult(testResult = testResult)

        context = {
            'message' : 'Test Done, Please set testMode False to use the search system' 
        }
        print('Done')
        # Return not found template
        return render(request  = request, template_name = '404.html', context = context)
    

    # Start Timer
    startTime = time.time()

    # Check Connection
    if(connection == False):
        context = {
            'message' : 'Connection to Server Fail' 
        }
        # Return not found template
        return render(request  = request, template_name = '404.html', context = context)

    # Add Crawl Data into SOLR
    if(addDataOp == True):
        # Clear all SOLR Data
        deleteExternalData(debug = debug)

        # Get static data from local directory
        createExternalData(debug = debug)

        context = {
            'message' : 'Added ' +fileName + '.json Please Set addDataOp variable to False' 
        }
        # Return not found template
        return render(request  = request, template_name = '404.html', context = context)
    
    
    # Get Client Data (if any)
    userInput, page = getClientData(debug = debug, request = request)

    # Preprocessing user inputs
    queryData, wordCount = preprocessing(debug = debug, data = userInput)

    # Query Optimization
    queryData, queryMode, suggestMode = queryOpt(debug = debug, data = queryData, tokenCount = wordCount)

    # Return a list of suggestions if exist a likelyhood of typo
    suggestList = suggestionData(debug = debug, data = userInput, suggestMode = suggestMode)
    
    # Read the data given the query string and mode
    result, resultCount, polarity = fetchExternalData(debug = debug, queryData= queryData, queryMode= queryMode, start = page)

    # Stop Timer
    stopTime = time.time()
    timeTaken = stopTime - startTime
    if(debug == True):
        print('Time Taken: ', timeTaken, 's')

    # Place on Context to be parse into template in order for user to see
    context = {
        'time_taken' : timeTaken,
        'result_count' : resultCount,
        'result' : result,
        'page_count' : page,
        'current_search' : userInput,
        'pos_percent' : polarity[1],
        'neg_percent' : polarity[0],
        'query_result': queryData,
        'suggestion' : suggestList,
    }

    if(debug == True):
        print('[Render] Full-Page')
    # Return home template
    return render(request  = request, template_name = 'home.html', context = context)

# Provide suggestion should there be any typo
def suggestionData(debug, data, suggestMode):

    # Ignore suggestion if it is empty data
    if(data == '' or suggestMode == 0 or optmiseQuery == False):
        return []

    # Entity Extractor
    tokenList ,extractedList, extractedIndexList = entityExtractor(debug = debug , data = data)

    # Initialize variable
    bestSuggestList = []
    accumulateList = [[],[],[]] # A list that expand the list of possible candidates 
    suggestedList = [tokenList.copy(),tokenList.copy(),tokenList.copy(),tokenList.copy()] # 1 top best , other 3 best candidate

    # Check if there is any misspell
    misspelled = spell.unknown(extractedList)

    # If there is no misspell on all the non-entity words return empty list
    if(len(misspelled) == 0):
        if(debug): print('No Misspell Found!')
        return []

    # Find those words that may be misspelled by traverse every words in the input
    for curIndex,token in enumerate(extractedList,start = 0):
        misspelled = spell.unknown(token)
        # If there exist a mis spell
        if(len(misspelled) != 0):
            bestSuggestList.append(''.join(spell.correction(token)))
            candidateList = list(spell.candidates(token))
            # If there is more than one suggested candidates
            if(len(candidateList) > 1):
                # Take up to 3 best candidates
                selectedCandidateList = get_close_matches(token, candidateList)
                
                # for every selected suggested candidates
                for index, candidate in enumerate(selectedCandidateList, start = 0):
                    
                    # Add into the list 
                    accumulateList[index].append(candidate)
                if(len(selectedCandidateList) == 2):
                    accumulateList[2].append(token)
                elif (len(selectedCandidateList) == 1):
                    accumulateList[1].append(token)
                    accumulateList[2].append(token)
                     
            # Only 1 suggested candidates then just add in 
            else:
                for index in range(len(accumulateList)):
                    accumulateList[index].append(token)
        # No changes
        else:
            
            bestSuggestList.append(token)

    # Update into origin text
    for suggestIndex in range(len(accumulateList) + 1):
        if(debug):print('Running Suggestion: ',suggestIndex)
        if(suggestIndex == 0):
            for index, suggest in enumerate(bestSuggestList,start = 0):
                if(suggest == ''): continue
                suggestedList[suggestIndex][extractedIndexList[index]]  = suggest 
                if(debug):print(extractedIndexList[index])
                if(debug):print(suggestedList)
        else:

            for suggest in accumulateList[suggestIndex-1]:

                if(suggest == ''): continue
                suggestedList[suggestIndex][extractedIndexList[index]]  = suggest
                if(debug):print(extractedIndexList[index])
                if(debug):print(suggestedList)

    if(debug):print('Best Recommended:')
    if(debug):print(bestSuggestList)

    if(debug):print('Other Candidates:')
    if(debug):print(accumulateList)

    # Convert all list into string
    for index,suggestion in enumerate(suggestedList, start = 0):
        suggestedList[index] = ' '.join(suggestion)

    # Removed Duplicates
    suggestedList = list(set(suggestedList))

    # Remove input if exist
    try:
        suggestedList.remove(data)
    except:
        if(debug):print('')

    if(debug):print('Generated Suggestions:')
    if(debug):print(suggestedList)

    return suggestedList


def entityExtractor(debug, data):
    # Initialize
    extractedList = []
    extractedIndexList = []
    tokenList = []
    index = 0

    # Tokenise the data
    tokenExtractList = nlp(data)
    
    # For every word check if is belong to an entity
    for token in tokenExtractList:
        if(debug):print('[Entity] Checking Entity:',token.text)
        # Set initial false entity
        isEntity = False

        # Check if it is a country entity (Most likely search)
        if nlp(token.text.upper())[0].ent_type_ == 'ORG': # all capital to work
            if(debug):print('[Entity] Company Name Detected',token.text)
            isEntity = True  
        
        # Check if it is a country entity (Moderate likely search)
        if nlp(token.text.lower())[0].ent_type_ == 'PERSON' and isEntity == False: # all small letter to work
            if(debug):print('[Entity] Person Name Detected: ',token.text)
            isEntity = True  
           
        # Check if it is a country entity (Least likely search)
        if(isEntity == False):
            try:
                if(not pycountry.countries.get(name=token.text) is None):
                    if(debug):print('[Entity] Country Name Detected',token.text)
                    isEntity = True   
            except:
                if(debug): print('[Entity] Country Name Not Detected',token.text)

        # If it is not an entity append into a new list
        if(isEntity == False):
            extractedList.append(token.text)
            extractedIndexList.append(index)
        tokenList.append(token.text)
        index += 1
        
    if(debug): print('Extracted Index: ', extractedIndexList)
    return tokenList ,extractedList, extractedIndexList



def sampleQuery(debug, query, data, field):
    tolerancePercent = 0.25
    toleranceDist = round(len(data)*tolerancePercent)
    if(debug):print('Sampling Data:',data)
    if(debug):print('Number of Characters: ', len(data))
    if(debug):print('Tolerance Value:', toleranceDist)
    if(debug):print('Field Checking:' ,field)

    # Search for the result (Check for any returns)
    results = solr.search(query, start = 0)
    if(debug == True):
        print('[Query-Sample] Result Count('+ field +'):',results.hits)
    # If no match result return
    if(results.hits == 0):
        return False
    else:
        # Handle 'code' field
        if(field == 'code'):
            return True
        # Handle 'company' field
        elif(field == 'company'):

            # If exist one result exactly match the query
            for result in results:
                # Casefolding and Edit Distance to calculate within the tolerance range
                if(debug):print('Calculate Company Dist:', levenshtein((str(result[field]).lstrip('[\'').rstrip('\']').lower()),data), ' | Data:', data , ' | Result: ', result['company'])
                if(levenshtein((str(result[field]).lstrip('[\'').rstrip('\']').lower()),data) <= toleranceDist):
                    
                    return True
        else:
            print('[Warning] No Field Exist for Sampling')
    return False

def queryOpt(debug,data,tokenCount):

    # Check if permission to optimize query
    if(optmiseQuery == True): 
        # Query optimise base on number of token
        # Empty case
        if(int(tokenCount) == 0):
            if(debug == True):
                print('[Query-OPT] No token :(')
            
            return 'query:' + data, 1, 0 #sort by latest
        # Code max 1 token
        elif(int(tokenCount) == 1):
            # Check if it is exactly a code
            field = 'code'
            query = field +':"'+ data + '"'
            if(sampleQuery(debug = debug, query= query, field = field, data = data) == True):
                if(debug == True):
                    print('[Query-OPT]', query)
                
                return query, 0, 0

            # Check if it is likely a company
            field = 'company'
            query = field +':'+ data + '*'
            if(sampleQuery(debug = debug, query= query, field = field, data = data) == True):
                if(debug == True):
                    print('[Query-OPT]', query )
                return query, 0, 0

            # Else fail
            if(debug == True):
                print('[Query-OPT]', query)
            field = 'query'
            query = field +':'+ data
            return  query, 0, 1
        ## Company max 3 token
        elif(int(tokenCount) <= 3):
            # Check if it is likely a company
            field = 'company'
            query = field +':'+ data + '*'
            if(sampleQuery(debug = debug, query= query, field = field, data = data) == True):
                if(debug == True):
                    print('[Query-OPT]', query )
                return query, 0, 0
            
            # Else fail
            if(debug == True):
                print('[Query-OPT]', query)
            field = 'query'
            query = field +':'+ data
            return  query, 0, 1

        else:
            
            return 'query:' + data, 0, 1
    
    else:
        if(debug == True):
            print('[Query-OPT] No Query Optimisation')
        return 'text:' + data, 0, 0


# Pre-process User Input to Fit the Query to SOLR
def preprocessing(debug, data):

    # Lower Case
    data = data.lower()
    if(debug == True):
        print('[Preprocess] Case Folding:', data)

    # Remove Stopwords
    word_tokens = word_tokenize(data) 
    
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    
    filtered_sentence = [] 
    
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w) 

    if(debug == True):
        print('[Query-OPT] Word Tokenize: \n',word_tokens) 
        print('[Query-OPT] Removed Stopword: \n',filtered_sentence) 
    data = ' '.join(filtered_sentence)

    # Count Number of word
    wordCount = len(data.split())
    if(debug == True):
        print('[Preprocess] Word Count:', wordCount)

    # Check for empty cases
    if(wordCount == 0):
        if(debug == True):
            print('[Preprocess] QueryData:', '*')
        return '*', wordCount
    else:
        if(debug == True):
            print('[Preprocess] QueryData:', data)
        return data, wordCount

# Fetch External Data
def fetchExternalData(debug, queryData, queryMode, start):

    # Sorting Activate Desc
    if(queryMode == 1):
        if(debug):print('[Sort] Timestamp Latest')
        sort = 'timestamp desc'
    elif (queryMode == 2):
        if(debug):print('[Sort] Timestamp Oldest')
        sort = 'timestamp asc'
    else:
        if(debug):print('[Sort] Timestamp Default')
        sort = ''

    # Declaration
    dataList = []
    resultCount = 0
    polarity = [0,0] # suppose to be -1 but unable catch any exception for solr.search result
    try:
        # Get positive and negative count 
        neg = solr.search(queryData, rows = 0, fq = 'polarity:1')
        pos = solr.search(queryData, rows = 0, fq = 'polarity:2')
            
        # Get pos and neg percentile
        polarity = calculatePolarity(debug = debug, pos = pos.hits, neg = neg.hits)   

        # Search for the result
        results = solr.search(queryData, rows = 10, start = start - 1, sort = sort)
        for result in results:
            tweet = Tweet(
                text         =  str(result['text']).lstrip('[\'').rstrip('\']'),
                dateTime     =  str(result['date_time']).lstrip('[\'').rstrip('\']'),
                code         =  str(result['code']).lstrip('[\'').rstrip('\']'),
                companyName  =  str(result['company']).lstrip('[\'').rstrip('\']'),
                subjectivity =  str(result['subjectivity']).lstrip('[\'').rstrip('\']'),
                polarity     =  str(result['polarity']).lstrip('[\'').rstrip('\']'),
                timestamp    =  str(result['timestamp']).lstrip('[\'').rstrip('\']'),
                query        =  str(result['query']).lstrip('[\'').rstrip('\']'),
            )
            dataList.append(tweet)
        resultCount = results.hits
        

        if(debug == True):
            print("[FETCH-EXT]\n")
            tweetResult(dataList= dataList)
            print("[FETCH-COUNT]", resultCount)
            print("[FETCH-DISPLAY]", len(results), ' index: ', start , '-' , start + 9)
        
    except Exception as e:
        if(debug == True): 
            print('[FETCH-ERROR]',e)

    return dataList, resultCount, polarity

# Calculate overall pos and neg percentile Pos = 1 , Neg = 0
def calculatePolarity(debug, pos, neg):
    negPercent = -1
    posPercent = -1

    total = pos + neg
    
    if(debug):
        print('Positive Count:',pos)
        print('Negative Count:',neg)
        print('Total Count   :',total)
    if(total == 0):
            negPercent = 0
            posPercent = 0
    elif(pos== 0 and total > 0):
        negPercent = 100
        posPercent = 0
    elif(neg == 0 and total > 0):
        posPercent = 100
        negPercent = 0
    else:
        posPercent = round((pos/total)*100,1)
        negPercent = round((neg/total)*100,1)
    
    return [negPercent,posPercent]



# Manipulate External Data (Add)
def createExternalData(debug):
    try:

        # Opening and Read the whole JSON file 
        f = open('static/data/' + fileName + '.json',) 
        sampleData = json.load(f) 
        # Closing JSON file 
        f.close() 
        solr.add(sampleData)
        
        if(debug == True): 
            print('[EXT-DATA]','ADDED SUCCESSFULLY')
    except Exception as e:
        if(debug == True):
            print('[ADD-ERROR]',e)

# Manipulate External Data (Delete)
def deleteExternalData(debug):
    try:
        solr.delete(q='*:*') # Delete All Document
        if(debug == True):
            print('[EXT-ACTION] DELETE ALL')
    except Exception as e:
        if(debug == True):
            print('[DEL-ERROR]',e)


# Get Client Query Data
def getClientData(debug,request):
    # Declaration
    global cacheInput
    data_search = ''
    page_count = 1

    # Get Data
    if request.method == 'POST':
        try:
            # Get Client Data
            if request.POST.get('data_search') is not None:
                
                data_search = request.POST.get('data_search')
                # Check if there is changes to previous input
                if(data_search != cacheInput):
                    # Reset Page Count
                    cacheInput = data_search
                else:
                    page_count = int(request.POST.get('page_count'))
                    

        except Exception as e:
            if(debug == True): 
                print('[POST-ERROR]',e)

        if(debug == True):
            print('[POST] Executed')
            print('[GET-SEARCH]', data_search)
            print('[GET-PAGECOUNT]', page_count)
    
    return data_search, page_count

# Display all the tweet result at console
def tweetResult(dataList):
    for index,data in enumerate(dataList, start = 1):
        print('==================Tweet[',index,']==================')
        print('Text          :', data.text)
        print('Date Time     :', data.dateTime)
        print('Code          :', data.code)
        print('Company Name  :', data.companyName)
        print('Subjectivity  :', data.subjectivity)
        print('Polarity      :', data.polarity)
        print('Query         :', data.query)
        print('Time Stamp    :', data.timestamp)

# Calculate similarity distance with Levenshtein distance
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]




