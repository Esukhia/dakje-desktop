import os

import pybo

from pathlib import Path

from widgets import Matchers
from storage.models import Rule, Dict
from .ViewManager import ViewManager
from Configure import BASE_DIR

class Token:
    def __init__(self, token, id=None):
        self.id = id  # have no id before save to database

        self.pyboToken = token
        self.content = token.content
        self.pos = token.pos
        self.lemma = token.lemma

        self.start = None
        self.end = None
        self.string = None

        self.level = None
        self.meaning = None

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
        self.matcher = Matchers.SimpleRuleMatcher()

        with open(self.TRIE_ADD_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join(['{} {}'.format(d.content, d.pos) for d in
                               Dict.objects.filter(
                                   action=Dict.ACTION_ADD)]))

        with open(self.TRIE_DEL_TEMP_FILE, 'w', encoding="utf-8") as f:
            f.write('\n'.join(['{} {}'.format(d.content, d.pos) for d in
                               Dict.objects.filter(
                                   action=Dict.ACTION_DELETE)]))

        self.tokenizer = pybo.BoTokenizer(
            'POS',
            toadd_filenames=[Path(self.TRIE_ADD_TEMP_FILE)],
            todel_filenames=[Path(self.TRIE_DEL_TEMP_FILE)]
        )

        os.remove(self.TRIE_ADD_TEMP_FILE)
        os.remove(self.TRIE_DEL_TEMP_FILE)

        # print(self.tokenizer.tok.trie.has_word("abc"))

    @property
    def view(self):
        return self.editor.view

    @property
    def tokens(self):
        return self.editor.tokens

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

    def matchRules(self):
        rules = Rule.objects.all()
        self.matcher.match(self.tokens, rules)
