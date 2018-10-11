# -*- coding: utf-8 -*-

import numpy as np
from multiprocessing import Pool
from Parse import CleanFiles, EXTRACTOR
from TF_IDF import GetFilesStatistics, MakeCorpusStatistics
from Normalizer import STEMMER

N_WORKERS = 8
SKIP_EXIST = True

DATADIR = "data/"
URLS_FILE = "urls.numerate.txt"
FILELIST_PREFIX = "filelist_"

N_URLS = 38114
DATA_INDICES_STR = [str(i) for i in range(1, N_URLS+1)]
TEST_INDICES_STR = ['15909', '1744', '17608', '32198', '5715']

DOCUMENTSDIR_SUFFIX = '_work/'
MODE = 'data' #data или test
CONTENT_DIR = 'content'
PARSED_DIR = 'parse_'
TF_DIR = 'tf_'
CORPUS_STAT_FILENAME_PREFIX = 'corpus_stat_'
CORPUS_STAT_FILENAME_EXT = '.dat'

def GetFilestringsSplit(filenames, n_workers=N_WORKERS):
    splits = np.linspace(0, len(filenames), n_workers+1, dtype=np.int)
    return [filenames[splits[i] : splits[i+1]] for i in range(n_workers)]

# args_array - массив из tuple аргументов, передается в starmap
def StartInPool(func, args_array, n_workers=N_WORKERS):
    proc_pool = Pool(n_workers)
    proc_pool.starmap(func, args_array)
    proc_pool.close()

def Parse(skip_exist=True):
    # Открываем файл со списком url
    urls_file = open(DATADIR+URLS_FILE, 'r', encoding="utf8")
    urls_parts = [line.split('\t') for line in urls_file.read().splitlines()]
    urls = dict((url[1], url[0]) for url in urls_parts)
    urls_file.close()

    # Запускаем обработку файлов
    file_vs_names = open(DATADIR+FILELIST_PREFIX+MODE+".txt", 'r', encoding="utf-8")
    filenames = file_vs_names.read().splitlines()
    file_vs_names.close()
    filenames_splits = GetFilestringsSplit(filenames)
    StartInPool(CleanFiles, [(urls, MODE+DOCUMENTSDIR_SUFFIX+CONTENT_DIR, \
                              MODE+DOCUMENTSDIR_SUFFIX+PARSED_DIR+EXTRACTOR+"_"+STEMMER, filenames_splits[i],
                              SKIP_EXIST) \
                             for i in range(N_WORKERS)])

def TF(skip_exist=True):
    if MODE == 'data':
        filenames_splits = GetFilestringsSplit(DATA_INDICES_STR)
    if MODE == 'test':
        filenames_splits = GetFilestringsSplit(TEST_INDICES_STR)
    StartInPool(GetFilesStatistics, [(MODE+DOCUMENTSDIR_SUFFIX+PARSED_DIR+EXTRACTOR+"_"+STEMMER, \
                                      MODE+DOCUMENTSDIR_SUFFIX+TF_DIR+EXTRACTOR+"_"+STEMMER, filenames_splits[i],
                                      SKIP_EXIST) \
                                     for i in range(N_WORKERS)])

def ProcessFiles():
    Parse()
    TF()

    indices = DATA_INDICES_STR if MODE == 'data' else TEST_INDICES_STR
    MakeCorpusStatistics(MODE+DOCUMENTSDIR_SUFFIX+TF_DIR+EXTRACTOR+"_"+STEMMER,
                         MODE+DOCUMENTSDIR_SUFFIX+CORPUS_STAT_FILENAME_PREFIX+EXTRACTOR+"_"+STEMMER+
                         CORPUS_STAT_FILENAME_EXT,
                         indices)

if __name__ == '__main__':
    ProcessFiles()
