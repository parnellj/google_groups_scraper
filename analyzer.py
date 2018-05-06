import glob
import json
import os
import pickle
import spacy
from collections import Counter
CD = os.path.dirname(os.path.realpath(__file__))

def load_threads(weeks=520):
    all_threads = []
    for i, week_path in enumerate(glob.glob(os.path.join(CD, 'outputs', '*'))):
        all_threads += json.load(open(week_path, 'r'))
        if i >= weeks: break
    return all_threads

nlp = spacy.load('en_core_web_lg', disable=['tagger', 'parser'])
print(nlp.pipeline)
titles = [t['thread_title'] for t in load_threads(weeks=9999) if t['thread_title']]

threads = []
entities = Counter()

for i, t in enumerate(titles):
    if i % 1000 == 0: print(i)
    doc = nlp(t)
    threads.append(doc)
    entities.update([ent.lemma_.lower() for ent in doc.ents])