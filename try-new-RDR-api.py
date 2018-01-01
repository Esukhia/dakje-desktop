from RDRPOSTagger.new_api import Tagger


class Word:
    def __init__(self, content):
        self.content = content
        self.partOfSpeech = None


def format_tagged(tagged):
    token_sep, tag_sep = ' ', '/'
    tokens = ['{}{}{}'.format(W.content, tag_sep, W.partOfSpeech) for W in tagged]
    return token_sep.join(tokens)


sentence = "ང་ ལྷ་ས་ this ལ་ འགྲོ་་ is གི་ ཡོད། true"

seg_tagger = Tagger(language="bo", mode="segment")
print(seg_tagger.tag_raw_line(sentence))
# ང་/X ལྷ་ས་/Y this/None ལ་/Z འགྲོ་་/Z is/None གི་/Z ཡོད།/E true/None

words = [Word(word) for word in sentence.split()]
POS_tagger = Tagger(language="bo", mode="default")
POS_tagger.tag_words(words)
print(format_tagged(words))
# ང་/PRON ལྷ་ས་/PROPN this/None ལ་/ADP འགྲོ་་/NOUN is/None གི་/ADP ཡོད།/NOUN true/None

# accepted modes: default, UD, segment
# the tagger will do as if non-tibetan tokens didn't exist, that is why
# the English words have "OOV" (default value, OutOfVocabulary) as tag
# What was actually tagged is "ང་_ལྷ་ས་_ལ་_འགྲོ་་_གི་_ཡོད།"