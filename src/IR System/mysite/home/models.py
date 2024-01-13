#==============================================================
# Course Name : Information Retrieval
# Course Code : CZ4034
# Title       : Information Retrieval Assignment (Group Project)
# Topic       : Stock Search
#==============================================================
from django.db import models        # Django's model framework 

# Tweet Data Model
class Tweet(models.Model):
    text = models.TextField()
    dateTime = models.TextField()
    code = models.TextField()
    companyName = models.TextField()
    subjectivity = models.TextField()
    polarity = models.TextField()
    timestamp = models.TextField()
    query = models.TextField()

    # Constructor of Tweet
    def __init__(self, text, dateTime ,code , companyName, subjectivity, polarity, timestamp, query):
        self.text = text
        self.dateTime = dateTime
        self.code = code
        self.companyName = companyName
        self.subjectivity = subjectivity
        self.polarity = polarity
        self.timestamp = timestamp
        self.query = query

