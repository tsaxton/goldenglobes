import json
import random
import re
from titlecase import titlecase

def removeRT(tweet):
    ''' Removes the RT @handle: rom the tweet.
        Input: string (Tweet)
        Output: string (Tweet without RT)'''
    t = re.split('RT\s\@\S+\:\s', tweet,1)
    if len(t)>1:
        return t[1]
    else:
        return t[0]

with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)

for t in tweets:
    removeRT(t['text'])

def winners(tweets):
    g = re.compile('.+.+\sgoes\sto.+.+')
    h = re.compile('.+.+wins.+.+for.+.+')
    winners={}
    awards={}
    output=[]
    for s in tweets:
        t = removeRT(s['text'])
        if h.match(t):
            words = re.split('wins',t)
            person = words[0].lstrip().rstrip()
            person = re.split('\.', person)[0] # ignore punctuation
            person = re.split('\!', person)[0]
            if '"' in person:
            	person = re.split('"', person)[1]
            if person=='' or person[0]=='#':
            	continue
            if person in winners.keys():
                winners[person]+=1
            else:
                winners[person]=1
            award = re.split('for\s',words[1])
            for phrase in award:
                p = phrase.lower().lstrip().rstrip()
                if re.match('^best', p):
                    if person in awards.keys():
                        if p in awards[person].keys():
                            awards[person][p]+=1
                        else:
                            awards[person][p]=1
                    else:
                        awards[person] = {}
                        awards[person][p]=1
        elif g.match(t):
            words = re.split('\sgoes\sto',t)
            if re.match('^best',words[0].lower().lstrip()):
                category = words[0].lower().lstrip().rstrip()
                who = re.split('\sfor\s',words[1])
                person = who[0].lstrip()
                person = re.split('\s#', person)[0]
                if '"' in person:
                	person = re.split('"', person)[1]
                person = re.split('\.', person)[0]
                person = re.split('\!', person)[0]
                what = ''
                if len(who) > 1:
                	what = who[1].lstrip().rstrip()
                	what = re.split('http', what)[0]
                	what = re.split('#', what)[0]
                	if '"' in what:
                		what = re.split('"', what)[1]
                	what = re.split('\.', what)[0]
                if person in winners.keys():
                	winners[person]+=1
                else:
                	winners[person]=1
                if person in awards.keys():
                	if category in awards[person].keys():
                		awards[person][category]+=1
                	else:
                		awards[person][category]=1
                else:
                	awards[person] = {}
                	awards[person][category]=1


    for key in winners:
        category = ''
        if winners[key] > 10:
            #print key+': '+str(winners[key])
            if key in awards:
                m = max(awards[key].values())
                for a in awards[key]:
                    if awards[key][a] == m:
                        #print a+': '+str(awards[key][a])
                        category = a
                        break # prevents from case of a tie but similar wording
            category = category.split('. ', 1)[0] #removes trailing links. award names do not take two sentences.
            if '."' in category:#if clause handles award names ending with quotes ex. "django unchained." 
                category = category.split('."',1)[0]
                category += str('."')
            category = category.split('#',1)[0] #removes any hashtags remaining
            if category != '':
                output.append({'winner': key, 'category': titlecase(category)})
    return output

'''g = re.compile('.+.+\sgoes\sto.+.+')
for s in tweets:
    t = removeRT(s['text'])
    if g.match(t):
        words = re.split('\sgoes\sto',t)
        if re.match('^best',words[0].lower().lstrip()):
            category = words[0].lower().lstrip()
            who = re.split('\sfor\s',words[1])
            # who[0] contains winner
            # who[1] contains role/movie, plus other crap
            person = who[0].lstrip()
            person = re.split('\s#',person)[0]
            if '"' in person:
                person = re.split('"',person)[1]
            what = ''
            if len(who) > 1:
                what = who[1].lstrip()
                what = re.split('http',what)[0]
                what = re.split('#', what)[0]
                if '"' in what:
                    what = re.split('"', what)[1]
                what = re.split('\.', what)[0]'''

results = winners(tweets)
for a in results:
    print a
