#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import wikipedia as wiki
from nltk import tokenize
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions

class SearchRobot():

    def __init__(self):
        self.keywords_list = []
        self.sentences_number = 7

        self.natural_language_understanding = NaturalLanguageUnderstandingV1(
                version = "2018-11-16",
                iam_apikey = "YOUR_API_KEY_HERE",
                url = "YOUR_URL_HERE")

    def search(self, search_term):
        summary = wiki.summary(search_term, sentences = 7)
        summary = re.sub(r"\([^)]*\)", "", summary)

        return tokenize.sent_tokenize(summary)

    def get_keywords(self, sentences):
        for sentence in sentences:
            response = self.natural_language_understanding.analyze(text = sentence,
                    features = Features(
                        keywords = KeywordsOptions(emotion = True, sentiment = True,
                            limit = 2))).get_result()

            temp_list = []
            for keyword in response["keywords"]:
                temp_list.append(keyword["text"])

            self.keywords_list.append(temp_list)

        return self.keywords_list
