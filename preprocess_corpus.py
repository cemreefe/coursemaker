import numpy as np
import pandas as pd
import re
import string
import json
import sys

# Remove 1st argument from the
# list of command line arguments
argument_list = sys.argv[1:]

pre_tokenization_replace = []
path = ""
out_path = ""
start_string = ""

for i, argument in enumerate(argument_list):

    if argument == "-ptc":
        pre_tokenization_replace = eval(argument_list[i+1])

    elif argument == "-i":
        path = argument_list[i+1]

    elif argument == "-o":
        out_path = argument_list[i+1]
        
    elif argument == "-s":
        start_string = argument_list[i+1]
        
if not (path and out_path):
    #print(bool(in_path),bool(out_path),column_name)
    print("""
    -i:\tinput text file containing the corpus
    -o:\toutput csv file for sentences
    -s:\t(optional) the starting string for the corpus in the file (to skip through some initial parts)
    """)
    sys.exit()


# read file into string
def readfile(path):
    f = open(path, 'r')
    c = f.read()
    return c

# normalize a string
def normalize(s, case_folding=True, stopword_removal=True, punctuation_removal=True, newline_removal=True, punctuation_whitelist=[]):

    if not s:
        return None

    # set lowercase
    if case_folding:
        s = s.lower()

    # remove custom html characters and tabs
    s = re.sub(r"&[a-z]{1,3};", " ", s)
    s = s.replace('\t', '')

    # replace punctuation marks with a blank space
    if punctuation_removal:
        for character in list(string.punctuation) + ['”', '“']:
            if character not in punctuation_whitelist:
                s = s.replace(character, ' ')

    # remove newline characters ('\n')
    if newline_removal:
        s = s.replace('\n', ' ')

    # remove stop words given in stopwords.txt from the string
    if stopword_removal:
        b = open('stopwords.txt')
        stop_words = [ line[:-1] for line in b.readlines() ]
        b.close()

        for word in stop_words:
            s = re.sub(r" {} ".format(word), " ", s)
            s = re.sub(r"^{} ".format(word), " ", s)
            s = re.sub(r" {}$".format(word), " ", s)

    # shorten mutliple blank spaces into one
    s = re.sub(r" +", " ", s)

    return s


corpus = readfile(path)

corpus = normalize(corpus, stopword_removal=False, punctuation_whitelist=['!', '.', '?', '\''])

for val_tuple in pre_tokenization_replace:
    corpus = corpus.replace(val_tuple[0], val_tuple[1])
    
#start      = 'the footsteps die out for'
startindex = corpus.index(start_string)

sentences  = re.split('\.|\?|\!', corpus[startindex:])

words      = normalize(corpus, stopword_removal=False)[startindex:].split(' ')
words      = [ word for word in words if re.match('[a-z]+', word) ]
    
unique_words, counts_words = np.unique(words, return_counts=True)

frequencies = []
for word, count in zip(unique_words, counts_words):
    frequencies.append([word, count])
    
frequencies.sort(key = lambda x: -x[1]) 

frequencies = np.array(frequencies)

#freqs_cumulative = [0]
#for freq in frequencies[:,1].astype(int):
#    freqs_cumulative.append(freqs_cumulative[-1] + freq)
    
#wcount = freqs_cumulative[-1]

f = open(out_path+"_freqs.csv", "w+")
str_to_file = 'word,count\n'
for row in frequencies:
        str_to_file += f'{row[0]},{row[1]}\n'
f.write(str_to_file)
f.close()


#print(sentences)
df = pd.DataFrame(sentences)
df.rename(columns={0:'sentence'}, inplace=True)

df.to_csv(out_path+".csv", index=False)

