#==============================================================
# Course Name : Information Retrieval
# Course Code : CZ4034
# Title       : Information Retrieval Assignment (Group Project)
# Topic       : Stock Search
#==============================================================
from django.test import TestCase  # Generated Django Library
from .models import Tweet         # Get Data models
import time                       # Use current date and time
import csv                        # Save test cases into csv format


# Simulate user inputs
class Test:
    # Constructor of Test
    def __init__(self, debug):
        self.debug = debug

    # Get All Possible Test Cases
    def getTestCases(self):
        testList = []

        emptyCases = ['']

        codeCases = ['BA','payc']

        companyCases = ['waste management inc']

        typoCases = ['wamart','singupora','meme stoack']

        testList = emptyCases + codeCases + companyCases + typoCases

        if(self.debug == True):
            {print('[Test] Get Test Cases :',testList)}
        return testList

    # Save all Test Cases Result into csv file
    def writeResult(self, testResult):
        field = ['s/n','test_case','rank','records','pos%','neg%','time_taken','text','company_name','code','subjectivity','polarity','suggestion','date_time','timestamp','query']
        with open('./test/test_'+ str(int(time.time())) +'.csv', 'w',  encoding='utf-8', newline= '') as csvfile:
            reader = csv.DictReader(csvfile)
            writer = csv.DictWriter(csvfile, fieldnames= field)
            writer.writeheader()
            
            testCount = 1
            
            for testCase,result,resultCount,timeTaken,polarity,suggestedList in testResult:
                rank = 1
                if(resultCount == 0):
                    writer.writerow({
                            's/n': str(testCount), 
                            'test_case' : str(testCase),
                            'rank' : str(rank),
                            'records': str(resultCount),
                            'pos%' : str(polarity[1]),
                            'neg%' : str(polarity[0]),
                            'time_taken' : str(timeTaken),
                            'text': str('No Result'),
                            'company_name' : str('No Result'),
                            'code' : str('No Result'),
                            'subjectivity': str('No Result'),
                            'polarity': str('No Result'),
                            'suggestion' : str(suggestedList),
                            'date_time' : str('No Result'),
                            'timestamp' : str('No Result'),
                            'query' : str('No Result')
                            })
                else:    
                    for item in result:
                        writer.writerow({
                            's/n': str(testCount), 
                            'test_case' : str(testCase),
                            'rank' : str(rank),
                            'records': str(resultCount),
                            'pos%' : str(polarity[1]),
                            'neg%' : str(polarity[0]),
                            'time_taken' : str(timeTaken),
                            'text': str(item.text),
                            'company_name' : str(item.companyName),
                            'code' : str(item.code),
                            'subjectivity': str(item.subjectivity),
                            'polarity': str(item.polarity),
                            'suggestion' : str(suggestedList),
                            'date_time' : str(item.dateTime),
                            'timestamp' : str(item.timestamp),
                            'query' : str(item.query)
                            })
                        rank += 1
                testCount += 1  

        
