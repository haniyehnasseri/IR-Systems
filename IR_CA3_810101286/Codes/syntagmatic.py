import sys
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
from nltk.tokenize import RegexpTokenizer
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


nltk_tokenizer=RegexpTokenizer(r'\w+')

for index,document in enumerate(documents):
    documents[index]= nltk_tokenizer.tokenize(document)


nltk.download('stopwords')
stop_words=set(stopwords.words("english"))
for index,document in enumerate(documents):
    documents[index]=[w for w in document if w not in stop_words ]

ps=PorterStemmer()
for index,document in enumerate(documents):
    documents[index]=[ps.stem(w).lower() for w in document]

for index,document in enumerate(documents):
    documents[index]=[w for w in document if w.isnumeric() == False]



# gather all words
words = set()

for d in documents:
    words.update(d)

## mutual information calculation  for two words
def mu(w1,w2):
    doc_length = len(documents)
    delta = 0.0000000001
    p_0_0 = len([d for d in documents if w1 not in d and w2 not in d])/doc_length
    p_1_1 = len([d for d in documents if w1 in d and w2 in d])/doc_length
    p_0_1 = len([d for d in documents if w1 not in d and w2 in d])/doc_length
    p_1_0 = len([d for d in documents if w1 in d and w2 not in d])/doc_length
    p_w1_0 = len([d for d in documents if w1 not in d])/doc_length
    p_w1_1 = len([d for d in documents if w1 in d])/doc_length
    p_w2_0 = len([d for d in documents if w2 not in d])/doc_length
    p_w2_1 = len([d for d in documents if w2 in d])/doc_length
    return (p_0_0 + delta) * math.log((p_0_0 + delta) / ((p_w1_0 + delta) * (p_w2_0 + delta))) + (p_0_1 + delta) * math.log((p_0_1 + delta) / ((p_w1_0 + delta) * (p_w2_1 + delta))) + (p_1_0 + delta) * math.log((p_1_0+ delta) / ((p_w1_1 + delta) * (p_w2_0 + delta))) + (p_1_1 + delta) * math.log((p_1_1 + delta) / ((p_w1_1 + delta) * (p_w2_1 + delta)))

    

def syntagmatic(w1):
    results = dict()
    for w in words:
        results[w] = mu(w1,w)
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]))
    print(sorted_results)

syntagmatic('pioneer')