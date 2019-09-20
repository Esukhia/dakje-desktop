from pybo import *


class Word:
    def __init__(self, token):
        # from pybo Token object
        self.text = None        # substring of the raw input string
        self.char_groups = None    # a group attributed to every character. from BoStringUtils
        self.chunk_type = None     # attributed by BoTokenizer.Tokenizer
        self.chunk_markers = None  # convert the int in chunk_type into something readable
        self.syls = None           # indices of syl chars to find cleaned syllables from self.text
        self.start = None          # start index of the word in the raw input string
        self.tag = None            # tag attributed by BoTokenizer.Tokenizer (more than UD tag)
        self.partOfSpeech = None   # POS attributed by BoTokenizer.Tokenizer (raw UD POS tag)
        self.__import_token(token)

        # specific to Word object
        self.tagIsOn = False
        self.level = 0
        self.taggedModePosition = 0
        self.plainTextModePosition = 0
        self.highlighted = {}

    def __import_token(self, token):
        self.text = token.text
        self.char_groups = token.char_groups
        self.chunk_type = token.chunk_type
        self.chunk_markers = token.chunk_markers
        self.syls = token.syls
        self.start = token.start
        self.tag = token.tag
        self.partOfSpeech = token.pos

    def isInPartOfSpeech(self, index):
        if self.length <= index < self.length + self.partOfSpeechLen:
            return True
        else:
            return False

    def needHighlighted(self):
        if True:
            for index, textFormat in self.highlighted.items():
                if self.isInPartOfSpeech(index):
                    return textFormat

    @property
    def length(self):
        return len(self.text)

    @property
    def end(self):
        return self.start + self.length

    @property
    def partOfSpeechEnd(self):
        return self.end + self.partOfSpeechLen

    @property
    def modeEnd(self):
        if self.tagIsOn:
            return self.partOfSpeechEnd
        else:
            return self.end

    @property
    def partOfSpeechLen(self):
        return len(self.partOfSpeech) + 1  # plus one for '/'


if __name__ == '__main__':
    trie = PyBoTrie(BoSyl(), 'empty')
    trie.inflect_n_add('བདེ་བ་', 'NOUN')
    trie.add('གཏན་', 'NOUN')
    trie.add('གྱི་', data='PART')
    tok = Tokenizer(trie)
    tokens = tok.tokenize(PyBoTextChunks('གཏན་གྱི་བདེ་བའི་རྒྱུ།'))
    words = [Word(token) for token in tokens]
    print('ok')
