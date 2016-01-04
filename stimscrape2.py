import pandas as pd
import numpy as np
import praw
import datetime
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import string
import urllib
import time
import re

english_stops = stopwords.words('english')
lmtzr = WordNetLemmatizer()
shortword = re.compile(r'\W*\b\w{1,2}\b')
nonan = re.compile(r'[^a-zA-Z ]')
html = re.compile(r'\<[^\>]*\>')
tag_to_type = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'R': wordnet.ADV}
def get_wordnet_pos(treebank_tag):
    return tag_to_type.get(treebank_tag[:1], wordnet.NOUN)
    
def clean(text):
    clean_text = nonan.sub('',html.sub('',text))
    words = nltk.word_tokenize(shortword.sub('',clean_text.lower()))
    filtered_words = [w for w in words if not w in english_stops]
    tags = nltk.pos_tag(filtered_words)
    return ' '.join(
        lmtzr.lemmatize(word, get_wordnet_pos(tag[1]))
        for word, tag in zip(filtered_words, tags)
    )
    
def internet_on():
    try :
        stri = "https://www.google.com"
        tempdata = urllib.urlopen(stri)
        return True
    except :
        print "not connected"
        time.sleep(10) 
        return False
        
def tokenize_comment(comment): #converts comment into non-stopword, non-punctuation space-delimited string
    comment = clean(comment) #lemmatizes
    tokens=nltk.wordpunct_tokenize(comment) #makes individual words from comments
    tokens=[token.lower() for token in tokens if token.lower() not in english_stops] #removes stopwords
    tokens = [token for token in tokens if token not in string.punctuation] #removes punctuation
    #print sorted(tokens)[0:20] #check to see if tokens are meaningful
    tokenstring='' #initialize empty string
    for x in tokens:
        tokenstring=tokenstring+x+' ' #make big space-limited token string
    return tokenstring


def collect_comments(subreddit_string, count, startdate, enddate, freqspec):

    #usage: collect_comments('opiates',None,'11/14/2010','11/16/2015','D')
    #subreddit_string is name of subreddit, e.g. 'opiates'
    #count is number of submissions to retrieve per frequency interval (as defined by freqspec). Can be set to None, which means all comments will be collected
    #startdate is how far back in time you want to retrieve comments, e.g., '11/14/2015'
    #freqspec is the frequency interval used for searching; we will loop at this interval from current date all the way back to start date. E.g., 'D' for day.

    r = praw.Reddit('Stimscrape 1.0 by stimscraper')
    r.login('stimscraper', 'stimscraperpassword',disable_warning='True')
    subreddit = r.get_subreddit(subreddit_string)

    date_range = list(pd.date_range(start=startdate, end=enddate, freq=freqspec)) #[::-1] #populates date range with specified frequency

    comment_dict={'authors':[],'comments':[],'links':[],'commenttimes':[]} #where our comments will be stored

    for lower_timestamp, upper_timestamp in zip(date_range,date_range[1:]):
        print 'Starting new reddit search query for: ', lower_timestamp
        # Convert timestamps from pd.Timestamp to epoch, offset by 1 second to avoid overlap
        lower_timestamp_epoch = int(lower_timestamp.value / 1e9)
        upper_timestamp_epoch = int((upper_timestamp.value / 1e9) - 1)

        # Create query for timeframe
        query = 'timestamp:%d..%d' % (lower_timestamp_epoch, upper_timestamp_epoch)
        while True:
            if internet_on():
                break
        submissions = r.search(query, subreddit=subreddit_string, sort='new', limit=count, syntax='cloudsearch')
    
         # Loop through the submissions
        for submission in submissions:
            print '.', 
            #try:
            while True:
                if internet_on():
                    break
            submission.replace_more_comments(limit=None, threshold=1) #this may take a while...
            while True:
                if internet_on():
                    break
            flat_comments = praw.helpers.flatten_tree(submission.comments) #this gives us more than just the top comment
            for x in flat_comments:
                #print '.',
                x=vars(x)
                #print x
                author=str(x['author'])
                body=str(x['body'].encode('utf8'))
                link=str(x['link_id'].encode('utf8'))
                commenttime=float(x['created'])
                comment_dict['authors'].append(author)
                comment_dict['comments'].append(tokenize_comment(body))
                comment_dict['links'].append(link)
                comment_dict['commenttimes'].append(commenttime)
                
            df = pd.DataFrame.from_dict(comment_dict)
            df.to_csv('opiates_comments.csv')
            #except Exception:
            #    print 'error'
    return comment_dict

comment_dict=collect_comments('opiates',None,'11/01/2014','11/16/2015','M')
