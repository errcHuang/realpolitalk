import os
import sys
import subprocess
import tweepy
from tweepy import OAuthHandler

#authentication stuff
__consumer_key__ = 'SDSxLoUOU5eNAQEOkvvEwTFKi'
__consumer_secret__ = 'D1ikExbbdX6xZ13IDQrDnXUqTEh1VG5vxZtp7pJ1zg6Hmteent'
__access_token__ = '76215622-BmkW83GMTl1ZB9ctNgVB22TSBo9saoUMByrxp7mW0'
__access_token_secret__ = 'FeUDn5Sdn1yVxLh30Wlg9pgREvc2AQtcq5uSKKUE892EV'

__auth__ = tweepy.OAuthHandler(__consumer_key__, __consumer_secret__)
__auth__.set_access_token(__access_token__, __access_token_secret__)

__api__ = tweepy.API(__auth__)

def main():
    reset_corpus()

    currentDir = os.path.dirname(os.path.abspath(__file__))
    #grab initial 200 tweets for training
    trumpTweets = __api__.user_timeline('realDonaldTrump', count = 200)
    cruzTweets = __api__.user_timeline('SenTedCruz', count = 200)

    clintonTweets = __api__.user_timeline('HillaryClinton', count = 200)
    sandersTweets = __api__.user_timeline('SenSanders', count = 200)


    #train classifier
    train_classifier('trump', write_tweets_to_file(trumpTweets, currentDir))
    train_classifier('cruz', write_tweets_to_file(cruzTweets, currentDir))
    train_classifier('clinton', write_tweets_to_file(clintonTweets, currentDir))
    train_classifier('sanders', write_tweets_to_file(sandersTweets, currentDir))
    

    #get older clinton tweets and classify
    oldClinton = grab_tweets('HillaryClinton', 10, clintonTweets[-1].id)

    #classify and split probabilities into list
    probList = classify(write_tweets_to_file(oldClinton, currentDir)).split()
    bestMatch = (str(probList[0]), float(probList[1])) #(best_candidate, probability)
    probList = probList[2:] 


    clean_workspace()

def train_classifier(candidate, trainingTxtFile):
    subprocess.call('crm learn.crm ' + candidate + ' < ' + trainingTxtFile, shell=True)


# returns string that contains probabilities 
# (bestMatch bestProb hillaryProb bernieProb donaldProb tedProb)
def classify(textFileName):
    return subprocess.check_output('crm classify.crm < ' + textFileName, shell=True)

def grab_tweets(screenName, numTweets, fromID):
    return __api__.user_timeline(screen_name = screenName, count = numTweets, max_id = fromID)

"""
saves tweets to text file under FirstnameLastname.txt by default
returns filename (string)

Note: make sure tweets isn't empty or else errors
"""
def write_tweets_to_file(tweets, directory):
    nameOfFile = str(tweets[0].author.screen_name) + '.txt'
    writeFile = open(directory + '/' + nameOfFile, 'w')
    for t in tweets:
        writeFile.write(t.text.encode('ascii', 'ignore') + '\n')
    writeFile.close()
    return nameOfFile

#deletes all crm114 corpus files and creates fresh ones
def reset_corpus():
    subprocess.call('rm -f clinton sanders trump cruz', shell=True)

    pipe = os.popen('crm learn.crm clinton', 'w')
    pipe.close()
    
    
    pipe = os.popen('crm learn.crm sanders', 'w')
    pipe.close()

    pipe = os.popen('crm learn.crm trump', 'w')

    pipe = os.popen("crm learn.crm cruz", 'w')
    pipe.close()

def clean_workspace():
    subprocess.call('rm *.txt', shell=True)

if __name__ == '__main__':
    main()


