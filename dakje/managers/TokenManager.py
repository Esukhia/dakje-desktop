'''





'''

import os

import pybo

from dakje.widgets import Matchers
from dakje.storage.models import Rule
from dakje.storage.models import Token as TokenModel
from .ViewManager import ViewManager
from dakje.web.settings import FILES_DIR


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
        """
        Class building token objects
        (pybo token attributes + custom attributes)
        IMPORTANT: .text_unaffixed should be used for lookups
        .text might include extra tseks
            :param self: 
            :param token: 
            :param id=None: 
        """
        # copy all token attributes from pybo tokens
        self.text = token.text
        self.text_cleaned = token.text_cleaned
        self.text_unaffixed = token.text_unaffixed
        self.lemma = token.lemma
        self.pos = token.pos
        self.start = token.start
        self.type = token.chunk_type
        # self.sense = token.sense # no sense in pybo
        self.level = None
        self.sense = None

        self.id = id  # have no id before save to database

        self.blockIndex = None
        self.end = self.start + len(self.text)
        self.string = None


    def applyTokenModel(self, tokenModel):
        # add attributes from the DB
        self.pos = tokenModel.pos if tokenModel.pos else self.pos
        self.lemma = tokenModel.lemma if tokenModel.lemma else self.lemma
        self.level = tokenModel.level if tokenModel.level else self.level
        self.sense = tokenModel.sense if tokenModel.sense else self.sense

    @property
    def length(self):
        return self.end - self.start

    @property
    def textWithoutTsek(self):
        return self.text_unaffixed[:-1] if self.text_unaffixed.endswith('་') else self.text_unaffixed

class TokenManager:
    # This class runs botok, and gives him custom lists
    TRIE_MODIF_DIR = os.path.join(FILES_DIR, 'words')
    if not os.path.exists(TRIE_MODIF_DIR):
        os.makedirs(TRIE_MODIF_DIR)

    TRIE_ADD_DIR = os.path.join(TRIE_MODIF_DIR, 'lexica_bo')
    if not os.path.exists(TRIE_ADD_DIR):
        os.makedirs(TRIE_ADD_DIR)

    TRIE_DEL_DIR = os.path.join(TRIE_MODIF_DIR, 'deactivate')
    print(TRIE_DEL_DIR)
    if not os.path.exists(TRIE_DEL_DIR):
        os.makedirs(TRIE_DEL_DIR)

    TRIE_ADD_TEMP_FILE = os.path.join(TRIE_ADD_DIR, 'TrieAddTempFile.txt')
    TRIE_DEL_TEMP_FILE = os.path.join(TRIE_DEL_DIR, 'TrieDelTempFile.txt')

    def __init__(self, editor):
        self.editor = editor
        # self.lang = "bo"
        # self.mode = "default"
        # self.tagger = None
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

        # the TRIE_MODIF directory should contain at least two subfolders:
        # lexica_bo: a dir containing files with words, a word per line
        # lexica_skrt: same, but for sanskrit entries
        # deactivate: same, but for the entries to deactivate from the trie
        self.tokenizer = pybo.WordTokenizer(
            'POS',
            tok_modifs= self.TRIE_MODIF_DIR
        )

    @property
    def view(self):
        return self.editor.view

    @property
    def tokens(self):
        return self.editor.tokens

    @timed
    def segment(self, string):
        tokens = self.tokenizer.tokenize(string, spaces_as_punct=True)
        return [Token(t) for t in tokens]

    def getString(self):
        # create display string for textEdit
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
        # filter tokens added to the db 
        tokenModels = TokenModel.objects.filter(
            type=TokenModel.TYPE_UPDATE)
        # import db tokens into tokenDict
        tokenDict = {
            tokenModel.text: tokenModel for tokenModel in tokenModels}

        for token in self.tokens:
            tokenModel = tokenDict.get(token.text_unaffixed)

            if tokenModel is None:
                tokenModel = tokenDict.get(token.textWithoutTsek)

            if tokenModel is not None:
                token.applyTokenModel(tokenModel)
