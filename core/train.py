# -*- coding: utf-8 -*-

import extract
import json
import os
from settings import BASE_DIR
from os import listdir
from os.path import isfile, join
from extract import *
from db.manager import *
from db import models
import operator


import logging
logger = logging.getLogger(__name__)

def parse_json(filename):
    texts = {}
    with open(filename, "r") as f:
        texts = json.load(f)
    for text in texts:
        author = text["Author"]
        title = text["Title"]
        period = text["Period"]
        url = text["URL"]
        yield author, title, period, url

def get_books(filename):
    """
    Gets the book if it is not in the texts folder otherwise dowload it
    """
    files = [ f for f in listdir(TEXTS_FOLDER) if isfile(join(TEXTS_FOLDER,f)) ]
    for author, title, period, url in parse_json(filename):
        try:
            if not format_filename(author, title) in files:
                book = extract.get_text(url, False, author, title, period, files)
        except:
            #TODO : ERROR 403
            pass

#TODO
def inspect(filename):
    """
    Check if the file is just text or an html page (if html then delete)
    """
    pass


def train(filename):
    get_books(filename)
    populate(filename)



def populate(filename):
    output = []
    for author, title, period, url in parse_json(filename):
        #insert period
        dic_period = {'name':period}
        list_search = ['name']
        period_obj = get_or_insert(dict_val=dic_period,
            instance=models.Period, list_search=list_search)
        #insert book
        words = read_text(filename)
        count = reduce(operator.add, words.values())
        logger.debug(words)
        logger.debug("Total Words: %s", count)
        dic_book = {'name':title,
            'author':author,
            'period':period_obj,
            'total_words':count,
            'sentence_total':0}
        list_search = ['name','author','period']
        book_obj = get_or_insert(dict_val=dic_book,
            instance=models.Book,list_search=list_search)
        #Words
        filename = format_filename(author, title)
        
        if len(words) == 0:
            continue

        logger.debug("Period id : %s %s" % (period_obj.id,period_obj.name))
        logger.debug("Book id : %s %s %s" % (book_obj.id,book_obj.name,book_obj.author))
        insert_words(words,book_obj)
         

if __name__ == "__main__":
    filename = os.path.join(BASE_DIR, "sources.json")
    train(filename)

