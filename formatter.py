#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import sys
import string
import os

accepted_formats = ['md', 'html']
repo_url      = "https:/github.com/cemreefe/coursemaker"

language_name = ""
csv_path      = ""
out_format    = "md"
out_path      = ""

argument_list = sys.argv

for i, argument in enumerate(argument_list):

    if argument == "-i" or argument == "--input":
        csv_path = argument_list[i+1]

    elif argument == "-l" or argument == "--language":
        language_name = argument_list[i+1]

    elif argument == "-o" or argument == "--output":
        out_path = argument_list[i+1]

    elif argument == "-f" or argument == "--format":
        if argument_list[i+1].lower() in accepted_formats:
            out_format = argument_list[i+1].lower()
        else:
            print('format not supported, using format ".md"')
        


if not (csv_path and language_name):
    
    print("""
    -i:  \t*(--input) input csv file containing sentences
    -l:  \t*(--language) name of the corpus's language
    -o:  \t (--output) path for formatted output file
    -f:  \t (--format) output format (default: 'md')
         \t  > available: 'md', 'html'
         \t  > future work: 'latex'

    *: required
    """)
    sys.exit()

# get words from a sentence's newvocab field and return a list of said words
def get_words_as_list(words_str):
    words = words_str.split('), (')

    for i, word in enumerate(words):
        word = word[1:] if (word[0] == '(' and i == 0) else word
        word = word[:-1] if (word[-1] == ')' and i == len(words)-1) else word
        
        words[i] = word

    return words

# process a sentence's fields
# from the course data
def sentence_to_fields(pt):
    percentage = pt[1]

    # format sentence
    # TODO: questions
    # TODO: proper names
    # TODO: capitalized languages like german
    sentence   = pt[0][0].upper() + pt[0][1:] + '.'
    
    # get words as a list, needs more processing
    words = get_words_as_list(pt[2])

    return percentage, sentence, words

# format all sentences and their fields
# in markdown format
def markdownify_course(pts, language_name=language_name, repo_url=repo_url):
    title         = f"{language_name} Vocab Builder"
    description   = f"This is an automatically generated sentence list to help you build {language_name} vocab. The sentences are introduced in an order to help you learn words starting from the most frequently used. After each sentence you can find the ratio of words you know in the corpus used to generate this content. For more information visit [the project repo]({repo_url}). If you want to use this generated material feel free to inform me. Cheers!"

    formatted = ""
    formatted += f"# {title}\n\n{description}\n\n---\n\n"

    for i, pt in enumerate(pts):
        
        percentage, \
        sentence,   \
        words       = sentence_to_fields(pt) 
        
        # sentence number and sentence
        formatted += f'### {i+1}. "{sentence}"\n'
        
        # new vocabulary in the sentence
        for word in words:
            entry    = word[:word.index(':')]
            meaning  = word[word.index(':'):]
            bulletpt = f"**{entry}**{meaning}"

            formatted += f'* {bulletpt}\n'
        
        # cumulative coverage percentage
        formatted += f'\n`{percentage:05.2f}%`\n\n\n\n'

    return formatted

# format all sentences and their fields
# in markdown format
def htmlify_course(pts, language_name=language_name, repo_url=repo_url):
    title         = f"{language_name} Vocab Builder"
    description   = f"This is an automatically generated sentence list to help you build {language_name} vocab. The sentences are introduced in an order to help you learn words starting from the most frequently used. After each sentence you can find the ratio of words you know in the corpus used to generate this content. For more information visit <a href='{repo_url}'>the project repo</a>. If you want to use this generated material feel free to inform me. Cheers!"

    formatted = f"""
    <head>
        <title>{title}</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
        <style>
            body {{
                max-width: 760px;
                margin: auto;
            }}
            .percentage {{
                list-style-type:none;
            }}
            @media print {{
               .block {{page-break-inside: avoid;}}
            }}
        </style>
    </head>
    """
    formatted += "<body>"

    formatted += f"<h1>{title}</h1>\n\n<p>{description}</p>\n<br><hr>"

    for i, pt in enumerate(pts):

        formatted += "<div class='block'>"
        
        percentage, \
        sentence,   \
        words       = sentence_to_fields(pt) 
        
        # sentence number and sentence
        formatted += f'<h3>{i+1}. "{sentence}"</h3>\n'
        
        formatted += '<ul>\n'
        # new vocabulary in the sentence
        for word in words:
            entry    = word[:word.index(':')]
            meaning  = word[word.index(':'):]
            bulletpt = f"<b>{entry}</b>{meaning}"

            formatted += f'<li>{bulletpt}</li>\n'
        
        # cumulative coverage percentage
        formatted += f'<li class="percentage"><small>{percentage:05.2f}%</small></li>\n'
        formatted += '</ul>\n'
        formatted += '<br>'

        formatted += "</div>"

    formatted += '</body>'

    return formatted

# write formatted string to file
# if output path specified use this field
# if not specified, set default path
def write_to_file(formatted_string, language_name=language_name, out_format=out_format, out_path=out_path):
    if out_path:
        f = open(out_path, 'w+')
    else:
        if not os.path.exists('courses'):
            os.makedirs('courses')
        f = open(f'courses/{language_name}_course.{out_format}', 'w+')
    f.write(formatted_string)
    f.close()

# Capitalize the first letter of each word in the language name
language_name = string.capwords(language_name)

# read the course data from csv
df = pd.read_csv(csv_path, '\t')

# each row holds one sentence and its data
pts = np.array(df)

# remove trailing empty spaces
for pt in pts:
    if pt[0][0] == " ":
        pt[0] = pt[0][1:]

# i just like initializing my variables like this before if/else stmts
formatted_string = None

if out_format == 'md':
    formatted_string = markdownify_course(pts, language_name)

elif out_format == 'html':
    formatted_string = htmlify_course(pts, language_name)


write_to_file(formatted_string)