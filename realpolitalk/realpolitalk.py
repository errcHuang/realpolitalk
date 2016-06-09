import os
import sys
import subprocess
import argparse
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

__current_dir__ = os.path.dirname(os.path.abspath(__file__))

__directory__ = -1

def main(argv):
    #command line parsing
    parser = argparse.ArgumentParser(description='Train ML classifier from tweets.')
    parser.add_argument('screen_names', nargs='+',
                        help = 'a list of twitter screen names. e.g. HillaryClinton realDonaldTrump')
    parser.add_argument('--trainpartition', '-t', nargs='?', default='.8', type=float, 
                        help = 'portion of tweets allocated for training. rest is for testing')
    parser.add_argument('--algorithm', '-a',  nargs='?', type=str,  default='<osb unique microgroom>',
                        help = 'type of algorithm for crm114. e.g. \'%(default)s\'')
    parser.add_argument('--directory', '-d', nargs='?', type=str, default = __current_dir__,
                        help = 'directory that all program files should go into')
    args = parser.parse_args()

    #global vars
    train_partition = args.trainpartition
    screen_names = args.screen_names
    __directory__ = args.directory
    
    #check that trainpartion is between 0 and 1
    if (not 0.0 <= train_partition <= 1.0):
        sys.exit('--trainpartition must be between 0.0 and 1.0')

    reset_corpus()
    create_crm_files(args.screen_names, args.algorithm)

    #grab all tweets
    all_tweets = grab_tweets(screen_names)
    print 'retrieved all tweets'
    

    """
    #randomly partition tweets into 10 subsamples
    clinton_subsamples = random_partition(clintonTweets, 10)
    sanders_subsamples = random_partition(sandersTweets, 10)
    trump_subsamples = random_partition(trumpTweets, 10)
    cruz_subsamples = random_partition(cruzTweets, 10)


    #future cross validation steps would be to train on some subsamples, test on others 
    """

    #partition tweets into training/test set
    training_tweets, test_tweets = get_training_and_test_set(train_partition,
            all_tweets)
    #training_tweets = [ [list of clintonTweets], [list of sandersTweets], ...]
    #test_tweets = [ [list of clintonTweets], [list of sandersTweets], ...] 
    
    #train classifier
    for tweets in training_tweets:
        screen_name = str(tweets[0].author.screen_name)
        train(screen_name, tweets)
    print 'trained classifier.'
    
    """
    #get older clinton tweets and classify
    oldClinton = grab_tweets('HillaryClinton', 10, clintonTweets[-1].id)

    probList = classify(write_tweets_to_file(oldClinton, currentDir)).split()
    """
    """#under construction
    for candidateTweets in test_tweets:
        for tweets in candidateTweets:
            for tweet in tweets:
                trueAuthor = tweet.author.screen_name
                bestMatchList, listOfProbList = classify(write_tweets_to_file(tweet, currentDir))
    """
    #classify and split probabilities into list
    bestMatch, probList = classify('speeches/clinton_NYVictorySpeech_apr202016.txt') #retrieve string output

    print bestMatch
    print "hillary %:", probList[0]
    print "bernie %:", probList[1]
    print "donald %:", probList[2]
    print "ted %:", probList[3]



    clean_workspace()
def create_crm_files(screen_names, classification_type):
    MATCH_VAR = 'match [:stats:] (:: :*:%s_prob:)' \
                ' /\\(%s\\): features: [[:graph:]]+ hits: [[:graph:]]+ prob: ([[:graph:]]+),/;'

    LEARN_CMD = "{ learn %s (:*:_arg2:) }"
    CLASSIFY_CMD = "{ isolate (:stats:);" \
            " classify %s ( %s ) (:stats:);" \
            " match [:stats:] (:: :best: :prob:)" \
            " /Best match to file #. \\(([[:graph:]]+)\\) prob: ([0-9\\.]+) /;" \
            " %s " \
            " output /:*:best: :*:prob: %s / }" # %output_list
    
    #create learn.crm
    learnCRM = open(os.path.join(__directory__,'learn.crm'), 'w')
    learnCRM.write(LEARN_CMD % classification_type)
    learnCRM.close()

    #create classify.crm
    classifyCRM = open('classify.crm', 'w')
    match_list = [MATCH_VAR % (names, names) for names in screen_names] #create list of MATCH_VARs based on screen name 
    output_list = [':*:%s_prob:' % names for names in screen_names] #create list for output

    classifyCRM.write(CLASSIFY_CMD % (classification_type,
                                      ' '.join(screen_names),
                                      ' '.join(match_list), 
                                      ' '.join(output_list)
                                     ))
    classifyCRM.close()

    CRM_BINARY = 'crm'
    CLASSIFICATION_EXT = '.css'

    #create corpus files
    for n in screen_names:
        subprocess.call('crm learn.crm ' + n + CLASSIFICATION_EXT)
                                      
