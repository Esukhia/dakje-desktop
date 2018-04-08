from TibStringUtils import TibStringUtil
from RDRPOSTagger import Tagger


class Tokenizer:
    def __init__(self, tokenizer):
        self.tok = tokenizer
        self.lang = "bo"
        self.mode = "segment"
        self.tagger = Tagger(language=self.lang, mode=self.mode)  # only instanciate when required
        self.stc = SegmentedTaggedConvertor()

    def process(self, text):
        if text == '':
            return []
        else:
            # pre-processing

            words = self.tok.tokenize(text)

            return words

    def split_in_tokens(self, sentence):
        words = []
        for s in sentence.split(' '):
            if s:
                # 1.
                if s == '\n':
                    words.append(s)
                # 2. the location of \n in s in unknown
                elif '\n' in s:
                    self.split_on_separator(s, '\n', words)
                # 3.
                else:
                    words.append(s)
        return words

    @staticmethod
    def split_on_separator(to_split, separator, destination):
        i = 0
        sub_word = ''
        while i < len(to_split):
            if to_split[i] != separator:
                sub_word += to_split[i]
            else:
                if sub_word != '':
                    destination.append(sub_word)
                    sub_word = ''
                destination.append(separator)
            i += 1


class SegmentedTaggedConvertor:
    """
    follows http://larkpie.net/tibetancorpus/#seg except for 'O' used for 'others'
    """
    def __init__(self):
        self.tsu = TibStringUtil
        pass

    def segmented2tagged(self, string):
        """

        :param string:
        :return: list of '<syl>/<tag>' strings
        """
        tsu = TibStringUtil(string)
        chunks = tsu.chunk_spaces()
        tsu.pipe_chunk(chunks, tsu.chunk_segmented_tib, to_chunk='chars', yes='bo')
        tsu.pipe_chunk(chunks, tsu.chunk_punct, to_chunk='bo', yes='punct')

        tagged = []
        for word in chunks:
            if word[0] == 'bo':
                word_indices = [word]
                tsu.pipe_chunk(word_indices, tsu.syllabify, to_chunk='bo', yes='syl')
                syls = [[a[1], '#'] for a in tsu.get_chunked(word_indices)]
                tagged_word = ['{}/{}'.format(t[0], t[1]) for t in self._tag_word(syls, affix_sep='-')]
                tagged.extend(tagged_word)
            elif word[0] == 'punct':
                tagged.append('{}/{}'.format(tsu.get_chunked([word])[0][1], 'PUNCT'))
            elif word[0] == 'non-bo':
                tagged.append('{}/{}'.format(tsu.get_chunked([word])[0][1], 'NoBo'))
            elif word[0] == 'space':
                pass  # leave spaces out
            else:
                tagged.append('{}/{}'.format(tsu.get_chunked([word])[0][1], 'O'))
        return tagged

    def _tag_word(self, syls, affix_sep='+'):
        tagged_syls = []

        if len(syls) == 1:
            syls[0][1] = 'S'

        elif len(syls) == 2:
            syls[0][1] = 'X'
            syls[1][1] = 'E'

        elif len(syls) == 3:
            syls[0][1] = 'X'
            syls[1][1] = 'Y'
            syls[2][1] = 'E'

        elif len(syls) == 4:
            syls[0][1] = 'X'
            syls[1][1] = 'Y'
            syls[2][1] = 'Z'
            syls[3][1] = 'E'

        elif len(syls) > 4:
            syls[0][1] = 'X'
            syls[1][1] = 'Y'
            syls[2][1] = 'Z'
            for i in range(3, len(syls)-1, 1):
                syls[i][1] = 'M'
            syls[len(syls)-1][1] = 'E'

        if self._is_affixed_syl(syls):
            syls[len(syls) - 1][0] = syls[len(syls)-1][0].replace(affix_sep, '')
            syls[len(syls)-1][1] += 'S'
        tagged_syls.extend(syls)

        return tagged_syls

    @staticmethod
    def tagged2segmented(tagged_syls):
        segmented = []
        for t_syl in tagged_syls:
            syl, tag = t_syl.split('/')
            # remove extra spaces
            if (tag == 'PUNCT' or tag == 'O') and (segmented and segmented[-1] == ' '):
                del segmented[-1]
            segmented.append(syl)
            if tag == 'E' or tag == 'S':
                segmented.append(' ')

        return ''.join(segmented).rstrip(' ')

    @staticmethod
    def _is_affixed_syl(syls):
        if '+' in syls[-1][0]:
            return True
        return False


class Word:
    def __init__(self, content):
        self.content = content
        self.partOfSpeech = None
        self.tagIsOn = False
        self.level = 0
        self.start = 0
        self.length = len(self.content)



