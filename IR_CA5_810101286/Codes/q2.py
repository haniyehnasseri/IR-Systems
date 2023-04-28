from mrjob.job import MRJob
from mrjob.step import MRStep
import csv
import sys
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from datetime import datetime
from datetime import datetime as dt


# a
class bestvalidations(MRJob):

    ## puts (validation, 1) pairs as mapping
    def mapper(self, _, line):
        row = line.split('\t')
        yield (row[2], 1)
        
    ## after grouping each validation with a list containing 1 as many as its occurance, reducer sums these 1s to get validation count
    def reducer(self, key, counts):
        yield key, sum(counts)

    combiner = reducer

## b
class mostrankedvalidations(MRJob):

    ## this mapper gets a review and maps its varions to its rating
    def mapper(self, _, line):
        row = line.split('\t')
        try:
            yield row[2], int(row[0])
        except ValueError:
            self.increment_counter('warn', 'missing rating', 1)


    ## after grouping each variation with a list containing ratings , this reducer averages the ratings for the given variation
    def reducer(self, key, ratings):
        c = 0
        s = 0
        for rating in ratings:
            c += 1
            s += rating
        yield key, s/c


nltk_tokenizer=RegexpTokenizer(r'\w+')
nltk.download('stopwords')
stop_words=set(stopwords.words("english"))
ps=PorterStemmer()
## c
class positiveratingsbigrams(MRJob):
    def smaller(self,w1,w2):
        if w1 < w2:
            return w1
        if w2 < w1:
            return w2
        if w1 == w2:
            return w1

    def bigger(self,w1,w2):
        if w1 < w2:
            return w2
        if w2 < w1:
            return w1
        if w1 == w2:
            return w1

    ## this mapper gets the line and if the rating is 4 or 5 for the review part,
    #  maps each bigram in it to the number of times it's been seen in the review sentence
    def mapper(self, _, line):
        row = line.split('\t')
        try:
            current_rating = int(row[0])
            if(current_rating == 4 or current_rating == 5):
                adjcents = dict()
                review = nltk_tokenizer.tokenize(row[3])
                review = [w for w in review if w not in stop_words and w.isnumeric() == False]
                review = [ps.stem(w).lower() for w in review]
                for i in range(0, len(review) - 1):
                    t = self.smaller(review[i], review[i+1]) + "|" + self.bigger(review[i], review[i+1])
                    if t in adjcents:
                        adjcents[t] += 1
                    else:
                        adjcents[t] = 1
                for key in adjcents:
                    yield key, adjcents[key]

        except ValueError:
            self.increment_counter('warn', 'missing rating', 1)

    ## after grouping each bigram with a list containing number of times it's been seen in the good rated review,
    #  this reducer sums the ocuurances times and pairs the bigram with its total occurance time in all good rated reviews
    def reducer(self, key, repeats):
        yield key, sum(repeats)

    combiner = reducer


## d
class worstvalidationlatestreview(MRJob):
    ## this mapper gets the line and maps its variation with the line itself!
    def mapper(self, _, line):
        row = line.split('\t')
        yield row[2], line

    ## after grouping each variation with all reviwes related to it,
    #  this reducer maps each validation with a tuple containing number of bad rated (1) reviews given to it 
    # and the last review for the validation (review with the maximum date)
    def reducer(self, key, values):
        try:
            number_of_ones = 0
            latest_date = None
            latest_cm = None
            for line in values:
                row = line.split('\t')
                if int(row[0]) == 1:
                    number_of_ones += 1
                date = dt.strptime(row[1], "%d-%b-%y")
                if latest_date is None or date > latest_date:
                    latest_date = date
                    latest_cm = row[3]
            yield key, (number_of_ones, latest_cm)

        except ValueError:
            self.increment_counter('warn', 'missing rating', 1)

if __name__ == '__main__':
    worstvalidationlatestreview.run()