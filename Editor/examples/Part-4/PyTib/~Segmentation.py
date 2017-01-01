# coding: utf-8

import re
from .common import strip_list, search

mark = '*'  # marker of unknown syllables. Can’t be a letter. Only 1 char allowed. Can’t be left empty.


class Segment:
    def __init__(self, lexicon, SC):
        self.lexicon = lexicon
        self.merged_part = r'(ར|ས|འི|འམ|འང|འོ)$'
        self.punct_regex = r'([༄༅༆༇༈།༎༏༐༑༔\s]+)'

        self.SC = SC
        # for bisect
        self.lexicon = sorted(self.lexicon)
        self.len_lexicon = len(self.lexicon)

        self.n = 0  # counter needed between methods segment() and __process()

    def is_word(self, maybe):
        final = False
        if search(self.lexicon, maybe, self.len_lexicon):
            final = True
        elif search(self.lexicon, re.sub(self.merged_part, '', maybe), self.len_lexicon):
            final = True
        else:
            if '་' in maybe:
                last_syl = maybe.split('་')[-1]
                if self.SC.get_info(last_syl) == 'thame':
                    maybe = re.sub(self.merged_part, '', maybe) + 'འ'
            else:
                if self.SC.get_info(maybe) == 'thame':
                    maybe = re.sub(self.merged_part, '', maybe) + 'འ'
            if search(self.lexicon, maybe, self.len_lexicon):
                final = True
        return final

    def __process(self, list1, list2, num):
        word = '་'.join(list1[self.n:self.n + num])
        if not search(self.lexicon, word, self.len_lexicon):
            maybe = re.split(self.merged_part, word)
            if not search(self.lexicon, maybe[0], self.len_lexicon):
                if search(self.lexicon, maybe[0] + 'འ', self.len_lexicon):
                    list2.append(maybe[0] + 'འ')
                else:
                    list2.append(maybe[0])
            else:
                list2.append(maybe[0])
            list2.append(maybe[1] + '་')
            # del list1[:num]
            self.n = self.n + num
        else:
            list2.append(word + "་")
            # del list1[:num]
            self.n = self.n + num

    def segment(self, string, ant_segment, unknown):
        """

        :param string: takes a unicode text file as input
        :param ant_segment: 0, segments normally. 1, separates the merged particles from their syllables
        :param unknown: 0, adds nothing. 1, adds character in variable mark to unknown words/syllables
        :return: outputs the segmented text
        """
        paragraphs = re.split(self.punct_regex, string)
        strip_list(paragraphs)

        text = []
        for par in paragraphs:
            words = []
            if not re.match(self.punct_regex, par):
                syls = par.split('་')
                strip_list(syls)

                self.n = 0
                while self.n < len(syls):
                    if len(syls[self.n:self.n + 3]) == 3 and self.is_word('་'.join(syls[self.n:self.n + 3])):
                        self.__process(syls, words, 3)
                    elif len(syls[self.n:self.n + 2]) == 2 and self.is_word('་'.join(syls[self.n:self.n + 2])):
                        self.__process(syls, words, 2)
                    elif len(syls[self.n:self.n + 1]) == 1 and self.is_word('་'.join(syls[self.n:self.n + 1])):
                        self.__process(syls, words, 1)
                    else:
                        if unknown == 0:
                            words.append('་'.join(syls[self.n:self.n + 1]) + '་')
                        elif unknown == 1:
                            words.append(mark + '་'.join(syls[self.n:self.n + 1]) + '་')
                        self.n += 1
                paragraph = ' '.join(words)
                if not paragraph.endswith('ང་'):
                    paragraph = paragraph[:-1]
                #########
                # add spaces at all tseks
                if ant_segment == 1:
                    paragraph = re.sub(r'་([^ ])', r'་ \1', paragraph)
                #
                #########
                text.append(paragraph)
            else:
                text.append(par)
        #
        ######################
        return ''.join(text)


def main():
    import os
    for file in os.listdir("../IN/"):
        with open('../IN/' + file, 'r', -1, 'utf-8-sig') as f:
            current_file = f.read().replace('༌', '་').replace('\r\n', '\n').replace('\r', '\n')
            current_file = current_file.split('\n')

        seg = Segment()
        text = []
        for line in current_file:
            if line == '':
                text.append(line)
            else:
                text.append(seg.segment(line, ant_segment=0, unknown=1))

        # write output
        with open('../' + 'anttib_' + file, 'w', -1, 'utf-8-sig') as f:
            f.write('\n'.join(text))

if __name__ == '__main__':
    main()