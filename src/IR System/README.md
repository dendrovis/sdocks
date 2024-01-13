# Project Overview
Build a basic search engine for information retrieval.

# Learning Outcomes
1. Code with necessary packages to build a preliminary search engine.
2. Describe and distinguish various retrieval systems.
3. Apply fundamental clustering, classification and web search technique, solve problems, such as computations and designs.

# How to use the program 101 guidelines
## Prerequisite:
1. Setup SOLR and Django properly.
    * nSOLR Installation Guide Link: https://solr.apache.org/guide/7_0/installing-solr.html.
    * Django Installation Guide Link: https://docs.djangoproject.com/en/3.1/topics/install/.
2. Setup VSCode IDE properly.
    * VSCode Latest Package Link: https://code.visualstudio.com/.
3. Setup Python properly.
    * Python Latest Package Link: https://www.python.org/downloads/. (Recommended: Ver 3.8.2 and above)
4. Install external packages.
    * “nltk” : https://pypi.org/project/nltk/.
    * “pysolr” : https://pypi.org/project/pysolr/.
    * “autocomplete” : https://pypi.org/project/autocomplete/.
    * “pyspellchecker” : https://pypi.org/project/pyspellchecker/.
    * “ekphrasis” : https://pypi.org/project/ekphrasis/. 
5. Downloaded and extract our project’s source code file called  “test_django-main.zip” into your local directory workspace.

## Setup Hosting:
### SOLR (Backend - Database)
1.	Open your command prompt (CMD) window.
2.	Key in and enter the following script in the command line: “solr start -p 8984”.
3.	Once entered you should be able to see this output at the last line of the command prompt: "Started Solr server on port 8984. Happy searching!".
4.	Key in and enter the following script at your browser to access the SOLR GUI of the hosting details: “http://localhost:8984/”.
5.	(Optional) Key in and enter the following script in the command line to end hosting the server: “solr stop -p 8984”.
### Django (Frontend)
1.	Open your VSCode IDE.
2.	Access the top window panel, clicked on 'File' dropdown menu.
3.  Click 'Open Workspace'.
4.	An window should pop up request you to select your extracted.
5.	At VSCode’s explorer section, right click 'mysite' directory.
6.  Click 'Open in integrated terminal'.
7.	A pop-up “bash” terminal should be visible.
8.	Key in and enter the following script: “python manage.py runserver”.
9.	Key in and enter the local IP address and port number to access the local web page as follows: “http://127.0.0.1:8000/”.
10.	(Optional) At terminal key “CTRL+C” to end hosting the server.

## Misc Configuration:
The configuration helps us to separate our concerns more easily. Thus, improve the workflow. Our configuration code can be located at “mysite/static/home/views.py”.

The configuration variable:
* addDataOp = False        # A toggle to add static crawled data into SOLR in JSON format
* debug = False            # This remove unnecessary debugging statement in compiled code to maintain efficient query
* fileName = 'tweets_v4'   # Select the file name use to read the data locally at mysite/static/data directory
* testMode = False         # This generate a csv that contain all the test cases based on a given fixed inputs for testing and analysis uses
* optmiseQuery = True      # Default - (Query the tweet SOLR) , Optimize - (Query with other feature/configuration SOLR has to offer)

## Disclaimer
All information retrieve are intended use for education purpose, no copyright infringement intended

## License
The software present here are open source and intended to be used for education purpose only. All the code is provided by us is sole for assessment purpose as well. This software have not been thoroughly tested under all conditions. We, therefore, cannot guarantee or imply reliability, serviceability, or function of this software.

## Version
1.0

## About the course
* Course Name : Information Retrieval
* Course Code : CZ4034
* Title       : Information Retrieval Assignment (Group Project)
* Topic       : Stock Search