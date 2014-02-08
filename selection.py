import json
import random
import re

def removeRT(tweet):
    t = re.split('RT\s\@\S+\:\s', tweet,1)
    if len(t)>1:
    	return t[1]
    else:
    	return t[0]

with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)

for t in tweets:
	removeRT(t['text'])

h = re.compile('.+.+wins.+.+for.+.+')
printed=[]
winners={}
for s in tweets:
	t = removeRT(s['text'])
	if h.match(t):
		#if t not in printed:
		    #printed.append(t)
		    #print re.sub(r'[^\x00-\x7F]+',' ', s['text'])
		    words = re.split('wins',t)
		    if words[0] in winners.keys():
		        winners[words[0]]+=1
		    else:
		    	winners[words[0]]=1

for key in winners:
	if winners[key] > 10:
	    print key+': '+str(winners[key])
