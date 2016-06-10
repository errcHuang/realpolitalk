# realpolitalk: a machine learning approach to understanding tweets
realpolitalk takes tweets from Twitter users and machine learns them. 

The vision behind the project is to be able to take someone's tweets, learn what makes their tweets unique to them, and be able to identify (proper term would be classify) their speech patterns in any medium, whether an essay, book, speech, etc.

##Requirements with installation instructions:
- Python 2.7 
- CRM-114 (installation instructions below)
###Debian/Ubuntu
`sudo apt-get install crm114`
###Red Hat/Fedora
`sudo dnf install crm114`
###Everyone Else
`## If you do not yet have libtre and its headers:
curl -O http://crm114.sourceforge.net/tarballs/tre-0.7.5.tar.gz
tar -zxf tre-*.tar.gz
cd tre-*
./configure --enable-static
make
sudo make install
cd ..

curl -O http://crm114.sourceforge.net/tarballs/crm114-20100106-BlameMichelson.src.tar.gz
tar -zxf crm114-*.tar.gz
cd crm114*.src
make
sudo make install
cd ..`
- Twitter API access (consumer key, consumer secret, access tokens)
[excellent tutorial here on accessing Twitter API](http://pythoncentral.io/introduction-to-tweepy-twitter-for-python/)
- Other requirements (tweepy, numpy, scikit-learn, matplotlib, etc.) can be installed with this command.
`pip install -r requirements.txt`

##Usage:
The basic usage pipeline for realpolitalk is to _train_ then _classify_ (and _reset_) as needed.
`python realpolitalk.py {train, classify, reset}`
###Training
The most basic usage is to enter the 'train' command and then enter any number of screen names that you want to train the algorithm on.
`python realpolitalk.py train HillaryClinton realDonaldTrump BernieSanders PRyan`
###Classifying 
After training realpolitalk on tweets, you can enter the 'classify' command and enter any number of textfiles you want classified. 

The result is a best match (whose speech pattern the textfile most resembles) and the distribution of probabilities for the other choices.
`python realpolitalk.py classify clinton_NYVictorySpeech_apr202016.txt trump_iowafreedomsummit_jan242016.txt.txt ...`
####Example output (of the above command)a
`best match: HillaryClinton
probabilities:
	HillaryClinton:: 1.0
	realDonaldTrump:: 5.81e-31
	BernieSanders:: 1.44e-22
	PRyan:: 1.64e-56

best match: realDonaldTrump
probabilities:
	HillaryClinton:: 1.47e-36
	realDonaldTrump:: 1.0
	BernieSanders:: 2.94e-12
	PRyan:: 1.7e-86`
###Reseting
If you want to start fresh, maybe train with different users, you can use the 'reset' command to delete all your trained corpuses (the already trained algorithm in .css file format) and tweets.
`python realpolitalk.py reset --all`

##Advanced Usage
###Training options


##Misc.
###CRM114
[CRM114](crm114.sourceforge.net) is basically a programming language/engine that is centered entirely around parsing and learning/classifying text streams. 

Originally used for spam classification, CRM114 is super fast (written in C) and wildly accurate (>99.9%). You can basically plug-and-play with different algorithms (Hidden Markov Model, OSB, winnow, bit entropy, etc.) with relative ease.


###Origin of name
Realpolitalk was originally designed to only analyze the tweets of politicians hence the [reference in the name](https://en.wikipedia.org/wiki/Realpolitik).
