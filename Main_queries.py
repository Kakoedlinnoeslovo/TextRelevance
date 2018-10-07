# -*- coding: utf-8 -*-

import numpy as np
from collections import defaultdict
import os

from TF_IDF import LemmInfo
from Main_files import DATADIR, DOCUMENTSDIR_SUFFIX, MODE, \
                       CORPUS_STAT_FILENAME_PREFIX, CORPUS_STAT_FILENAME_EXT
from Normalizer import STEMMER, FirstReplaces, SecondaryReplaces, Steming
from Scorer import ScoreQuery, GetWordsIDF

# Формат: номер\tтекст запроса\tпереформулировки
QUERIES_FILENAME = 'queries.numerate_review.txt'
SAMPLE_SUBMISSION_FILENAME = 'sample.submission.txt'
OUTPUT_NAME = 'submissions/out.submission.txt'+STEMMER+'-1'

def RemoveEmptyWords(words_list):
    result = []
    for w in words_list:
        if w != '':
            result.append(w)
    return result

def SplitWords(text):
    words = Steming(FirstReplaces(text)).split(" ")
    return [SecondaryReplaces(w).lower() for w in words]

# Возвращает corpus_dict (слово - LemmInfo), общая длина корпуса
def LoadCorpusInfo():
    corpus_dict = defaultdict(LemmInfo)
    corpus_file = open(MODE+DOCUMENTSDIR_SUFFIX+CORPUS_STAT_FILENAME_PREFIX+STEMMER+CORPUS_STAT_FILENAME_EXT,
                       'r', encoding='utf-8')
    corpus_lines = corpus_file.read().splitlines()
    for line in corpus_lines[:-1]:
        line = line.split('\t')
        corpus_dict[line[0]].count_documents = int(line[1])
        corpus_dict[line[0]].count_in_corpus = int(line[2])
    corpus_size = int(corpus_lines[-1])
    corpus_file.close()
    return corpus_dict, corpus_size

class QueryInfo:
    def __init__(self):
        self.doc_indices = []
        self.words_base = ''
        self.words_extend = ''

def LoadQueries(load_if_exists=True):
    queries_dict = defaultdict(QueryInfo)

    if (not os.path.exists(DATADIR+QUERIES_FILENAME+"_"+STEMMER)) or (not load_if_exists):
        file_queries = open(DATADIR+QUERIES_FILENAME, 'r', encoding='utf-8')
        out_stemming = open(DATADIR+QUERIES_FILENAME+"_"+STEMMER, 'w', encoding='utf-8')
        queries_strs = file_queries.read()[1:].splitlines()
        for query_str in queries_strs:
            parts = query_str.split('\t')
            query_id = int(parts[0])
            out_stemming.write(str(query_id)+"\t")
            queries_dict[query_id].words_base = RemoveEmptyWords(SplitWords(parts[1]))
            out_stemming.write(' '.join(queries_dict[query_id].words_base)+"\t")
            if len(parts) > 2:
                queries_dict[query_id].words_extend = RemoveEmptyWords(SplitWords(parts[2]))
            out_stemming.write(' '.join(queries_dict[query_id].words_extend))
            out_stemming.write('\n')
            print(query_id)
            out_stemming.flush()
        file_queries.close()
        out_stemming.close()
    else:
        file_queries = open(DATADIR+QUERIES_FILENAME+"_"+STEMMER, 'r', encoding='utf-8')
        for query_str in file_queries.read().splitlines():
            if query_str == '':
                continue
            parts = query_str.split('\t')
            query_id = int(parts[0])
            queries_dict[query_id].words_base = RemoveEmptyWords(parts[1].split(' '))
            queries_dict[query_id].words_extend = RemoveEmptyWords(parts[2].split(' '))
        file_queries.close()

    file_submission = open(DATADIR+SAMPLE_SUBMISSION_FILENAME, 'r', encoding='utf-8')
    lines = file_submission.read().splitlines()[1:] #Первая строка - заголовок
    for l in lines:
        parts = l.split(",")
        queries_dict[int(parts[0])].doc_indices.append(int(parts[1]))
    file_submission.close()
    return queries_dict

if __name__ == '__main__':
    corpus_info, corpus_len = LoadCorpusInfo()
    median_idf = np.median(GetWordsIDF(corpus_info.keys(), corpus_len, corpus_info))
    queries_dict = LoadQueries()

    out_file = open(OUTPUT_NAME, 'w')
    out_file.write("QueryId,DocumentId\n")
    for query_id, query_info in queries_dict.items():
        scores = -np.array(ScoreQuery(query_info, corpus_len, corpus_info, median_idf))
        print(query_id, scores[:5])
        argsort = np.argsort(scores)
        for doc_pos in argsort:
            out_file.write(str(query_id)+","+str(query_info.doc_indices[doc_pos])+"\n")
        out_file.flush()
    out_file.close()