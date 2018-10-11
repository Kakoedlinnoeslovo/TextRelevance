# -*- coding: utf-8 -*2

import re
import os
from inscriptis import get_text
from bs4 import BeautifulSoup

from Normalizer import Steming, FirstReplaces, SecondaryReplaces

# Строка, временно разделяющая в файле 1го парсинга заголовок и основной текст
TITLE_SPLITER = 'TITLETITLETTTTIIIIITTTLLLEE'
EXTRACT_TITLE = re.compile('<title>(.*?)<\/title>', re.DOTALL)

EXTRACTOR = 'bs' # inscriptis или bs (beautiful soup)
BS_COMMENT = re.compile('<!---.*--->', re.DOTALL)

# Принимает на вход текст, возвращает слова из него
def ExtractText(text):
    text = FirstReplaces(text)
    text = Steming(text)

    result_words = []
    for w in text.split(" "):
        w = SecondaryReplaces(w)
        if w != '':
            result_words.append(w)
    return result_words

def InscriptisDecoder(text):
    return get_text(text)

def BSDecoder(text):
    soup = BeautifulSoup(text)
    data = soup.findAll(text=True)

    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match(BS_COMMENT, str(element.encode('utf-8'))):
            return False
        return True

    result = filter(visible, data)
    return " ".join(result)

def DecodeHTML(text):
    if EXTRACTOR == 'inscriptis':
        return InscriptisDecoder(text)
    if EXTRACTOR == 'bs':
        return BSDecoder(text)

def ParseFile(text, out_name, skip_exist=True):
    if os.path.exists(out_name) and skip_exist:
        return

    # Выделяем заголовок и текст
    title_search = re.search(EXTRACT_TITLE, text)
    if title_search is not None:
        title = title_search.groups()[0]
    else:
        title = ''
    # Добавляем пробелы, чтобы слова не склеивались
    text = text.replace("<", " <").replace(">", "> ")
    inner_text = get_text(text)
    out_text = ' '.join(ExtractText(title + " " + TITLE_SPLITER + " " + inner_text))
    out_title, out_inner = out_text.split(TITLE_SPLITER)

    out_file = open(out_name, 'w', encoding='utf-8')
    out_file.write(out_title+"\n")
    out_file.write(out_inner)
    out_file.close()

def CleanFiles(url_nums, source_dir, out_dir, filenames, bad_encoding_filename,
               skip_exist=True):
    for name in filenames:
        f = open(source_dir+"/"+name, "r", encoding="utf-8", errors='replace')
        url = f.readline()[:-1]
        text = f.read().lower()
        ParseFile(text, out_dir+"/"+str(url_nums[url]), skip_exist)
