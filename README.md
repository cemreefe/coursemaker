# Course Maker
A script to parse sentences in a language corpus, and sort them in an order ideal for language studies.

## The Idea

![number of known most used words versus their cumulative usage percentage in the whole corpus. credit: @thevenuehouse on reddit](./media/graph.png)

Most used 100 words in a language make up approximately 50% of words in a corpus (This of course varies from language to language. E.g. it is lover in agglutinative languages). If you sort the most used words and start learning words from this list (frequency sorted list `fsl`) you can effectively increase your hit rate in the corpus. 

I want to sort sentences in a similar manner. The first sentence of the proposed order shall ideally contain the first n words in the `fsl`. Any sentence can contain any number of words from previous sentences, and tries to incorporate any number of next m most used words.

> Work in progress...



## More Word Statistics 

*src. : @thevenuehouse on reddit*

A few interesting learnings:

- The top word 'yang', meaning 'that' or 'which' makes up 3% of all usage.
- Top 10 most common = 18% of all usage
- Top 100 most common = 50% of all usage
- Getting from 0% to 50% understanding of vocabulary means learning just 100 words. Getting from 50% to 98% means learning 9900.
- Getting from 80% to 99% means learning 7,500 words!
- This indicates the road from intermediate to fluent is much more difficult than novice to intermediate.
- The graph shows the higher a word is ranked in commonness, it's use in the language exponentially grows.

Limitations:

- This doesn't take into account phrasal verbs (e.g. in English 'Wash up', 'take off').
- OpenSubtitles corpus has nearly 1000 examples of nonsense words that I tried to remove, but some may remain. If they only occur once they make little impact to the drawing.
- The corpus is quite small at 196,000 words (10,000 unique)