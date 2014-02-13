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
        return removeRT(t[len(t)-1]) # this recursiveness is necessary to remove the case of multiple RTs
    else:
        return t[0]

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

def getNominees(tweets):
    nominee = re.compile('.+.+should\shave\swon.+.+')
    g = re.compile('.+.+\sgoes\sto.+.+')
    h = re.compile('.+.+wins.+.+for.+.+')
    flag = False
    listing = []
    ret = {}
    for t in tweets:
        t = removeRT(t['text'])
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


# Imperatives Begin Here
with open('goldenglobes.json', 'r') as f:
    tweets = map(json.loads, f)


results = winners(tweets)
for a in results:
    print a
nominees = getNominees(tweets)
for n in nominees:
    print titlecase(n)
    for person in nominees[n]:
        print person
    print "\n"
