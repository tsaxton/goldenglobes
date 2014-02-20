import json
import re
import selection
import random

with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)
cleanTweets = []
for t in tweets:
	cleanTweets.append(selection.removeRT(t['text']))

'''wearing = re.compile('.+.+wearing.+.+')
for t in cleanTweets:
	if wearing.match(t):
		print t'''

'''selection = random.sample(cleanTweets,10)
for s in selection:
	print s'''

hashtags = {}
for t in cleanTweets:
	st = t.lower().encode('utf-8').split(' ')
	for s in st:
		if len(s) < 1:
			continue
		if s[0] == '#':
			subs = s[1:]
			if subs in hashtags.keys():
				hashtags[subs] += 1
			else:
				hashtags[subs] = 1
for h in hashtags:
	if hashtags[h] > 15:
		print h + ', ' + str(hashtags[h])

