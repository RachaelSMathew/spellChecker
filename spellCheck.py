import math
from metaphone import doublemetaphone
from datetime import datetime
import subprocess as sp
from functools import cache
import re
import gzip
import sys

invertedIndex = {}
phoneticC = {}
countLength = {}
lastEdit = {}
docs = []
num = 0

#get the files for the dictionary 
for f in sp.getoutput("cd fileDict && ls").split("\n"):
    f.replace(" ","\ ")
    docs.append(open("fileDict/"+f, "rb"))
firstRow = ["z","x","c","v","b","n","m"]
secRow = ["a","s","d","f","g","h","j","k","l"]
thirdRow = ["q","w","e","r","t","y","u","i","o","p"]
allLetters = "zxcvbnmasdfghjklqwertyuiop"

@cache
#farthest distance will be from q to m (6.67)
def distKey(a, b):
    a = a.lower()
    b = b.lower()
    if  a not in allLetters or b not in allLetters:
        return 4;
    cor1 = []
    cor2 = []
    if a in thirdRow:
        cor1 = [thirdRow.index(a), 2]
    elif a in secRow:
        cor1 = [secRow.index(a)+.3, 1]
    elif a in firstRow:
        cor1 = [firstRow.index(a)+.6, 0]

    if b in thirdRow:
        cor2 = [thirdRow.index(b), 2]
    elif b in secRow:
        cor2 = [secRow.index(b)+.3, 1]
    elif b in firstRow:
        cor2 = [firstRow.index(b)+.6, 0]
    return math.sqrt(abs(cor1[0]-cor2[0])**2 + abs(cor1[1]-cor2[1])**2)

