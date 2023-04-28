import sys
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
from nltk.tokenize import RegexpTokenizer
from statistics import mean
import collections
import math

documents = []

# opening the CSV file
with open('bitcoin_articles.csv', mode ='r', encoding='UTF-8')as file:
   
  # reading the CSV file
  csvFile = csv.reader(file)
 
  # gathering initial docs
  for lines in csvFile:
        documents.append(lines[3])

documents = documents[1:]

## tokenizing
nltk_tokenizer=RegexpTokenizer(r'\w+')

for index,document in enumerate(documents):
    documents[index]= nltk_tokenizer.tokenize(document)

## removing stop words
nltk.download('stopwords')
stop_words=set(stopwords.words("english"))
for index,document in enumerate(documents):
    documents[index]=[w for w in document if w not in stop_words ]

## stemming the words
ps=PorterStemmer()
for index,document in enumerate(documents):
    documents[index]=[ps.stem(w).lower() for w in document]

for index,document in enumerate(documents):
    documents[index]=[w for w in document if w.isnumeric() == False]

## collect all words
words = set()
for d in documents:
    words.update(d)

## average doc length
avdl = np.mean([len(d) for d in documents])

## calculate idf for each word
idf_w = dict()
for w in words:
    idf_w[w] = math.log((len(documents) + 1)/(len([1 for d in documents if w in d])))


## tf formula for each word in a doc
def tf(w,d):
    return (d.count(w) / (len(d) + 0.5))

## calculate tf vector for each doc
tf_matris = []
for d in documents:
    word_freq = dict()
    for w in words:
        word_freq[w] = tf(w,d)
    tf_matris.append(word_freq)

## for finding context(bag of words) of each word w:
## --> find top 5 docs having highest tf for w. then average tf verctor of these docs
top_rank = 5
word_context = dict()
for w in words:
    l = dict()
    for row in range(len(tf_matris)):
        l[row] = tf_matris[row][w]
    l_sorted = sorted(l, key=l.get, reverse=True)
    top_ranked_docs = []
    i = 0
    for s in l_sorted:
        if i == top_rank:
            break
        top_ranked_docs.append(list(tf_matris[s].values()))
        i+=1
    word_context[w] = list(np.average(top_ranked_docs, axis=0))


## calculate idf in sim(d1,d2) or not
idf_en = True

def internal_mult(x,y):
    s = 0.0
    words_lst = list(words)
    for i in range(len(words)):
        if idf_en == False:
            s += word_context[x][i] * word_context[y][i]
        else:
           s += word_context[x][i] * word_context[y][i] * idf_w[words_lst[i]] 
    return s

def paradigmatic(w1):
    results = dict()
    for w in words:
        results[w] = internal_mult(w1,w)
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]))
    print(sorted_results)



paradigmatic('trade')
    






