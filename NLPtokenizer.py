from NLPpipeline import Helpers
import re


class Tokenizer:
    def __init__(self, tokenizer):
        self.pytib = tokenizer
        self.helpers = Helpers()

    def process(self, text):
        if text == '':
            return []
        else:
            # pre-processing

            # segment (note: spaces in input are replaced by underscores, they will be returned in the pipeline)
            text = self.pytib.segment(text, unknown=0, reinsert_aa=False, space_at_punct=True, distinguish_ra_sa=True,
                                      affix_particles=True)

            # post-process segmented
            text = self.helpers.normalize_punct_of(text)

            # split in tokens using spaces
            tokens = self.split_in_tokens(text)

            return tokens

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
        self.spaces = [" ", " ", "᠎", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "​", " ", " ", "　", "﻿"]
        self.tib_punct = ['།', '༑', '༐', '༎', '༈', '༔', '༁', '༡', '༢', '༣', '༤', '༥', '༦', '༧', '༨', '༩', '༠']
        self.other_punct = ['\t', '\n']
        self.all_punct = self.spaces + self.tib_punct
        self.tsk = '་'
        pass

    def segmented2tagged(self, string):
        """

        :param string:
        :return: list of '<syl>/<tag>' strings
        """
        chunks = self.syllabify(string, self.all_punct)
        tagged = []
        for word in chunks:
            tagged_word = ['{}/{}'.format(t[0], t[1]) for t in self._tag_word(word, affix_sep='-')]
            tagged.extend(tagged_word)
        return tagged

    def _tag_word(self, word, affix_sep='+'):
        tagged_syls = []

        if self._is_not_punct_nor_empty(word):
            syls = [[w, '#'] for w in self.syllabify(word, syl_sep=self.tsk)]

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

        elif word != '':
            tagged_syls.append([word, 'O'])

        return tagged_syls

    @staticmethod
    def tagged2segmented(syls):
        segmented = []
        split_syls = [a.split('/') for a in syls]
        for num, syl in enumerate(split_syls):
            content, tag = syl
            if tag.endswith('S') or tag == 'E':
                segmented.append(content + '་')
            elif tag == 'O':
                if not split_syls[num - 1][0].endswith('ང'):
                    segmented[num - 1] = segmented[num - 1].replace('་', '')
                segmented.append(content)
            elif tag == 'ES' or tag == 'SS':
                segmented[num - 1] = segmented[num - 1]
                segmented.append(content + '་')
            else:
                segmented.append(content + '་')
        segmented_str = ''.join(segmented)
        return segmented_str

    @staticmethod
    def syllabify(string, breaks=None, syl_sep=None):
        syls = ['']
        c = 0
        while c <= len(string) - 1:
            char = string[c]
            if breaks and char in breaks:
                if syls[-1] != '':
                    if c < len(string):
                        syls.append('')
                while c < len(string) and string[c] in breaks:
                    syls[-1] += string[c]
                    c += 1
                if c < len(string):
                    syls.append('')
            elif syl_sep and char == syl_sep:
                syls[-1] += char
                if c < len(string):
                    syls.append('')
                c += 1
            else:
                syls[-1] += char
                c += 1
        return syls

    @staticmethod
    def _is_not_punct_nor_empty(word):
        match = re.findall(r'[།༑༐༎༈༔༁༡༢༣༤༥༦༧༨༩༠ ]', word)
        if match or word == '':
            return False
        return True

    @staticmethod
    def _is_affixed_syl(syls):
        if '+' in syls[-1][0]:
            return True
        return False


if __name__ == '__main__':
    stc = SegmentedTaggedConvertor()
    inPut = '''སྐྱེས །  ། རྒན་པོ ལོ་ལོན འདི གཅིག་པུ ། །; དཀར་གསལ དུང་ཟླ འདི མཛེས་པ-ས །  ། སྣང་བ-འི མེ་ཏོག ཀྱང འབུས ཏེ ། 
     ། ཚོར་བ-འི ཁ་དོག དེ བཞད ན །  ། ཆིག་ལབ སྐྱ་བོ འང དྲན འོང །།; གནད་དུ་སྨིན་པ ཞིག མ་རྙེད །  ། ལོ་ཟླ ལྕག གིས ཀྱང མ སྐུལ 
     །  ། རེ་དོག ཕྲེང་བ ཡིས བརྒྱུས་པ-འི །  ། མི་ཚེ ཁོ་ཐག ཀྱང མ་ཆོད ། །; དགུན གསུམ ལྷག་རླུང འདི ལྡང་བ-ས །  ། རུལ གོག 
     ཕྱི་ཤུན ཡང གཙེས བྱུང ། ། ན་ནིང ལོ་མ དེ-ར བྲིས་པ-འི །  ། དགའ་བ-འི ཡིག་རིས ཀྱང དེངས སོང །།; དལ གྱིས རླུང་བུ ཞིག འཕུར 
     ཏེ །  ། ཁོ་བོ-འི པང་ཁུག ན བསྔས བྱུང ། ། ལོ་ཟླ མང་པོ རུ མ་མཇལ །  ། དཔྱིད་ཀྱི་དཔལ་ཡོན དེ ཡིན ནམ ། །; འགྲོ་འོང འཚུབ ཁ 
     འདི རྒྱས་པ-ས །  ། ང དང འདུན་པ ཡི བར ལ །  ། གྲེ ལས ཕྱུང་བ རང མིན་པ-འི །  ། རི་བོ-འི བྲག་ཅ དེ ཐོས སྐད ། །; སེམས དང 
     དད་པ གཉིས འདྲེས་པ-འི །  ། རང་སྣང ལྷ-ར བསྲེ རང འོང ན །  ། ཤིང གི སྐྲ་ཤད དེ བོར་བ-ས །  ། གཙུག་གི་རལ་བ འདི འཕྱིང འགྲོ 
     ། །; ལྡེབས་ངོས སྨིག་རྒྱུ ཞིག མཆེད དེ །  ། ཤིང་སྡོང ཁེ-ར སྐྱེས ཤིག བྲིས སོང ། ། མིག ལ འདྲེས་+བ རང་བྱུང ན །  ། 
     རྟོག་པ-འི བལ་སྐུད ཅིག གྲུབ འགྲོ ། །; ཁ་བ མ་བབས་པ-འི མཚན་མོ །  ། གྲང་ངར ལྷག ལྷག ཏུ འཕྱོ ཡང ། ། རླུང་བུ-ས དྲིལ་བ ཡི 
     ཤོག་ལྷེ-ར །  ། སྨྱུ་གུ-འི རྐང་རྗེས འདི དོད འོང །།'''
    tagged = stc.segmented2tagged(inPut)
    print(tagged)
    reverted = stc.tagged2segmented(tagged)
    print(inPut.replace('\n', ' '))
    print(reverted.replace('\n', ' '))