@cache
##taken from https://www.educative.io/answers/the-levenshtein-distance-algorithm
def levenshteinDist(a, b, specific=False):
    # Declaring array 'D' with rows = len(a) + 1 and columns = len(b) + 1:
    D = [[0 for i in range(len(b) + 1)] for j in range(len(a) + 1)]

    # Initialising first row:
    for i in range(len(a) + 1):
        D[i][0] = i

    # Initialising first column:
    for j in range(len(b) + 1):
        D[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                # Adding 1 to account for the cost of operation
                insertion = (1 if not specific else (distKey(b[j-1], "g") if i==1 else distKey(b[j-1], a[i-2]))) + D[i][j - 1] #cost from b[j-1] to a[i-2] and if i==1 then b[j-1] to g
                deletion = (1 if not specific else (distKey(a[i-1], "g") if i==1 else distKey(a[i-1], a[i-2]))) + D[i - 1][j] #cost from a[i-1] and a[i-2] and if i==1 then a[i-1] to g
                replacement = (1 if not specific else (distKey(a[i-1], b[j-1]))) + D[i - 1][j - 1] #cost from a[i-1] b[j-1]

                # Choosing the best option:
                D[i][j] = min(insertion, deletion, replacement)

    return D[len(a)][len(b)]

@cache
#popularity of word 
def popularity(word):
    count = 0
    for doc in invertedIndex[word]:
        count += (len(invertedIndex[word][doc]) / lastEdit[doc])
    if count == 1:
        return 1
    return math.log(count)

def sortSecond(val):
    return val[1]

@cache
def wordStartSame(word): ## and length diff is at max 3 letters from word 
    arr = []
    for words in invertedIndex:
        if words == "" or words == " ":
            continue
        if words[0] == word[0] and abs(len(word)-len(words)) <= 2:
            arr.append(words)
    return arr

###########                     MAIN                    ##############
#creating dictionary 
for doc in docs:
    while True:
            content=doc.readline()
            if not content:
                break
            words = str(content).replace("\\n", "").replace("\\r", "").replace("\\",'').replace("\'b", "").replace("b'", ""). replace("b\"", "")
            words = re.split(r'x[a-fA-F0-9][a-fA-F0-9]|,', words)
            for word in words:
                wordArr = word.split()
                filename = docs.index(doc)
                for single in wordArr:
                    single = single.strip()
                    single = single.rstrip("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'")
                    single = single.lstrip("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'")
                    if single == "" or single == " "  or single.isnumeric() or len(single) == 1 or not re.search(r'[a-zA-Z]+', single):
                        continue
                    if single in invertedIndex:
                        if filename in invertedIndex[single]:
                            invertedIndex[single][filename].append(num)
                        else:
                            invertedIndex[single][filename] = [num]
                    else:
                        invertedIndex[single] = {filename: [num]};
                num = num + 1
    dateEdit = sp.getoutput("stat "+re.escape(doc.name).replace("\'", "\\'")).split("Modify: ")[1].split(".")[0]
    datTimeFormat = datetime.strptime(dateEdit, '%Y-%m-%d %H:%M:%S')
    lastEdit[docs.index(doc)] = (datetime.now()  - datTimeFormat).total_seconds() / (60 * 60) # get difference in hours
lastEdit = {k: v for k, v in sorted(lastEdit.items(), key=lambda item: item[1])} #sort dates of last edit

for doc in docs:
    doc.close()

#delta encoding of inverted Index 
for word in invertedIndex.keys():
    for doc in invertedIndex[word]:
        for num in range(len(invertedIndex[word][doc])-1, 0, -1) : 
            invertedIndex[word][doc][num] = invertedIndex[word][doc][num] - invertedIndex[word][doc][num-1]

#creating phoentic code and dictionary of words of same length 
for word in invertedIndex.keys():
    pC = doublemetaphone(word)[0]
    if pC in phoneticC:
        phoneticC[pC].append(word)
    else:
        phoneticC[pC] = [word]

    if len(word) in countLength:
        countLength[len(word)].append(word)
    else:
        countLength[len(word)] = [word]

#take words from text
fileR = open(sys.argv[1], "r")
words = []
while True:
    content=fileR.readline()
    if not content:
        break
    words += (content.replace("\n", "").split(" "))
fileR.close()

@cache
def returnRank(arg):
    if len(arg) == 1:
        return
    arg = arg.rstrip("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'")
    arg = arg.lstrip("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'")
    if arg == "" or arg == " "  or arg.isnumeric():
        return

    pC = doublemetaphone(arg)[0] if doublemetaphone(arg)[0] in phoneticC else doublemetaphone(arg)[1]
    wordSamepC = []
    if pC in phoneticC and pC != "": #might not find words that are the same code 
        wordSamepC = phoneticC[pC]
    wordSameLen = countLength[len(arg)]
    iDist = []

    for word in wordSamepC:
        dist = .0001 if levenshteinDist(arg, word) == 0 else levenshteinDist(arg, word) 
        iDist.append([word, (dist)]) 
        iDist.sort(key=sortSecond) #getting SMALLEST distance 

    for word in wordStartSame(arg):
        dist = .0001 if levenshteinDist(arg, word) == 0 else levenshteinDist(arg, word) 
        if [word, (dist)] not in iDist:
            iDist.append([word, (dist)]) 
        iDist.sort(key=sortSecond) #getting SMALLEST distance 

    for word in wordSameLen:
        dist = .0001 if levenshteinDist(arg, word) == 0 else levenshteinDist(arg, word)
        if [word, (dist)] not in iDist:
            iDist.append([word, (dist)]) 
        iDist.sort(key=sortSecond) #getting SMALLEST distance 

    #filter the iDist array if two elements next to each other are more than .01 apart use distance thingy 
    """
    insertion = (distKey(b[j-1], "g") if i==1 else distKey(b[j-1], a[i-2])) + D[i][j - 1] #cost from b[j-1] to a[i-2] and if i==1 then b[j-1] to g
    deletion = (distKey(a[i-1], "g") if i==1 else distKey(a[i-1], a[i-2])) + D[i - 1][j] #cost from a[i-1] and a[i-2] and if i==1 then a[i-1] to g
    replacement = distKey(a[i-1], b[j-1]) + D[i - 1][j - 1] #cost from a[i-1] b[j-1]
    """
    #filter the iDist array such that any two elements next to each other are  more than .01 apart, and if so, then check the popularity of both 
    iDistN = [iDist[0]]
    for index in range(1, len(iDist)):
        i = len(iDistN) - 1
        if abs(iDist[index][1] - iDistN[i][1]) <= 0.01:
            if levenshteinDist(iDist[index][0], arg, True) < levenshteinDist(iDistN[i][0], arg, True) or popularity(iDist[index][0])*0.1 > popularity(iDistN[i][0]):
                iDistN[i] = iDist[index]
        else:
            iDistN.append(iDist[index])
    iDist = iDistN

    if iDist[0][0] != arg:
        print("Instead of \""+ arg+ "\" did you mean this?")
        for d in iDist:
            print(d[0])

#take in every argument
for arg in words:
    returnRank(arg)
