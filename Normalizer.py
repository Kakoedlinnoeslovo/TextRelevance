# -*- coding: utf-8 -*-

import numpy as np
import subprocess
import os
import re

import Stemmer
from bs4 import BeautifulSoup

STEMMER = 'yandex' #pystem, yandex, nostem

EXTRACT_DIGITS = re.compile("(\d+)")
NOT_DIGIT_OR_LETTER = re.compile("\W+")
BS_COMMENT = re.compile('<!--.*-->')

# Предварительно нормализует текст
def FirstReplaces(text, preserve_tabs=False):
    text = text.replace("-\n", "") # Склейка переносов
    text = re.sub(NOT_DIGIT_OR_LETTER, r' ', text) # Удаляем все небуквенные и нециферные символы
    text = ' '.join(re.split(EXTRACT_DIGITS, text)) # Разделяем цифры со словами
    return text

def YandexStemming(text, preserve_tabs=False):
    text_hash = str(np.abs(hash(text)))

    # Сохраняем текст в файл, вызываем стеммер
    input = open(text_hash+".in", 'w', encoding="utf-8")
    input.write(text)
    input.close()
    subprocess.call(["mystem.exe", "-ldc", text_hash+".in", text_hash+".out"])

    # Читаем текст из выходного файла, удаляем все лишние символы
    output = open(text_hash+".out", 'r', encoding='utf-8')
    text_out = output.read()
    stemmer_en = Stemmer.Stemmer('english') # Стемминг английского на всякий случай
    text_out = re.sub(NOT_DIGIT_OR_LETTER, r' ', text_out) # Удаляем все небуквенные и нециферные символы
    text_out = stemmer_en.stemWords(text_out.split(" "))
    output.close()

    # Удаляем лишние файлы
    os.remove(text_hash+".in")
    os.remove(text_hash+".out")
    return " ".join(text_out)

def PystemStemming(text):
    stemmer_rus = Stemmer.Stemmer('russian')
    stemmer_en = Stemmer.Stemmer('english')
    words = text.split(" ")
    words_out = stemmer_en.stemWords(stemmer_rus.stemWords(words))
    return " ".join(words_out)

def BSSteming(text):
    soup = BeautifulSoup(text)
    data = soup.find_all(text=True)

    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match(BS_COMMENT, str(element.encode('utf-8'))):
            return False
        return True

    result = filter(visible, data)
    return result

# Нормализует текст с помощью стеминга
def Steming(text):
    if STEMMER == 'yandex':
        return YandexStemming(text)
    if STEMMER == 'pystem':
        return PystemStemming(text)
    if STEMMER == 'bs':
        return BSSteming(text)
    if STEMMER == 'nostem':
        return text

# Окончательно нормализует слово
def SecondaryReplaces(word):
    word = word.replace(u'ё', u'е')
    word = word.replace('_', '')
    word = word.strip()
    return word
