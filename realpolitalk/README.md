# realpolitalk: a machine learning approach to understanding twitter
This project takes tweets from any number of twitter handles and uses it to 

##Requirements with installation instructions:
Python 2.7
CRM-114
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

Other requirements (tweepy, numpy, scikit-learn, matplotlib, etc.) can be installed with this command.
`pip install -r requirements.txt`

##How to run:

##Misc.
Realpolitalk was originally designed to only analyze the tweets of politicians, which is why [reference in the name](https://en.wikipedia.org/wiki/Realpolitik) is oriented around politics.
