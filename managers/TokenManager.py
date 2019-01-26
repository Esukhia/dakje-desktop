import os

import pybo

from pathlib import Path

from widgets import Matchers
from storage.models import Rule
from storage.models import Token as TokenModel
from .ViewManager import ViewManager
from storage.settings import BASE_DIR


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
    def __init__(self, token, id=None):
        self.id = id  # have no id before save to database

        self.pyboToken = token
        self.content = token.content
        self.pos = token.pos
        self.lemma = token.lemma

        self.start = token.start
        self.end = self.start + len(token.content)
        self.string = None

        self.level = None
        self.meaning = None

    def applyTokenModel(self, tokenModel):
        self.pos = tokenModel.pos if tokenModel.pos else self.pos
        self.lemma = tokenModel.lemma if tokenModel.lemma else self.lemma
        self.level = tokenModel.level if tokenModel.level else self.level
        self.meaning = tokenModel.meaning if tokenModel.meaning else self.meaning

    @property
    def length(self):
        return self.end - self.start

    @property
    def contentWithoutTsek(self):
        return self.content[:-1] if self.content.endswith('་') else self.content


class TokenManager:
    TRIE_ADD_TEMP_FILE = os.path.join(BASE_DIR, 'TrieAddTempFile.txt')
    TRIE_DEL_TEMP_FILE = os.path.join(BASE_DIR, 'TrieDelTempFile.txt')

    def __init__(self, editor):
        self.editor = editor
        self.lang = "bo"
        self.mode = "default"
        self.tagger = None
        self.matcher = Matchers.PyKnowRuleMatcher()

        with open(self.TRIE_ADD_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join([
                '{} {}'.format(d.content, d.pos)
                for d in TokenModel.objects.filter(
                    type=TokenModel.TYPE_UPDATE) if d.pos is not None
            ]))

        with open(self.TRIE_DEL_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join([
                '{} {}'.format(d.content, d.pos)
                for d in TokenModel.objects.filter(
                    type=TokenModel.TYPE_REMOVE) if d.pos is not None
            ]))

        self.tokenizer = pybo.BoTokenizer(
            'POS',
            toadd_filenames=[Path(self.TRIE_ADD_TEMP_FILE)],
            todel_filenames=[Path(self.TRIE_DEL_TEMP_FILE)]
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
            result = ''
            for i, token in enumerate(tokens):
                token.start = len(result)
                result += (toStr(token) + sep if i != len(tokens) - 1
                           else toStr(token))
                token.end = len(result)
            return result

        if self.view == ViewManager.PLAIN_TEXT_VIEW:
            return _join(self.tokens, lambda t: t.content, sep='')

        elif self.view == ViewManager.SPACE_VIEW:
            return _join(self.tokens, lambda t: t.content, sep=' ')

        elif self.view == ViewManager.TAG_VIEW:
            return _join(self.tokens, lambda t: t.content + '/' + t.pos, sep='')
        else:
            return _join(self.tokens, lambda t: t.content + '/' + t.pos, sep=' ')

    def find(self, position):
        for i, token in enumerate(self.tokens):
            if position in range(token.start, token.end):
                return (i, token)

    @timed
    def matchRules(self):
        rules = Rule.objects.all()
        self.matcher.match(self.tokens, rules)

    @timed
    def applyDict(self):
        tokenModels = TokenModel.objects.filter(
            type=TokenModel.TYPE_UPDATE)

        tokenDict = {
            tokenModel.content: tokenModel for tokenModel in tokenModels}

        for token in self.tokens:
            tokenModel = tokenDict.get(token.content)

            if tokenModel is None:
                tokenModel = tokenDict.get(token.contentWithoutTsek)

            if tokenModel is not None:
                token.applyTokenModel(tokenModel)
