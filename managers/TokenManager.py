import pybo

from .ViewManager import ViewManager


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

    @property
    def length(self):
        return self.end - self.start

    @property
    def contentWithoutTsek(self):
        return self.content[:-1] if self.content.endswith('་') else self.content


class TokenManager:
    def __init__(self, editor):
        self.editor = editor
        self.lang = "bo"
        self.mode = "default"
        self.tagger = None
        self.tokenizer = None

        if not self.tokenizer:
            self.tokenizer = pybo.BoTokenizer('POS')

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
        for token in self.tokens:
            if position in range(token.start, token.end):
                return token

    # def getSavedTokens(self):
    #     return [Token(tokenDoc, tokenDoc.doc_id)
    #             for tokenDoc in self.editor.storage.all()]

    def saveTokens(self):
        for token in self.tokens:
            token.id = self.editor.db.insert({
                'content': token.content,
                'pos': token.pos,
                'level': token.level
            })

    def readTokens(self):
        self.editor.tokens = [Token(tokenDoc, tokenDoc.doc_id)
                              for tokenDoc in self.editor.db.all()]
        self.editor.refreshView()
        self.editor.refreshCoverage()

    # def updateToken(self, token, attrsDict):
    #     if token.id is not None:
    #         self.editor.storage.get(doc_id=token.id)
    #     else:
    #         raise AttributeError('The token must have an id for updating.')
