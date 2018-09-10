import pybo

from .ViewManager import ViewManager

class Token:
    def __init__(self, token):
        self.content = token.content
        self.pos = token.pos

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

    def segment(self, sentence):
        tokens = self.tokenizer.tokenize(sentence)
        return [Token(t) for t in tokens]

    def getString(self, tokens):
        if self.view == ViewManager.PLAIN_TEXT_VIEW:
            return ''.join([t.content for t in tokens])
        elif self.view == ViewManager.SPACE_VIEW:
            return ' '.join([t.content for t in tokens])
        elif self.view == ViewManager.TAG_VIEW:
            return ''.join([t.content + '/' + t.pos for t in tokens])
        else:
            return ' '.join([t.content + '/' + t.pos for t in tokens])
