from tweepy import OAuthHandler
from sklearn.metrics import *
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import subprocess
import argparse
import tweepy
import random
import pickle

#authentication stuff for twitter
__consumer_key__ = 'SDSxLoUOU5eNAQEOkvvEwTFKi'
__consumer_secret__ = 'D1ikExbbdX6xZ13IDQrDnXUqTEh1VG5vxZtp7pJ1zg6Hmteent'
__access_token__ = '76215622-BmkW83GMTl1ZB9ctNgVB22TSBo9saoUMByrxp7mW0'
__access_token_secret__ = 'FeUDn5Sdn1yVxLh30Wlg9pgREvc2AQtcq5uSKKUE892EV'

__auth__ = tweepy.OAuthHandler(__consumer_key__, __consumer_secret__)
__auth__.set_access_token(__access_token__, __access_token_secret__)

__api__ = tweepy.API(__auth__)


__directory__ = '' #placeholder for directory

def main(argv):
    #Create top level parser
    parser = argparse.ArgumentParser(
            description='Machine learning classifier that learns people\'s speech patterns via their tweets.', 
            prog='PROG')
    subparsers = parser.add_subparsers(help='Use one of the following three commands:\n' \
                                            '\ttrain --help\n' \
                                            '\tclassify --help\n' \
                                            '\treset --help\n')

    #create parser for 'train' command
    parser_train = subparsers.add_parser('train', help='given twitter handles, train the classifier')
    parser_train.add_argument('screen_names', nargs='+', 
                        help = 'twitter handles for those whose tweets you want to use to train the classifier')
    parser_train.add_argument('--trainpartition', '-tp', nargs='?', default='.8', type=float,
                        help = 'portion of tweets allocated for training. rest is for testing')
    parser_train.add_argument('--algorithm', '-a',  nargs='?', type=str,  default='<osb unique microgroom>',
                        help = 'type of algorithm for crm114. e.g. \'%(default)s\'')
    parser_train.add_argument('--directory', '-d', nargs='?', type=str, default = os.path.dirname(os.path.abspath(__file__)),
                        help = 'directory that all program files should go into')
    parser_train.add_argument('--offline', action='store_true', help = 'use offline saved tweets')
    parser_train.add_argument('--resetcorpus', action='store_true', help = 'delete all trained corpuses')
    parser_train.add_argument('--resettweets', action='store_true', help = 'delete all saved offline tweets')
    parser_train.add_argument('--resetall', action='store_true', help = 'delete all trained corpuses and offline tweets')
    parser_train.add_argument('--eval', action='store_true', 
            help = 'evalute effectiveness of algorithm by separating tweets into training/test sets and printing model evaluation statistics')
    parser_train.set_defaults(func=train_command)
    
    """ UNDER CONSTRUCTION
    #create parser for reset command
    parser_reset = subparsers.add_parser('reset', help='delete corpuses, tweets, crm files')
    parser_reset.set_defaults(func = reset_command)

    #-classify - UNDER CONSTRUCTION
    #parser.add_argument('-classify', '-c', nargs=
    """
    
    #parse the args and call whichever function was selected (func=...)
    args = parser.parse_args()
    args.func(args)

def train_command(args):

    #global vars
    train_partition = args.trainpartition
    screen_names = args.screen_names #screen names for training

    #check flags for train command

    #--trainpartition, check that trainpartion is between 0 and 1
    if (not 0.0 <= train_partition <= 1.0):
        sys.exit('--trainpartition must be between 0.0 and 1.0')
    
    #--algorithm
    create_crm_files(screen_names, args.algorithm)

    #--directory
    __directory__ = args.directory

    #--offline
    all_tweets = grab_tweets(screen_names, args.offline) #grab alltweets
    print 'retrieved all tweets'

    #--resetcorpus/--resetall
    if (args.resetcorpus or args.resetall):
        subprocess.call('rm -f *.css', shell=True) #remove all corpus type files

    #--resettweets/--resetall
    if (args.resettweets or args.resetall):
        subprocess.call('rm -f *.tweets', shell=True)

    #partition tweets into training/test set
    training_tweets, test_tweets = get_training_and_test_set(train_partition, all_tweets)
    #training_tweets = [ [list of clintonTweets], [list of sandersTweets], ...]
    #test_tweets = [ [list of clintonTweets], [list of sandersTweets], ...]

    #train classifier
    for someones_tweets in training_tweets:
        screen_name = str(someones_tweets[0].author.screen_name)
        train(screen_name, someones_tweets)
    print 'trained classifier.'

    
    #Testing (UNDER CONSTRUCTION)
    print 'evaluating algorithm...'
    y_true = []
    y_pred = []
    for tweets in test_tweets:
        for t in tweets:
            trueAuthor = t.author.screen_name
            matchList, probList = classify(write_tweets_to_file([t], __directory__, trueAuthor + '.txt'))

            #TO-DO: SOMEHOW EVALUTE PROBLIST
            print probList

            y_true.append(trueAuthor)
            y_pred.append(matchList[0])
    #Compute Accuracy Score
    print 'Accuracy score (normalized):', accuracy_score(y_true, y_pred)
    #Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=screen_names)
    print cm
    plt.figure()
    plot_confusion_matrix(cm, screen_names)
    plt.show()
    #Classification report
    print(classification_report(y_true, y_pred, target_names=screen_names))


    #classify and split probabilities into list
    #bestMatch, probList = classify('speeches/clinton_NYVictorySpeech_apr202016.txt') #retrieve string output
    clean_workspace()

