# -*- coding: utf-8 -*-
import os

from RDRPOSTagger.InitialTagger.InitialTagger4Bo import initializeBoSentence
from .SCRDRlearner.Object import FWObject
from .SCRDRlearner.SCRDRTree import SCRDRTree
from .Utility.Utils import getWordTag, readDictionary


def is_a_tibetan(word):
    def is_tibetan_char(char):
        return (char >= 'ༀ' and char <= '༃') or (char >= 'ཀ' and char <= 'ྼ')\
               or char in ['_', '༄', '༅', '།', '་', '༌', '༑', '༎', '༏', '༐', '༔', 'ᛰ']

    is_tib_word = True
    for char in word:
        if not is_tibetan_char(char):
            is_tib_word = False
    return is_tib_word


class Word:
    def __init__(self, **kwargs):
        self.word = kwargs.get("word", None)
        self.tag = kwargs.get("tag", "OOV")


class RDRPOSTagger(SCRDRTree):
    """
    minimal RDRPOSTagger
    inspired from extRDRPOSTagger.py
    """

    def __init__(self):
        SCRDRTree.__init__(self)

    def tag_raw_sentence(self, raw_line, initial_tagger):
        line = initial_tagger(raw_line)
        sen = []
        wordTags = line.split()
        for i in range(len(wordTags)):
            fw_object = FWObject.getFWObject(wordTags, i)
            word, tag = getWordTag(wordTags[i])
            node = self.findFiredNode(fw_object)
            if node.depth > 0:
                sen.append(Word(word=word, tag=node.conclusion))
            else:  # Fired at root, return initialized tag
                sen.append(Word(word=word, tag=tag))
        return sen

# this variable is global so that it can be accessed by WordManager.getPartOfSpeeches() from outside Tagger class
models = {"bo_default": (os.path.join(os.path.dirname(__file__), "Models", "POS", "Tibetan.RDR"),
                         os.path.join(os.path.dirname(__file__), "Models", "POS", "Tibetan.DICT")),
          "bo_UD": (os.path.join(os.path.dirname(__file__), "Models", "UniPOS", "Tibetan.RDR"),
                    os.path.join(os.path.dirname(__file__), "Models", "UniPOS", "Tibetan.DICT")),
          "bo_segment": (os.path.join(os.path.dirname(__file__), "Models", "SEGMENT", "Tibetan.RDR"),
                         os.path.join(os.path.dirname(__file__), "Models", "SEGMENT", "Tibetan.DICT"))
          }


class Tagger:
    '''
    A RDRPOSTagger access point that has new features:
    - allows for simple access to multiple models by language
    - inclusion of new models is as easy as adding a new element in the models global variable

    - it includes an index mechanism to tag only the words that pass the __to_be_tagged() filter
    - can directly add tags within a list of Word objects (uses the index to keep track of where tags belong)
    - can tag as normal: taking a string as input, outputting a string.
    '''
    def __init__(self, **kwargs):
        self.language = kwargs.get("language", "bo")
        self.text = kwargs.get("text", None)
        self.mode = kwargs.get("mode", None)
        self.RDR = kwargs.get("RDR", RDRPOSTagger())
        self.model = {}
        self.__load_model()
        self.tagger, self.dictionary = self.__prepare_tagger()

    def __load_model(self):
        lang = '{}_{}'.format(self.language, self.mode)

        self.model.update({self.language: {self.mode+'_rdr': models[lang][0],
                                           self.mode+'_dict': models[lang][1]}})

    def __prepare_tagger(self):
        rdr_file = self.model[self.language][self.mode + "_rdr"]
        dict_file = self.model[self.language][self.mode + "_dict"]

        tagger = self.RDR
        tagger.constructSCRDRtreeFromRDRfile(rdr_file)
        dictionary = readDictionary(dict_file)
        return tagger, dictionary

    @staticmethod
    def __to_be_tagged(word):  # add any other condition here
        return is_a_tibetan(word)

    def __index_tokens_to_tag(self, words):
        index = {}
        count = 0
        for word_num, word in enumerate(words):
            if self.__to_be_tagged(word):
                index[count] = word_num
                count += 1
        return index

    def tag_raw_line(self, raw_text, initial_tagger=initializeBoSentence):
        '''

        :param raw_text: input text (words are separated by spaces)
        :param initial_tagger: the initial tagger we want to use. (leave empty for default)
        :return: a string containing the tagged words
        '''
        # generate the list of Word objects
        words = [Word(word=w) for w in raw_text.split()]

        # identify what will be tagged
        index = self.__index_tokens_to_tag([w.word for w in words])

        # tagging
        self.text = ' '.join([words[index[i]].word for i in range(len(index))])
        tagged = self.tagger.tag_raw_sentence(self.text, initial_tagger)
        # reinsert the tags in correct tokens
        for token_num, word in enumerate(tagged):
            words[index[token_num]].tag = word.tag
        return ' '.join(['{}ᚽ{}'.format(w.word, w.tag) for w in words])

    def tag_words(self, words, initial_tagger=initializeBoSentence):
        '''

        :param words: a list of Word objects
        :param initial_tagger: the initial tagger we want to use. (leave empty for default)
        :return: directly adds the tags in the corresponding Word objects
        '''
        # identify what will be tagged
        index = self.__index_tokens_to_tag([w.content for w in words])

        # tagging
        self.text = ' '.join([words[index[i]].content for i in range(len(index))])
        tagged = self.tagger.tag_raw_sentence(self.dictionary, self.text, initial_tagger)

        # reinsert tags in correct tokens
        for token_num, word in enumerate(tagged):
            words[index[token_num]].partOfSpeech = word.tag
