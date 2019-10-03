import os

# import pybo
import pybo

from pathlib import Path

from widgets import Matchers
from storage.models import Rule
from storage.models import Token as TokenModel
from .ViewManager import ViewManager
from web.settings import BASE_DIR


import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Timed decorator
def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(
            func.__name__, round(end - start, 5)))
        return result
    return wrapper


class Token:
    """
    A class used to represent token objects
    (pybo token attributes + custom attributes)
    """
    def __init__(self, token, id=None):

        # copy all token attributes from pybo tokens
        self.__dict__ = token.__dict__.copy()

        self.id = id  # have no id before save to database

        self.blockIndex = None
        self.end = self.start + len(self.text)
        self.string = None

        self.level = None
        self.meaning = None

    def applyTokenModel(self, tokenModel):
        # add attributes from the DB
        self.pos = tokenModel.pos if tokenModel.pos else self.pos
        self.lemma = tokenModel.lemma if tokenModel.lemma else self.lemma
        self.level = tokenModel.level if tokenModel.level else self.level
        self.meaning = tokenModel.meaning if tokenModel.meaning else self.meaning

    @property
    def length(self):
        return self.end - self.start

    @property
    def textWithoutTsek(self):
        return self.text[:-1] if self.text.endswith('་') else self.text


class TokenManager:
    TRIE_MODIF_DIR = os.path.join(BASE_DIR, 'resources', 'dictionaries')
    if not os.path.exists(TRIE_MODIF_DIR):
        os.makedirs(TRIE_MODIF_DIR)

    TRIE_ADD_DIR = os.path.join(TRIE_MODIF_DIR, 'lexica_bo')
    if not os.path.exists(TRIE_ADD_DIR):
        os.makedirs(TRIE_ADD_DIR)

    TRIE_DEL_DIR = os.path.join(TRIE_MODIF_DIR, 'deactivate')
    if not os.path.exists(TRIE_DEL_DIR):
        os.makedirs(TRIE_DEL_DIR)

    TRIE_ADD_TEMP_FILE = os.path.join(TRIE_ADD_DIR, 'TrieAddTempFile.txt')
    TRIE_DEL_TEMP_FILE = os.path.join(TRIE_DEL_DIR, 'TrieDelTempFile.txt')

    def __init__(self, editor):
        self.editor = editor
        self.lang = "bo"
        self.mode = "default"
        self.tagger = None
        self.matcher = Matchers.expertaRuleMatcher()

        with open(self.TRIE_ADD_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join([
                '{} {}'.format(d.text, d.pos)
                for d in TokenModel.objects.filter(
                    type=TokenModel.TYPE_UPDATE) if d.pos is not None
            ]))

        with open(self.TRIE_DEL_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join([
                '{} {}'.format(d.text, d.pos)
                for d in TokenModel.objects.filter(
                    type=TokenModel.TYPE_REMOVE) if d.pos is not None
            ]))

        # This should be using pybo instead:
        # self.tokenizer = pybo.WordTokenizer(
        #   'POS',
        #   tok_modifs = self.TRIE_ADD_TEMP_FILE)
        ### note: the directory should contain at least two subfolders:
        # lexica_bo: a dir containing files with words, a word per line
        # lexica_skrt: same, but for sanskrit entries
        # deactivate: same, but for the entries to deactivate from the trie
        self.tokenizer = pybo.WordTokenizer(
            'POS',
            tok_modifs= self.TRIE_MODIF_DIR
        )

        # os.remove(self.TRIE_ADD_TEMP_FILE)
        # os.remove(self.TRIE_DEL_TEMP_FILE)

        # print(self.tokenizer.tok.trie.has_word("abc"))

    @property
    def view(self):
        return self.editor.view

    @property
    def tokens(self):
        return self.editor.tokens

    @timed
    def segment(self, sentence):
        tokens = self.tokenizer.tokenize(sentence)
        return [Token(t) for t in tokens]

    def getString(self):
        def _join(tokens, toStr, sep):
            blockIndex = 0
            result = ''
            for i, token in enumerate(tokens):
                token.blockIndex = blockIndex
                token.start = len(result)
                result += (toStr(token) + sep if i != len(tokens) - 1
                           else toStr(token))
                token.end = len(result)

                if token.text.endswith('\n'):
                    blockIndex += 1
            return result

        if self.view == ViewManager.PLAIN_TEXT_VIEW:
            return _join(self.tokens, lambda t: t.text, sep='')

        elif self.view == ViewManager.SPACE_VIEW:
            return _join(self.tokens, lambda t: t.text, sep=' ')

        elif self.view == ViewManager.TAG_VIEW:
            return _join(self.tokens, lambda t: t.text + '/' + t.pos, sep='')
        else:
            return _join(self.tokens, lambda t: t.text + '/' + t.pos, sep=' ')

    def find(self, position):
        for i, token in enumerate(self.tokens):
            if position in range(token.start, token.end):
                return i, token

    def findByBlockIndex(self, blockIndex):
        startIndex, endIndex = None, None
        for i, token in enumerate(self.tokens):
            if startIndex is None:
                if token.blockIndex == blockIndex:
                    startIndex = i
                    endIndex = i
            elif token.blockIndex == blockIndex:
                endIndex = i
        return startIndex, endIndex

    @timed
    def matchRules(self):
        rules = Rule.objects.all()
        self.matcher.match(self.tokens, rules)

    @timed
    def applyDict(self):
        tokenModels = TokenModel.objects.filter(
            type=TokenModel.TYPE_UPDATE)

        tokenDict = {
            tokenModel.text: tokenModel for tokenModel in tokenModels}

        for token in self.tokens:
            tokenModel = tokenDict.get(token.text)

            if tokenModel is None:
                tokenModel = tokenDict.get(token.textWithoutTsek)

            if tokenModel is not None:
                token.applyTokenModel(tokenModel)
