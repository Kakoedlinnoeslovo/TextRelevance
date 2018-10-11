# -*- coding: utf-8 -*-

import numpy as np
from collections import defaultdict

from Main_files import MODE, DOCUMENTSDIR_SUFFIX, TF_DIR, N_URLS
from Normalizer import STEMMER
from Parse import  EXTRACTOR

CONSTANT_IDF = 1.5

COEFFICIENT_BASE_WORDS = 1.0
COEFFICIENT_SYNONIMS_WORDS = 0.3
K1 = 1.0
K2 = 1.0 / 1000
CONSTANT_FORMAT = 1.0
WEIGHT_FOR_TITLE = 0.5

COEFFICIENT_PAIRS = 0.3
WEIGHT_FOR_ROW = 1.5
WEIGHT_FOR_INVERSE = 0.7
WEIGHT_FOR_SKIP2 = 0.5
WEIGHT_FOR_SKIP_IN_QUERY = 0.1

COEFFICIENT_INCLUDE_ALL_WORDS = 0.2
MISS_PENALTY = 0.03

def GetWordsIDF(words, corpus_len, corpus_info):
    result = []
    for w in words:
        if corpus_info[w].count_in_corpus != 0:
            #result.append(-np.log(1 - np.exp(-CONSTANT_IDF * corpus_info[w].count_in_corpus / N_URLS)))
            result.append(-np.log(corpus_info[w].count_in_corpus / corpus_len))
        else:
            print("No word: "+w)
            result.append(0.0)
    return result

def GetQueryDocumensWordsIDF(words, documents_info):
    result = []
    for w in words:
        word_count = 0
        for document_dict in documents_info:
            if len(document_dict[w]) != 0:
                word_count += 1
        if word_count != 0:
            result.append(-np.log(word_count / len(documents_info)))
        else:
            result.append(0.0)
    return result

# Возвращает словарь(слово - список вхождений), размер документа
def ParseTFDocument(url_id):
    document_dict = defaultdict(list)
    doc_file = open(MODE+DOCUMENTSDIR_SUFFIX+TF_DIR+EXTRACTOR+"_"+STEMMER+"/"+str(url_id), 'r', encoding='utf-8')
    doc_lines = doc_file.read().splitlines()
    for line in doc_lines[:-1]:
        line_parts = line.split('\t')
        document_dict[line_parts[0]] = [int(i) for i in line_parts[2].split(" ")]
    doclen = int(doc_lines[-1])
    doc_file.close()
    return document_dict, doclen

def SingleWordScore(word, word_idf, document_dict, document_len):
    tf = len(document_dict[word])
    score1 = tf / (tf + K1 + K2 * document_len)
    score2 = WEIGHT_FOR_TITLE if (0 in document_dict[word]) else 0
    return word_idf*(score1 + CONSTANT_FORMAT*score2)

def GetPairCount(w1, w2, positions1, positions2):
    count_row = 0
    count_inverse = 0
    count_skip2 = 0
    for p1 in positions1:
        if (p1+1) in positions2:
            count_row += 1
        if (p1-1) in positions2:
            count_inverse += 1
        if (p1+2) in positions2:
            count_skip2 += 1
    return count_row, count_inverse, count_skip2

def CountMiss(words, words_idf, document_info, median_idf):
    count_miss = 0
    for word_id, w in enumerate(words):
        if len(document_info[w]) == 0 and (words_idf[word_id] > median_idf):
            count_miss += 1
    return count_miss

def ScoreWords(words, words_idf, document_dict, document_len):
    score = 0
    for word_id, w in enumerate(words):
        score += SingleWordScore(w, words_idf[word_id], document_dict, document_len)
    return score

def ScoreIncludeAllWords(words, words_idf, document_dict, median_idf):
    score = 0
    for word_id in range(len(words)):
        score += words_idf[word_id]
    score *= MISS_PENALTY ** (CountMiss(words, words_idf, document_dict, median_idf))
    return score

def ScoreQueryPairs(words, words_idf, document_dict):
    score = 0
    for i in range(len(words)-1):
       count_row, count_inverse, count_skip2 = GetPairCount(words[i], words[i+1], document_dict[words[i]],
                                                            document_dict[words[i+1]])
       pair_tf = count_row*WEIGHT_FOR_ROW + count_inverse*WEIGHT_FOR_INVERSE + count_skip2*WEIGHT_FOR_SKIP2
       score += (words_idf[i] + words_idf[i+1]) * (pair_tf) / (1 + pair_tf)
    return score

# Возвращает набор scores, соотвествтующий порядку документов в query_info
def ScoreQuery(query_info, corpus_len, corpus_info, median_idf):
    #global K2
    #K2 = float(N_URLS) / corpus_len
    #print(K2)
    documents_data = [ParseTFDocument(doc_id) for doc_id in query_info.doc_indices]
    documents_info = [documents_data[i][0] for i in range(len(documents_data))]
    base_words_idf = GetWordsIDF(query_info.words_base, corpus_len, corpus_info)
    extend_words_idf = GetWordsIDF(query_info.words_extend, corpus_len, corpus_info)
#    base_words_idf = GetQueryDocumensWordsIDF(query_info.words_base, documents_info)
#    extend_words_idf = GetQueryDocumensWordsIDF(query_info.words_extend, documents_info)
    #print(base_words_idf, extend_words_idf)

    results = []
    for doc_index in range(len(query_info.doc_indices)):
        results.append(COEFFICIENT_BASE_WORDS * ScoreWords(query_info.words_base, base_words_idf,
                                                           *documents_data[doc_index]) + \
                       COEFFICIENT_SYNONIMS_WORDS * ScoreWords(query_info.words_extend, extend_words_idf,
                                                               *documents_data[doc_index]) + \
                       COEFFICIENT_BASE_WORDS * COEFFICIENT_PAIRS * \
                                    ScoreQueryPairs(query_info.words_base, base_words_idf, documents_info[doc_index]) + \
                       COEFFICIENT_SYNONIMS_WORDS * COEFFICIENT_PAIRS * \
                                    ScoreQueryPairs(query_info.words_extend, extend_words_idf, documents_info[doc_index]) + \
                       COEFFICIENT_INCLUDE_ALL_WORDS * ScoreIncludeAllWords(query_info.words_base, base_words_idf,
                                                                            documents_info[doc_index], median_idf))
#        print(doc_id, COEFFICIENT_BASE_WORDS * ScoreWords(query_info.words_base, base_words_idf,
#                                                           document_dict, document_len),
#                       COEFFICIENT_SYNONIMS_WORDS * ScoreWords(query_info.words_extend, extend_words_idf,
#                                                               document_dict, document_len),
#                       COEFFICIENT_BASE_WORDS * COEFFICIENT_PAIRS * \
#                                    ScoreQueryPairs(query_info.words_base, base_words_idf, document_dict),
#                       COEFFICIENT_SYNONIMS_WORDS * COEFFICIENT_PAIRS * \
#                                    ScoreQueryPairs(query_info.words_extend, extend_words_idf, document_dict),
#                       COEFFICIENT_INCLUDE_ALL_WORDS * ScoreIncludeAllWords(query_info.words_base, base_words_idf,
#                                                                            document_dict, median_idf))
    return results