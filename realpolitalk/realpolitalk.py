import os
import sys
import subprocess
import tweepy
import random
import pickle
from tweepy import OAuthHandler

#authentication stuff for twitter
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
    
    """
    #grab initial 200 tweets for training
    trumpTweets = __api__.user_timeline('realDonaldTrump', count = 200)
    cruzTweets = __api__.user_timeline('SenTedCruz', count = 200)

    clintonTweets = __api__.user_timeline('HillaryClinton', count = 200)
    sandersTweets = __api__.user_timeline('SenSanders', count = 200)
    print 'retrieved tweets'
    """
    
    #grab all tweets
    clintonTweets = []
    sandersTweets = []
    trumpTweets = []
    cruzTweets = []


    #if tweets exist in offline binary files
    if(os.path.isfile('trump.tweets') and 
       os.path.isfile('cruz.tweets') and
       os.path.isfile('clinton.tweets') and
       os.path.isfile('sanders.tweets')):
        tt = open('trump.tweets', 'rb')
        ct = open('cruz.tweets', 'rb')
        ht = open('clinton.tweets', 'rb')
        st = open('sanders.tweets', 'rb')

        print 'loading tweets from file...'
        trumpTweets = pickle.load(tt)
        cruzTweets = pickle.load(ct)
        clintonTweets = pickle.load(ht)
        sandersTweets = pickle.load(st)
        print 'loaded all tweets.'

        tt.close()
        ct.close()
        ht.close()
        st.close()
    else:  #retrieve tweets from online
        print 'retrieving tweets from twitter...'
        trumpTweets = get_all_tweets('realDonaldTrump')
        cruzTweets = get_all_tweets('SenTedCruz')
        clintonTweets = get_all_tweets('HillaryClinton')
        sandersTweets = get_all_tweets('SenSanders')

        #open files
        tt = open('trump.tweets', 'wb')
        ct = open('cruz.tweets', 'wb')
        ht = open('clinton.tweets', 'wb')
        st = open('sanders.tweets', 'wb')
       
        print 'saving tweets...'
        #save tweets in binary file
        pickle.dump(trumpTweets, tt)
        pickle.dump(cruzTweets, ct)
        pickle.dump(clintonTweets, ht)
        pickle.dump(sandersTweets, st)
        print 'saved tweets to file.'

        #close all files
        tt.close()
        ct.close()
        ht.close()
        st.close()
    

    """
    #randomly partition tweets into 10 subsamples
    clinton_subsamples = random_partition(clintonTweets, 10)
    sanders_subsamples = random_partition(sandersTweets, 10)
    trump_subsamples = random_partition(trumpTweets, 10)
    cruz_subsamples = random_partition(cruzTweets, 10)


    #future cross validation steps would be to train on some subsamples, test on others 
    """

    #partition tweets into training/test set
    training_tweets, test_tweets = get_random_training_and_test_set(
            clintonTweets, sandersTweets, trumpTweets, cruzTweets)
    #training_tweets = [ [list of clintonTweets], [list of sandersTweets], ...]
    
    #train classifier
    train_classifier('clinton', write_tweets_to_file(training_tweets[0], currentDir))
    train_classifier('sanders', write_tweets_to_file(training_tweets[1], currentDir))
    train_classifier('trump', write_tweets_to_file(training_tweets[2], currentDir))
    train_classifier('cruz', write_tweets_to_file(training_tweets[3], currentDir))
    print 'trained classifier.'
    
    """
    #get older clinton tweets and classify
    oldClinton = grab_tweets('HillaryClinton', 10, clintonTweets[-1].id)

    #classify and split probabilities into list
    probList = classify(write_tweets_to_file(oldClinton, currentDir)).split()
    """
    probList = classify('speeches/clinton_NYVictorySpeech_apr202016.txt') #retrieve string output
    probList = probList.split() 
    bestMatch = (str(probList[0]), float(probList[1])) #(best_candidate, probability)
    probList = probList[2:]
    probList = [float(i) for i in probList] #convert probList into floats

    print bestMatch
    print "hillary %:", probList[0]
    print "bernie %:", probList[1]
    print "donald %:", probList[2]
    print "ted %:", probList[3]

    clean_workspace()

#slices a list into n nearly-equal-length partitions
#returns list of lists
def random_partition(lst, n):
    random.shuffle(lst)
    division = len(lst) / float(n)
    return [ lst[int(round(division * i)): int(round(division * (i+1)))] for i in xrange(n) ]

#Randomly resamples labeled datasets into comprehensive training set and test set
#reshuffles data and returns training/test sets at random proportions
#each argument in *dataset should represent 1 "class" of a dataset
#function reconstructs 
def get_random_training_and_test_set(*dataset):
    training_data = []
    test_data = []
    for data in dataset:
        random.shuffle(data)
        randIndex = random.choice(range(len(data))) #calculates random index in dataset
        training_data.append(data[:randIndex]) #partitions training set from start to random index
        test_data.append(data[randIndex:]) #partition test set from random index to end
    return (training_data, test_data) 

def train_classifier(candidate, trainingTxtFile):
    subprocess.call('crm learn.crm ' + candidate + ' < ' + trainingTxtFile, shell=True)

# returns string that contains probabilities 
# (bestMatch bestProb hillaryProb bernieProb donaldProb tedProb)
def classify(textFileName):
    return subprocess.check_output('crm classify.crm < ' + textFileName, shell=True)

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


"""TWITTER RELATED FUNCTIONS"""

def grab_tweets(screenName, numTweets, fromID):
    return __api__.user_timeline(screen_name = screenName, count = numTweets, max_id = fromID)

#Source: gist.github.com/yanofsky/5436496
def get_all_tweets(screen_name):
    #initialize a list to hold all the tweepy Tweets
    alltweets = []	
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = __api__.user_timeline(screen_name = screen_name,count=200)
    
    #save most recent tweets
    alltweets.extend(new_tweets)
    
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
            print "getting tweets before %s" % (oldest)
            
            #all subsiquent requests use the max_id param to prevent duplicates
            new_tweets =__api__.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
            
            #save most recent tweets
            alltweets.extend(new_tweets)
            
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
            
            print "...%s tweets downloaded so far" % (len(alltweets))
    return alltweets
    
#saves tweets to text file under FirstnameLastname.txt by default
#returns filename (string)
#Note: make sure tweets isn't empty or else errors
def write_tweets_to_file(tweets, directory):
    nameOfFile = str(tweets[0].author.screen_name) + '.txt'
    writeFile = open(directory + '/' + nameOfFile, 'w')
    for t in tweets:
        writeFile.write(t.text.encode('ascii', 'ignore') + '\n')
    writeFile.close()
    return nameOfFile

if __name__ == '__main__':
    main()


