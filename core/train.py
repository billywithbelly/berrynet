# -*- coding: utf-8 -*-

from __future__ import division
import extract
import json
import os
from settings import BASE_DIR
from os import listdir
from os.path import isfile, join
from extract import *
from db.manager import *
from sqlalchemy import func 
from sqlalchemy import and_
from db import models
import operator

import logging
logger = logging.getLogger(__name__)


class Trainer:

    def __init__(self, filename):
        self.filename = filename

    def json(self):
        if not hasattr(self, "_json"):
            _json = []
            texts = {}
            with open(self.filename, "r") as f:
                texts = json.load(f)
            for text in texts:
                author = text["Author"]
                title = text["Title"]
                period = text["Period"]
                url = text["URL"]
                _json.append((author, title, period, url))
        return _json

    def get_books(self):
        """
        Gets the book if it is not in the texts folder otherwise dowload it
        """
        files = [ f for f in listdir(TEXTS_FOLDER) if isfile(join(TEXTS_FOLDER,f)) ]
        for author, title, period, url in self.json():
            filename = format_filename(author, title)
            try:
                if not filename in files:
                    book = extract.get_text(url, False, author, title, period)
            except:
                #TODO : ERROR 403
                os.remove(os.path.join(TEXTS_FOLDER, format_filename(author, title)))
                pass

    def train(self):
        logger.debug("      STARTING get_books")
        self.get_books()
        logger.debug("      STARTING populate")
        self.populate()
        logger.debug("      STARTING categories")
        self.categories()
        logger.debug("      STARTING conditional_probability")
        self.conditional_probability()

    def populate(self):
        output = []
        for author, title, period, url in self.json():
            words = read_text(os.path.join(TEXTS_FOLDER, format_filename(author, title)))
            if len(words) == 0:
                continue
            total_words = reduce(operator.add, words.values())
            #insert period
            dic_period = {'name':period}
            list_search = ['name']
            period_obj = get_or_insert(dict_val=dic_period,
                instance=models.Period, list_search=list_search)
            #insert book
            # logger.debug(words)
            logger.debug("Total Words: %s", total_words)
            dic_book = {'name':title,
                'author':author,
                'period':period_obj,
                'total_words':total_words,
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
            insert_words(words,book_obj,total_words)

    def categories(self):
        words_all = get({},Word,[],True)
        total = len(words_all)
        for word_obj in words_all:
            self.calculate_categories(word_obj=word_obj)
            total -= 1
            if total % 500 ==0:
                logger.debug("Progressing Word -- Category... %s" % total)
        session.commit()

    def calculate_categories(self, word_obj=None):
        if not word_obj:
            return False
        max_rate, min_rate = get_max_min_rate(word_obj)
        construct_categories(min_rate,max_rate, word_obj)


    def period_probability(self, period, log=False):
        """
        # libros de esa epoca
        ---
        # total de libros
        """
        books_period = session.query(Book).filter_by(period=period).count()
        if log:
            logger.debug("      books_period = %f " % (books_period))
        return books_period


    def word_category_period_probability(self, word, category, period, log=False):
        """
        cuenta cuantos (libros de esa epoca) tienen esa palabra en esa categoria
        ---
        numero de libros de esa epoca
        """
        num_books__word_cat = 0
        books_period = session.query(Book).filter_by(period=period).all()
        for book in books_period:
            #el libro contiene la palabra
            book_word = session.query(WordCount).filter_by(
                book=book,word=word).all()
            word_category = session.query(WordCategory).filter_by(
                category=category,word=word).one()
            
            #if len(book_word)==0, no relation then prob 0 
            if len(book_word) > 0 and word_category:
                if book_word[0].rate >= word_category.min_range and book_word[0].rate < word_category.max_range:
                    num_books__word_cat += 1
        if log:
            logger.debug("      num_books__word_cat= %f" % (num_books__word_cat))

        return num_books__word_cat

    def probability(self, word, category, period, log=False):
        """
        probabilidad esa palabra en esa categoria en esa epoca
        ---
        probabilidad de esa epoca = # libros de esa epoca / cantidad de libros
        """
        word_category_period_probability = self.word_category_period_probability(word, category, period, log=log)
        period_probability = self.period_probability(period, log=log)
        if log:
            logger.debug("  word cat period prob = %f / period prob = %f = %f" % (word_category_period_probability,period_probability,word_category_period_probability/period_probability))
        return word_category_period_probability/period_probability


    def conditional_probability(self):
        """
        """
        session.query(WordConditionalProbability).delete()
        bulk = []
        words_all = session.query(Word).all()
        periods = session.query(Period).all()
        categories = session.query(Category).all()
        for period in periods:
            logger.debug(period.name)
            for category in categories:
                logger.debug(category.description)
                total = len(words_all)
                for word in words_all:
                    #word rate?
                    prob = self.probability(
                        word=word,
                        category=category,
                        period=period)
                    if prob > 1:
                        logger.debug("word %s category %s  period %s prob %s" % (word.text,category.description, period.name, prob))
                        self.probability(word=word,category=category,period=period, log=True)
                    word_cond_prob = WordConditionalProbability(
                        word=word,
                        category=category,
                        period=period,
                        probability=prob)
                    bulk.append(word_cond_prob)
                    total -= 1
                    if total % 500 == 0:
                        logger.debug("left ... %s words" % total)
        session.add_all(bulk)
        session.commit()
        self.complete_probability()

    def complete_probability(self):
        bulk = []
        list_cat = ['med','high','high_high']
        cats_ids = session.query(Category).filter(Category.description.in_(list_cat)).all()
        low = session.query(Category).filter(Category.description=='low').one()

        words_all = session.query(Word).all()
        periods = session.query(Period).all()
        for period in periods:
            total = len(words_all)
            for word in words_all:
                sum_3cat = session.query(
                    func.sum(WordConditionalProbability.probability)).filter(
                        and_(WordConditionalProbability.id_category.in_(c.id for c in cats_ids),
                            WordConditionalProbability.id_word == word.id,
                            WordConditionalProbability.id_period == period.id)
                    ).all()[0][0]
                cat_low = session.query(WordConditionalProbability).filter(
                        and_(WordConditionalProbability.id_category == low.id,
                            WordConditionalProbability.id_word == word.id,
                            WordConditionalProbability.id_period == period.id)
                    ).all()
                cat_low[0].probability = 1 - sum_3cat
                # print "word_id %s period %d sum %s" %(word.id,period.id,sum_3cat)
                total -= 1
                if total % 500 == 0:
                    logger.debug("left ... %s words" % total)
        session.commit()

