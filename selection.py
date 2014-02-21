import json
import random
import re
from titlecase import titlecase
from tfidf import *
import numpy
import sys
from alchemyapi import *
from operator import itemgetter
import pprint

def removeRT(tweet):
    ''' Removes the RT @handle: rom the tweet.
        Input: string (Tweet)
        Output: string (Tweet without RT)'''
    t = re.split('RT\s\@\S+\:\s', tweet,1)
    if len(t)>1:
        return removeRT(t[len(t)-1]) # this recursiveness is necessary to remove the case of multiple RTs
    else:
        return t[0]

def winners(tweets):
    g = re.compile('.+.+\sgoes\sto.+.+')
    h = re.compile('.+.+wins.+.+for.+.+')
    winners={}
    awards={}
    output=[]
    i = 0
    for t in tweets:
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
                            awards[person][p].append(i)
                        else:
                            awards[person][p] = [i]
                    else:
                        awards[person] = {}
                        awards[person][p]=[i]
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
                        awards[person][category].append(i)
                    else:
                        awards[person][category] = [i]
                else:
                    awards[person] = {}
                    awards[person][category]=[i]
        i += 1


    for key in winners:
        category = ''
        if winners[key] > 10:
            #print key+': '+str(winners[key])
            if key in awards:
                maxLen = 0
                for a in awards[key]:
                    l = len(awards[key][a])
                    if l > maxLen:
                        maxLen = l
                        category = a
                        categoryKey = a
            category = category.split('. ', 1)[0] #removes trailing links. award names do not take two sentences.
            if '."' in category:#if clause handles award names ending with quotes ex. "django unchained." 
                category = category.split('."',1)[0]
                category += str('."')
            category = category.split('#',1)[0] #removes any hashtags remaining
            if category != '' and key != '':
                output.append({'winner': key, 'category': titlecase(category), 'max': max(awards[key][categoryKey]), 'min': min(awards[key][categoryKey]), 'ave': numpy.mean(awards[key][categoryKey]), 'positions': awards[key][categoryKey], 'median': numpy.median(awards[key][categoryKey])})
    return output

def getNominees(tweets):
    nominee = re.compile('.+.+should\shave\swon.+.+')
    # should of won
    # should've won
    # robbed
    g = re.compile('.+.+\sgoes\sto.+.+')
    h = re.compile('.+.+wins.+.+for.+.+')
    flag = False
    listing = []
    ret = {}
    for t in tweets:
        if nominee.match(t):
            name = re.split('should\shave\swon',t)[0]
            name = re.split('[?.,!]', name)
            name = name[len(name)-1].lstrip().rstrip()
            if 'but' in name:
                name = re.split('but\s', name)
                name = name[len(name)-1].lstrip().rstrip()
            if len(name)<=3:
                continue
            if "@" in name:
                continue
            upper = 0
            wordcount = 1
            for l in name:
                if l.isupper():
                    upper += 1
                if l == " ":
                    wordcount += 1
            if float(upper)/float(wordcount) < .5 or float(upper)/float(len(name))>.3:
                continue
            listing.append(name)
        elif h.match(t) and len(listing) > 0:
            award = re.split('for\s',t)
            for phrase in award:
                p = phrase.lower().lstrip().rstrip()
                if re.match('^best', p):
                    if len(p.split(" ")) > 6:
                        continue
                    if "#" in p:
                        continue
                    #print p + "\n"
                    for persona in listing:
                        if p not in ret.keys():
                            ret[p] = []
                        if persona not in ret[p]:
                            ret[p].append(persona)
                    listing = []
        elif g.match(t) and len(listing) > 0:
            words = re.split('\sgoes\sto',t)
            if re.match('^best',words[0].lower().lstrip()):
                category = words[0].lower().lstrip().rstrip()
                if len(category.split(" ")) > 6:
                    continue
                if "#" in category:
                    continue
                #print category + "\n"
                for persona in listing:
                    if category not in ret.keys():
                        ret[category] = []
                    if persona not in ret[category]:
                        ret[category].append(persona)
                listing = []
    return ret

