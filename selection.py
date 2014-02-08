import json
import random
import re

def removeRT(tweet):
    print re.split('RT\ \@\S+:', tweet,1)[1]

with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)

for t in tweets:
	removeRT(t)

'''h = re.compile('.+.+wins.+.+for.+.+')
printed=[]
for s in tweets:
	if h.match(s['text']):
		if s['text'] not in printed:
		    printed.append(s['text'])
		    #print re.sub(r'[^\x00-\x7F]+',' ', s['text'])
		    print re.split('wins',s['text'])'''
