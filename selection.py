import json
import random
import re

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
    h = re.compile('.+.+wins.+.+for.+.+')
    winners={}
    awards={}
    output=[]
    for s in tweets:
	    t = removeRT(s['text'])
	    if h.match(t):
		    words = re.split('wins',t)
		    if words[0] in winners.keys():
		        winners[words[0]]+=1
		    else:
		        winners[words[0]]=1
		    award = re.split('for\s',words[1])
		    for phrase in award:
		    	p = phrase.lower()
		    	if re.match('^best', p):
				    if words[0] in awards.keys():
					    if p in awards[words[0]].keys():
						    awards[words[0]][p]+=1
					    else:
						    awards[words[0]][p]=1
				    else:
					    awards[words[0]] = {}
					    awards[words[0]][p]=1

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
	        	output.append({'winner': key, 'category': category})
    return output

'''g = re.compile('.+.+\sgoes\sto.+.+')
for s in tweets:
	t = removeRT(s['text'])
	if g.match(t):
		words = re.split('\sgoes\sto\s',t)
		print words'''

results = winners(tweets)
for a in results:
	print a