def crm_files_exist(screen_names):
    #check if files exit already
    allFilesExist = True
    for name in screen_names:
        complete_directory = os.path.join(__directory__, name + '.css')
        if(os.path.isfile(complete_directory) is False):
            allFilesExist = False
            break
    return allFilesExist


def create_crm_files(screen_names, classification_type):
    CLASSIFY_EXT = '.css'    #create files if they don't exist
    LEARN_CMD = "{ learn %s (:*:_arg2:) }"
    CLASSIFY_CMD = "{ isolate (:stats:);" \
            " classify %s ( %s ) (:stats:);" \
            " match [:stats:] (:: :best: :prob:)" \
            " /Best match to file #. \\(([[:graph:]]+)\\) prob: ([0-9\\.]+) /;" \
            " %s " \
            " match [:best:] (:: :best_match:) /([[:graph:]]+).css/;" \
            " output /:*:best_match: :*:prob: \\n %s\\n / }" # %output_list
    MATCH_VAR = 'match [:stats:] (:: :%s_prob:)' \
                ' /\\(%s\\): features: [[:graph:]]+ hits: [[:graph:]]+ prob: ([[:graph:]]+),/;'
    #create learn.crm
    learnCRM = open(os.path.join(__directory__,'learn.crm'), 'w')
    learnCRM.write(LEARN_CMD % classification_type)
    learnCRM.close()

    #create classify.crm
    classifyCRM = open('classify.crm', 'w')
    name_list = [names + CLASSIFY_EXT for names in screen_names]
    match_list = [MATCH_VAR % (names, names) for names in name_list] #create list of MATCH_VARs based on screen name
    output_list = ['%s: :*:%s_prob:' % (names.split('.')[0], names) for names in name_list] #create list for output

    classifyCRM.write(CLASSIFY_CMD % (classification_type,
                                      ' '.join(name_list),
                                      ' '.join(match_list),
                                      ' '.join(output_list)
                                     ))
    classifyCRM.close()

    CRM_BINARY = 'crm'
    CLASSIFICATION_EXT = '.css'

    #create corpus files
    for n in screen_names:
        pipe = os.popen(('crm '+ os.path.join(__directory__) + 'learn.crm ' +  str(n + CLASSIFICATION_EXT)), 'w')
        pipe.close()

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
    trainingTxtFile = write_tweets_to_file(tweets,__directory__, screen_name + '.txt')
    subprocess.call('crm ' + os.path.join(__directory__, 'learn.crm') + 
            ' ' + (screen_name+'.css') + ' < '+ trainingTxtFile, shell=True)

# classifies textfile and returns best match and probabilities
# bestMatch = tuple(bestMatch bestProb)
# probList = [ (twitterHandle1, probability1) (twitterHandle2, probability2) ...]
def classify(textFileName):
    output =  subprocess.check_output('crm ' + os.path.join(__directory__, 'classify.crm') + ' < ' + textFileName, shell=True) #string output from crm114
    outList = output.split()
    bestMatch = (str(outList[0]), float(outList[1])) #(best_candidate, probability)
    outList = outList[2:]

    probList = []
    it = iter(outList)
    for x in it:
        probList.append((x, float(next(it))))

    return (bestMatch, tuple(probList))


def clean_workspace():
    subprocess.call('rm -f *.txt', shell=True)


"""TWITTER RELATED FUNCTIONS"""


#grabs all tweets in list of screen_names and returns one list with lists of tweets
def grab_tweets(screen_names, use_offline = True):
    LOCAL_FILE_EXT = '.tweets'

    all_tweets = []


    for name in screen_names:
        complete_directory = os.path.join(__directory__, name + LOCAL_FILE_EXT)
        if(use_offline and os.path.isfile(complete_directory)):
            tweetFile = open(name+LOCAL_FILE_EXT, 'rb')

            print 'loading %s\'s tweets from file...' % name
            tweets = pickle.load(tweetFile)
            tweetFile.close()

            all_tweets.append(tweets) #add that person's tweetlist to big list
        else:
            print 'retrieving %s\'s tweets from twitter' % name
            tweets = get_all_tweets(name, False)

            tf = open(complete_directory, 'wb')

            print 'saving %s\'s tweets to file...' % name
            pickle.dump(tweets, tf)
            tf.close()

            all_tweets.append(tweets) #add person's tweetlist to biglist
    return all_tweets

#source: gist.github.com/yanofsky/5436496
def get_all_tweets(screen_name, include_retweets = True):
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
    #parse out t.co links - TO-DO
    #alltweets = [for t in alltweets t.text.find('https://t.co')

    if (include_retweets is False): #filter out retweets
        print 'parsing out retweets...'
        alltweets = [t for t in alltweets if (t.text.startswith('RT') is False) 
                    and t.text.startswith('"') is False] 
    return alltweets

#saves tweets to text file under firstnamelastname.txt by default
#returns filename (string)
#note: make sure tweets isn't empty or else errors
def write_tweets_to_file(tweets, directory, nameoffile = 'lmao.txt'):
    writefile = open(os.path.join(directory,  nameoffile), 'w')
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

def plot_confusion_matrix(cm, labels, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


if __name__ == '__main__':
    main(sys.argv[1:])


