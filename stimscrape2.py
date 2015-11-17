import pandas as pd
import numpy as np
import praw
import datetime
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string


english_stops = stopwords.words('english')

def tokenize_comment(comment): #converts comment into non-stopword, non-punctuation space-delimited string
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

    date_range = list(pd.date_range(start=startdate, end=enddate, freq=freqspec)) #populates date range with specified frequency

    comment_dict={'authors':[],'comments':[],'links':[],'dates':[]} #where our comments will be stored

    for lower_timestamp, upper_timestamp in zip(date_range, date_range[1:]):
        print 'Starting new reddit search query for: ', lower_timestamp
        # Convert timestamps from pd.Timestamp to epoch, offset by 1 second to avoid overlap
        lower_timestamp_epoch = int(lower_timestamp.value / 1e9)
        upper_timestamp_epoch = int((upper_timestamp.value / 1e9) - 1)

        # Create query for timeframe
        query = 'timestamp:%d..%d' % (lower_timestamp_epoch, upper_timestamp_epoch)
        submissions = r.search(query, subreddit=subreddit_string, sort='new', limit=count, syntax='cloudsearch')
    
         # Loop through the submissions
        for submission in submissions:
            print 'Starting on new submission' 
            try:
                submission.replace_more_comments(limit=None, threshold=1) #this may take a while...

                flat_comments = praw.helpers.flatten_tree(submission.comments) #this gives us more than just the top comment
                for x in flat_comments:
                    print '.',
                    x=vars(x)
                    #print x
                    author=str(x['author'])
                    body=str(x['body'].encode('utf8'))
                    link=str(x['link_id'].encode('utf8'))
                    comment_dict['authors'].append(author)
                    comment_dict['comments'].append(tokenize_comment(body))
                    comment_dict['links'].append(link)
    
                df = pd.DataFrame.from_dict(comment_dict)
                df.to_csv('opiates_comments.csv')
            except Exception:
                print 'error'
    return comment_dict

comment_dict=collect_comments('opiates',None,'11/16/2010','11/16/2015','M')