#slices a list into n nearly-equal-length partitions
#returns list of lists
def random_partition(lst, n):
    random.shuffle(lst)
    division = len(lst) / float(n)
    return [ lst[int(round(division * i)): int(round(division * (i+1)))] for i in xrange(n) ]

#Randomly resamples labeled datasets into comprehensive training set and test set
#reshuffles data and returns training/test sets at 
#the list 'dataset' should have lists that represent classes
def get_training_and_test_set(trainProportion, dataset):
    training_data = []
    test_data = []
    for data in dataset:
        random.shuffle(data)
        trainIndex = trainProportion * len(data) #calculates index for end of training set
        trainIndex = int(round(trainIndex))
        training_data.append(data[:trainIndex]) #partitions training set from start to random index
        test_data.append(data[trainIndex:]) #partition test set from random index to end
    return (training_data, test_data) 

#note tweets must not be empty
def train(screen_name, tweets):
    trainingTxtFile = write_tweets_to_file(tweets,__directory__)
    subprocess.call('crm learn.crm ' + screen_name + '.css' +' < ' + trainingTxtFile, shell=True)

# classifies textfile and returns best match and probabilities 
# bestMatch = tuple(bestMatch bestProb) 
# probList = tuple(hillaryProb bernieProb donaldProb tedProb)
def classify(textFileName):
    output =  subprocess.check_output('crm classify.crm < ' + textFileName, shell=True) #string output from crm114
    probList = output.split() 
    bestMatch = (str(probList[0]), float(probList[1])) #(best_candidate, probability)
    probList = probList[2:]
    probList = [float(i) for i in probList] #convert probList into floats
    return (bestMatch, tuple(probList))

#deletes all crm114 corpus files and creates fresh ones
def reset_corpus():
    subprocess.call('rm -f *.css', shell=True) #remove all corpus type files


def clean_workspace():
    subprocess.call('rm -f *.txt', shell=True)


"""TWITTER RELATED FUNCTIONS"""

""" DEPRECATED
def grab_tweets_from(screenName, numTweets, fromID):
    return __api__.user_timeline(screen_name = screenName, count = numTweets, max_id = fromID)
"""

#grabs all tweets in list of screen_names and returns one list with lists of tweets
def grab_tweets(screen_names, save_offline = True):
    LOCAL_FILE_EXT = '.tweets'

    all_tweets = []


    for name in screen_names:
        complete_directory = os.path.join(__directory__, name + LOCAL_FILE_EXT)
        if(os.path.isfile(complete_directory)):
            tweetFile = open(name+LOCAL_FILE_EXT, 'rb')

            print 'loading %s\'s tweets from file...' % name
            tweets = pickle.load(tweetFile)
            tweetFile.close()

            all_tweets.extend(tweets) #add that person's tweetlist to big list
        else:
            print 'retrieving %s\'s tweets from twitter' % name
            tweets = get_all_tweets(name)

            if (save_offline):
                tf = open(complete_directory, 'wb')

                print 'saving %s\'s tweets to file...' % name
                pickle.dump(tweets, tf)
                tf.close()
            
            all_tweets.extend(tweets) #add person's tweetlist to biglist
    return all_tweets

#source: gist.github.com/yanofsky/5436496
def get_all_tweets(screen_name):
    #initialize a list to hold all the tweepy tweets
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
    
#saves tweets to text file under firstnamelastname.txt by default
#returns filename (string)
#note: make sure tweets isn't empty or else errors
def write_tweets_to_file(tweets, directory):
    nameoffile = str(tweets[0].author.screen_name) + '.txt'
    writefile = open(directory + '/' + nameoffile, 'w')
    for t in tweets:
        writefile.write(t.text.encode('ascii', 'ignore') + '\n')
    writefile.close()
    return nameoffile


def frange(*args):
    """A float range generator."""
    start = 0.0
    step = 1.0

    l = len(args)
    if l == 1:
        end = args[0]
    elif l == 2:
        start, end = args
    elif l == 3:
        start, end, step = args
        if step == 0.0:
            raise ValueError, "step must not be zero"
    else:
        raise TypeError, "frange expects 1-3 arguments, got %d" % l

    v = start
    while True:
        if (step > 0 and v >= end) or (step < 0 and v <= end):
            raise StopIteration
        yield v
        v += step

if __name__ == '__main__':
    main(sys.argv[1:])


