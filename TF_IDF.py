# -*- coding: utf-8 -*-

import os
from collections import defaultdict

# words_dict - словарь: {слово - список позиций в тексте, где оно встречается}
# 0 соответствует title
# Вывод: слово, количество вхождеий, позиции вхождение
def WriteWordsToFile(file_name, words_dict):
    file = open(file_name, 'w', encoding='utf-8')
    final_length = 0
    for w, positions in words_dict.items():
        final_length += len(positions)
        file.write(w+"\t"+str(len(positions))+"\t")
        file.write(" ".join(str(pos) for pos in positions))
        file.write("\n")
    file.write(str(final_length))
    file.close()

def FileStatistics(input_path, output_path, skip_if_exitst=True):
    if os.path.exists(output_path) and skip_if_exitst:
        return

    input_file = open(input_path, 'r', encoding='utf-8')
    title = (input_file.readline()[:-1])
    inner_text = input_file.read()
    input_file.close()

    words_dict = defaultdict(list)
    for w in title.split(' '):
        if w != '':
            words_dict[w.lower()].append(0) # В title

    count_skiped = 0
    for pos, w in enumerate(inner_text.split(' ')):
        if w == '':
            count_skiped += 1
            continue
        words_dict[w.lower()].append(pos+1-count_skiped)

    WriteWordsToFile(output_path, words_dict)

def GetFilesStatistics(input_dir, out_dir, filenames, skip_if_exist=True):
    for name in filenames:
        FileStatistics(input_dir+"/"+name, out_dir+"/"+name, skip_if_exist)


class LemmInfo:
    def __init__(self):
        self.count_documents = 0
        self.count_in_corpus = 0

# Записывает информацию для idf в формате
# <лемма> <число содерж. документов> <число вхождений в коллекцию> (x N)
# <общее число лемм в коллекции>
def MakeCorpusStatistics(input_dir, out_filename, filenames):
    corpus_dict = defaultdict(LemmInfo)

    for name in filenames:
        file = open(input_dir+"/"+name, 'r', encoding='utf-8')
        words_info = file.read().splitlines()[:-1] # Т.к. последняя - общее число слов в документе
        for info in words_info: # Слова уникальны (dict)
            info = info.split('\t')
            word = info[0]
            corpus_dict[word].count_in_corpus += int(info[1])
            corpus_dict[word].count_documents += 1
        file.close()

    out_file = open(out_filename, 'w', encoding='utf-8')
    corpus_size = 0
    for w, info in corpus_dict.items():
        out_file.write(w+"\t"+str(info.count_documents)+"\t"+str(info.count_in_corpus)+"\n")
        corpus_size += info.count_in_corpus
    out_file.write(str(corpus_size))
    out_file.close()