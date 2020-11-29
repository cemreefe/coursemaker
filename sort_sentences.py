import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt

# Remove 1st argument from the
# list of command line arguments
argument_list = sys.argv[1:]

in_path = ""
out_path = ""
column_name = ""
freq_path = ""
sentence_count = 0
consider_sentence_limit = 0
min_sentence_length = 5

for i, argument in enumerate(argument_list):

    if argument == "-is":
        in_path = argument_list[i+1]
    
    elif argument == "-if":
        freq_path = argument_list[i+1]
        
    elif argument == "-o":
        out_path = argument_list[i+1]
        
    elif argument == "-col":
        column_name = argument_list[i+1]
    
    elif argument == "-sc":
        sentence_count = eval(argument_list[i+1])
        
    elif argument == "-csl":
        consider_sentence_limit = eval(argument_list[i+1])
        
    elif argument == "-msl":
        min_sentence_length = eval(argument_list[i+1])
        
if not (in_path and out_path and column_name and sentence_count and freq_path):
    #print(bool(in_path),bool(out_path),column_name)
    print("""
    -is:\tinput csv file containing sentences
    -if:\tinput csv file containing frequencies
    -o:\toutput csv file for sorted sentences
    -col:\tname of the column containing sentences in the input csv file
    -sc:\tnumber of sentences to return, default (-1 for max)
    -csl:\tnumber of considered sentences in the corpus
    -msl:\tminimum sentence length for consideration
    """)
    sys.exit()
        
        

        
df_s        = pd.read_csv(in_path)

sentences   = list(df_s[column_name])
sentences   = [ str(sentence) for sentence in sentences if str(sentence) != "nan" ]

consider_sentence_limit = consider_sentence_limit if consider_sentence_limit else len(sentences) 

sentences   = sentences[:consider_sentence_limit]

df_f        = pd.read_csv(freq_path)

frequencies = np.array(df_f)
frequencies[:,1] = frequencies[:,1].astype(int)

words       = frequencies[:,0]

#print(frequencies[:10])

freqs_cumulative = [0]
for freq in frequencies[:,1].astype(int):
    freqs_cumulative.append(freqs_cumulative[-1] + freq)
    
    
wcount = freqs_cumulative[-1]


def sentences_to_feature(sentences, feature, frequencies):
    all_orders = []
    
    freq_list = list(frequencies[:,0])
    freq_dict = {}
    for i, word in enumerate(freq_list):
        freq_dict[word] = i
        
    freq_set = set(freq_list)
    
    if feature == 'orders':
        for sentence in sentences:
            sentence_orders = [ freq_dict[word] for word in sentence.split(' ') if word in freq_set]
            all_orders.append(sentence_orders)
        
        return all_orders
    
    if feature == 'frequencies':
        freqs = np.array(frequencies[:,1]).astype(float)/wcount
        for sentence in sentences:
            sentence_orders = [ freqs[freq_dict[word]] for word in sentence.split(' ') if word in freq_set]
            all_orders.append(sentence_orders)
        
        return all_orders


sentence_frequencies = sentences_to_feature(sentences, 'frequencies', frequencies)


# get ideal sentence with most average vocab coverage return
def get_ideal_index(sentences, frequencies):
    
    xfrequencies = np.copy(frequencies)
    
    xwords       = set(xfrequencies[:,0])

    xsentences = [' '.join([token for token in set(sentence.split(' ')) if token in xwords ]) for sentence in sentences ]
    xsentence_frequencies = sentences_to_feature(xsentences, 'frequencies', frequencies)

    sums = [ np.sum(xsf)/len(xsf) if xsf != [] else 0 for xsf in xsentence_frequencies ]

    return np.argmax(sums)
    
    
def get_in_order(sentences, frequencies, sentence_count=20, metric="vanilla"):
    
    sentence_count = sentence_count if sentence_count != -1 else len(sentences)
    
    sentences_ordered = []

    remaining_sentences   = [ sentence for sentence in set(sentences.copy()) if len(sentence)>min_sentence_length ]
    remaining_frequencies = np.copy(frequencies)

    print(len(remaining_sentences), len(remaining_frequencies))
    
    cumulative_return = 0

    vocab = set()
    learning_history = [0]

    for i in range(sentence_count):

        if metric == "vanilla":
            chosen_index = 1

        elif metric == "max-avg":
            chosen_index = get_ideal_index(remaining_sentences, remaining_frequencies)
        
        else:
            print("error: invalid metric")
            return None
        
        if chosen_index == -1:
            print("error")
            return None

        sentence = remaining_sentences.pop(chosen_index)

        newvocab = [ word for word in set(sentence.split(' ')) if word not in vocab ]
        filtered = ' '.join(newvocab)

        orders   = sentences_to_feature(list([filtered]), 'orders', remaining_frequencies)
        sfreqs   = sentences_to_feature(list([filtered]), 'frequencies', remaining_frequencies)

        vocab.update(newvocab)

        new_percentage = 100*np.sum(sfreqs) if sfreqs else 0
        cumulative_return += new_percentage

        trunc = 100
        print('{} - return: {:.2f}% ({:.2f}% cumulative)'.format(i, new_percentage, cumulative_return),
              f'\n{chosen_index}:\t"{sentence[:trunc]}{"..."*int(len(sentence)>trunc)}"', '\n')

        learning_history.append(learning_history[-1] + new_percentage)
        sentences_ordered.append(sentence)

        for order in orders:
            remaining_frequencies = np.delete(remaining_frequencies, order, 0)
            
        if not remaining_sentences:
            break
            
    #plt.plot(learning_history)
    
    return sentences_ordered, learning_history    
    
def get_cumulative_count(sentences):
    counts = [0]
    vocabs = [set([]), ]
    for sentence in sentences:
        tokens = [ token for token in set(sentence.split(' ')) if token in words ]
        counts.append(len(tokens))
        vocabs.append(set(list(vocabs[-1])+tokens))
    return counts, vocabs
    
ordered_vanilla, history_vanilla = get_in_order(sentences, frequencies, sentence_count, metric="vanilla")
ctsva, vcbva = get_cumulative_count(ordered_vanilla)
    
ordered_maxavg, history_maxavg = get_in_order(sentences, frequencies, sentence_count, metric="max-avg")
ctsma, vcbma = get_cumulative_count(ordered_maxavg)



f = open(out_path+".csv", "w+")
str_to_file = 'sentence, cumulative coverage\n'
for sentence, coverage in zip(ordered_maxavg, history_maxavg):
        str_to_file += f'{sentence}, {coverage}\n'
f.write(str_to_file)
f.close()


plt.plot(100*np.array(freqs_cumulative[:len(vcbma[-1])+1])/wcount, label='ideal VCC')
plt.plot(list(map(len, vcbma)), history_maxavg, label='constructed VCC')
plt.plot(list(map(len, vcbva)), history_vanilla, label='VCC for the original sentence order')
plt.title('Vocabulary coverage by number of studied words')
plt.ylabel('vocabulary coverage (%)')
plt.xlabel('words studied')
#plt.xticks(range(len(vcbma)+1)[::10])
plt.legend()
plt.show()


    
    
    
