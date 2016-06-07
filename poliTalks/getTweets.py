import os
import sys
import tweepy
from tweepy import OAuthHandler

currentDir = os.path.dirname(os.path.abspath(__file__))

#authentication stuff
consumer_key = 'SDSxLoUOU5eNAQEOkvvEwTFKi'
consumer_secret = 'D1ikExbbdX6xZ13IDQrDnXUqTEh1VG5vxZtp7pJ1zg6Hmteent'
access_token = '76215622-BmkW83GMTl1ZB9ctNgVB22TSBo9saoUMByrxp7mW0'
access_token_secret = 'FeUDn5Sdn1yVxLh30Wlg9pgREvc2AQtcq5uSKKUE892EV'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def grabTweets(screenName, numTweets, fromID):
    return api.user_timeline(screen_name = screenName, count = numTweets, max_id = fromID)

def writeTweetsToFile(tweets, directory):
    nameOfFile = str(tweets[0].author.screen_name) + '.txt'
    writeFile = open(directory + '/' + nameOfFile, 'w')
    for t in tweets:
        writeFile.write(t.text.encode('ascii', 'ignore') + '\n')
    writeFile.close()
    return nameOfFile

#grab initial 200 tweets for training
#trumpTweets = api.user_timeline('realDonaldTrump', count = 200)
#cruzTweets = api.user_timeline('SenTedCruz', count = 200)

clintonTweets = api.user_timeline('HillaryClinton', count = 200)
sandersTweets = api.user_timeline('SenSanders', count = 200)


#write to file
cName = writeTweetsToFile(clintonTweets, currentDir)
sName = writeTweetsToFile(sandersTweets, currentDir)

#train classifier
os.system('crm learn.crm clinton < ' + cName)
os.system('crm learn.crm sanders < ' + sName)

#get older clinton tweets and classify
oldClinton = grabTweets('HillaryClinton', 10, clintonTweets[-1].id)
cOld = writeTweetsToFile(oldClinton, currentDir)
os.system('crm classify.crm < ' + cOld)


