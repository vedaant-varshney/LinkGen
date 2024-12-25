import os
import yake
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer as wnl

# Supply vault directory here
vault_dir = "/mnt/d/Documents/ObsidianDev"

nltk.download('wordnet')
lemmatizer = wnl()

# Lists md files in root dir
def list_files_recursively(root_dir):
    file_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # removes .obsidian directory from search path
        dirnames[:] = [d for d in dirnames if d != '.obsidian']
        for file in filenames:
            file_list.append(os.path.join(dirpath, file))
    return [f for f in file_list if f.endswith('.md')]

filenames = list_files_recursively(vault_dir)

contents = []

for filen in filenames:
    with open(filen, 'r') as f:
        content = f.read()
        ind = content.find("## Generated Tags")
        if ind != -1:
            content = content[:ind]
        contents.append((filen, content))


language = "en"
max_ngram_size = 2
deduplication_threshold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 10

custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
tag_list = {}
global_tags = {} 

for content in contents:
    keywords = custom_kw_extractor.extract_keywords(content[1])
    blocked = ('pasted', 'image', 'pasted image', 'tags', 'links', 'generated tags', 'and links', 'tags and links')
    keywords = [([lemmatizer.lemmatize(word.lower()) for word in keyword[0].split(" ")], keyword[1]) for keyword in keywords if keyword[0].lower() not in blocked]


    parent_set = {} 
    for keyword_set in keywords:
        for ind_word in keyword_set[0]:
            if ind_word not in parent_set:
                parent_set[ind_word] = keyword_set[0]

    output_tags = set(["_".join(tag) for tag in parent_set.values()])
    output_tags = output_tags.union(set(parent_set.keys()))
    for tag in output_tags:
        if tag not in global_tags:
            global_tags[tag] = 1
        else:
            global_tags[tag] += 1


    tag_list[content[0]] = output_tags

print(global_tags)
global_tags = {key: value for key, value in global_tags.items() if value >= 2}
global_tags = set(global_tags.keys())
print(global_tags)


for fname in tag_list.keys():
    tag_list[fname] = global_tags.intersection(tag_list[fname])

vectorizer = TfidfVectorizer(stop_words='english')


tfidf_matrix = vectorizer.fit_transform([content[1] for content in contents])
sim_matrix = cosine_similarity(tfidf_matrix)

tolerance = 0.2
for i, content in enumerate(contents):
    lines = []
    with open(content[0], 'r+') as f:
        lines = f.readlines()
        try: 
            ind = lines.index("## Generated Tags and Links\n")
            print(lines[ind])
        except ValueError:
            ind = len(lines)

        # cosine sim_matrix for document 
        doc_sim_mat = sim_matrix[:, i]

        links = []
        for j in range(len(doc_sim_mat)):
            if doc_sim_mat[j] > tolerance and doc_sim_mat[j] != 1:
                links.append(contents[j][0][len(vault_dir)+1:])

        # links = ["[["+ link "]]" for link in links]
        links = " ".join(["[["+link+"]]" for link in links])
        tags = " ".join(["#"+tag for tag in tag_list[content[0]]])

        if ind != len(lines):
            lines[ind+1] = links+"\n"
            lines[ind+2] = tags+"\n"
        else:
            lines.append("\n\n---\n") 
            lines.append("## Generated Tags and Links\n") 
            lines.append(links+"\n") 
            lines.append(tags+"\n\n")
            lines.append("\n---\n") 
        
        f.seek(0)
        f.writelines(lines)