def getHosts(tweets):
    h = re.compile('.+.+\shosts\s.+.+')
    n = re.compile('.+.+\snext\s.+.+')
    votes = {}
    for t in tweets:
        if h.match(t) and not n.match(t):
            tokens = tokenizer.tokenize(t)
            bi_tokens = bigrams(tokens)
            for b in bi_tokens:
                #if isupper(b[0][0]) and isupper(b[1][0]):
                if b[0][0].isupper() and b[1][0].isupper():
                    bJoined = b[0] + ' ' + b[1]
                    if bJoined in votes.keys():
                        votes[bJoined] += 1
                    else:
                        votes[bJoined] = 1
    avg = numpy.mean(votes.values())
    s = numpy.std(votes.values())
    cutoff = avg + 2*s
    hosts = []
    for v in votes:
        if votes[v] >= cutoff and not (('Golden' in v) or ('Globes' in v)):
            hosts.append(v)
    return hosts


# Imperatives Begin Here
with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)
tweets = sorted(tweets, key=itemgetter('created_at')) 
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(tweets)
cleanTweets = []
for t in tweets:
    cleanTweets.append(removeRT(t['text']))



# 1. Find the names of the hosts
print getHosts(cleanTweets)
# 2. For each award, find the name of the winner.
results = winners(cleanTweets)
for a in results:
    print a
# 4. For each award, try to find the nominees
nominees = getNominees(cleanTweets)
for n in nominees:
    print titlecase(n)
    for person in nominees[n]:
        print person
    print "\n"

# Probably going to completely junk this code
# The tweets where it talks about presenters don't seem to have any real correlation to the locations of the award that they are presenting.
# Because they are announced beforehand, though, it is acceptable to parse them from another online source, like Wikipedia
'''p = re.compile('.+.+present.+.+')
query = ''
alchemy = AlchemyAPI()
entities = []
matches = []
matchNumber = []
i = 0
for t in cleanTweets:
    if p.match(t):
        matches.append(t.lower().encode('utf-8'))
        matchNumber.append(i)
        query += t.encode('utf-8') + ' '
        if sys.getsizeof(query)>153000:
            response = alchemy.entities('text',query,{})
            if response['status'] == 'OK':
                entities.extend(response['entities'])
            query = ''
    i += 1
presenters = {}
for e in entities:
    if e['type'] == 'Person':
        eWords = e['text'].split(' ')
        if len(eWords) >= 2 and len(eWords) <= 4 and len(eWords[0]) > 2 and eWords[0][0].isupper():
            presenters[str(e['text'])] = []
for i in range(len(matches)):
    t = matches[i]
    no = matchNumber[i]
    for p in presenters:
        if p.lower() in t:
            presenters[p].append(no)
print presenters'''
# this method completely failed... always chose the same category
'''categoryPresenters = {}
for p in presenters:
	if len(presenters[p]) < 1:
		continue
	median = numpy.median(presenters[p])
	for a in results:
		possibleCategories = {}
		dist = 0
		for pos in a['positions']:
			dist += abs(median - pos)
		possibleCategories[a['category']] = dist
	chosenCategory = min(possibleCategories)
	if chosenCategory in categoryPresenters.keys():
		categoryPresenters[chosenCategory].append(p)
	else:
		categoryPresenters[chosenCategory] = [p]
for cat in categoryPresenters:
	print cat.upper()
	for c in categoryPresenters[cat]:
		print c
	print "\n\n"'''


# this method sucks less, but still has chance accuracy
'''catPresent = {}
for p in presenters:
    if len(presenters[p]) < 1:
        continue
    avg = numpy.median(presenters[p])
    dist = float("inf")
    for a in results:
        diff = numpy.absolute(avg - a['median'])
        if diff < dist:
            dist = diff
            cat = a['category']
    if cat in catPresent.keys():
        catPresent[cat].append(p)
    else:
        catPresent[cat] = [p]

for cat in catPresent:
    print cat.upper()
    for c in catPresent[cat]:
        print c
    print "\n"'''
