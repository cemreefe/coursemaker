from deep_translator import GoogleTranslator

def translate_adaptor(text, source, target):
    translator = GoogleTranslator(source=source, target=target)
    return translator.translate(text, src=source, dest=target)

import re

mdf = ""

with open('courses/russian_course.md', 'r') as f:
    mdf = f.read()
    
sentences = mdf.split('\n\n\n')[1:-1]

def mdf_to_obj(mdf):
    sentence = re.search(r'[0-9]+\. "(.*?)"', mdf).group(1)
    words = re.findall(r'\*\*(.+)\*\*: (.+)', mdf)
    translation = translate_adaptor(sentence, 'ru', 'en')
    return {
        'sentence': sentence,
        'words': words,
        'translation': translation
    }

objects = []

for sentence in sentences:
    if sentence in [o['sentence'] for o in objects]:
        print(sentence, 'already translated')
        continue
    obj = mdf_to_obj(sentence)
    print(obj)
    objects.append(obj)

objects

import json 

with open('courses/russian_course.json', 'w') as f:
    json.dump(objects, f, ensure_ascii=False, indent=2)




