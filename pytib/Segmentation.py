# coding: utf-8

import re
from .common import strip_list, search, occ_indexes, merge_list_items, split_list_items, is_tibetan_letter, open_file

mark = '#'  # marker of unknown syllables. Can’t be a letter. Only 1 char allowed. Can’t be left empty.


class Segment:
    def __init__(self, lexicon, compound, ancient, exceptions, len_word_syls, user_vocabs, SC):
        self.lexicon = lexicon
        self.user_vocabs = user_vocabs
        self.merged_part = r'(ར|ས|འི|འམ|འང|འོ|འིའོ)$'
        self.punct_regex = r'(་?[༄༅༆༇༈།༎༏༐༑༔\s]+་?)'

        self.SC = SC

        # for bisect
        self.lexicon = sorted(self.lexicon)
        self.len_lexicon = len(self.lexicon)

        self.compound = compound
        self.len_word_syls = len_word_syls

        self.ancient = ancient
        self.exceptions = exceptions

        self.n = 0  # counter needed between methods segment() and __process()

    def include_user_vocab(self, vocabs=True):
        def find_non_dupes(longer_list, len_longer, shorter_list):
            non_dupes = []
            for x in shorter_list:
                if not search(longer_list, x, len_longer):
                    non_dupes.append(x)
            return non_dupes

        def find_new(vocabs):
            new_entries = []
            for vocab in vocabs:
                # filter the current vocab with the previously found new_entries
                deduped_vocab = find_non_dupes(new_entries, len(new_entries), self.user_vocabs[vocab])
                # find entries from deduped_vocab that are not in self.lexicon
                new = find_non_dupes(self.lexicon, self.len_lexicon, deduped_vocab)
                new_entries.extend(new)
            return new_entries

        # 1. find all new entries to add to self.lexicon
        if type(vocabs) is not list:
            all_vocabs = [a for a in self.user_vocabs.keys()]
            total_entries = find_new(all_vocabs)
        else:
            total_entries = find_new(vocabs)

        # 2. update the lexicon with the new entries
        self.lexicon = sorted(self.lexicon+total_entries)

        # for bisect
        self.len_lexicon = len(self.lexicon)

        # for segment()
        self.len_word_syls = list(set([len(word.split('་')) for word in self.lexicon]))
        self.len_word_syls = sorted(self.len_word_syls, reverse=True)

    def is_word(self, maybe):
        final = False
        if search(self.lexicon, maybe, self.len_lexicon):
            final = True
        elif self.SC.is_thame(maybe):
            if search(self.lexicon, re.sub(self.merged_part, '', maybe), self.len_lexicon):
                final = True
            elif search(self.lexicon, re.sub(self.merged_part, '', maybe) + 'འ', self.len_lexicon):
                final = True
        elif re.sub(self.merged_part, '', maybe) in self.exceptions and search(self.lexicon, re.sub(self.merged_part, '', maybe), self.len_lexicon):
            final = True
        return final

    def __process(self, list1, list2, num, reinsert_aa, distinguish_ra_sa):
        word = '་'.join(list1[self.n:self.n + num])
        if not search(self.lexicon, word, self.len_lexicon):
            maybe = re.split(self.merged_part, word)
            if not search(self.lexicon, maybe[0], self.len_lexicon):
                if reinsert_aa and search(self.lexicon, maybe[0] + 'འ', self.len_lexicon):
                    list2.append(maybe[0] + 'འ')
                else:
                    list2.append(maybe[0])
            else:
                list2.append(maybe[0])
            # separate འིའོ
            if maybe[1] == 'འིའོ':
                maybe[1] = maybe[1][:2]+' '+maybe[1][2:]
            if distinguish_ra_sa:
                list2.append('_{}་'.format(maybe[1]))
            else:
                list2.append(maybe[1] + '་')
            # del list1[:num]
            self.n = self.n + num
        else:
            list2.append(word + "་")
            # del list1[:num]
            self.n = self.n + num

    def basis_segmentation(self, string, unknown=1, space_at_punct=True, syl_segmented=0, reinsert_aa=False, distinguish_ra_sa=False):
        """

        :param string: takes a unicode text file as input
        :param syl_segmented: 0, segments normally. 1, segments in syls while separating the merged particles
        :param unknown: 0, adds nothing. 1, adds character in variable mark to unknown words/syllables
        :param space_at_punct: adds a space between the syls and the punctuation if True
        :return: outputs the segmented text
        """
        string = string.replace('༌', '་')  # replaces unbreakable tseks by normal tseks.
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
                    not_processed = True  # if a word has been found (value is False), don’t try to process the word
                    for l_w in self.len_word_syls:
                        if not_processed is True and self.is_word('་'.join(syls[self.n:self.n + l_w])):
                            self.__process(syls, words, l_w, reinsert_aa, distinguish_ra_sa)
                            not_processed = False
                        elif not_processed is True and len(syls[self.n:self.n + l_w]) == 1:
                            if unknown == 0:
                                words.append('་'.join(syls[self.n:self.n + 1]) + '་')
                            elif unknown == 1:
                                words.append(mark + '་'.join(syls[self.n:self.n + 1]) + '་')
                            self.n += 1
                paragraph = ' '.join(words)

                # regroup པ་བ་པོ་བོ་ with previous syllables
                # we leave the disambiguation of syntax versus morphological unities for POS Tagging
                paragraph = re.sub(r' (པ|བ|པོ|བོ)(\s|་)', r'\1\2', paragraph)

                # delete the extra trailing tsek, since all the trailing tseks are found within the punctuations elements
                paragraph = paragraph.rstrip('་')

                #########
                # add spaces at all tseks
                if syl_segmented == 1:
                    paragraph = re.sub(r'་([^ ])', r'་ \1', paragraph)
                #
                #########
                text.append(paragraph)
            else:
                par = par.replace('	', ' ').replace(' ', ' ')  # hack to eliminate tabs from punctuation blocks
                if space_at_punct:
                    text.append(' '+par.replace(' ', '_')+' ')
                else:
                    text.append(par)
        #
        ######################
        return ''.join(text)#.replace('  ', '')

    def do_compound(self, segmented):
        """

        :param segmented:
        :return:
        """
        words = segmented.split(' ')

        for n, elt in enumerate(self.compound[0]):
            repl = self.compound[1][n]
            syls = repl[1]
            applied = False

            idx = occ_indexes(words, elt)
            if idx != []:  # only keeps replacements that have occurrences in words
                left = repl[0]
                right = repl[2]

                # there is no restriction
                if left == [''] and right == ['']:
                    for i in idx:
                        words[i[0]:i[1]] = syls
                    applied = True

                # there is some restriction
                else:
                    ok = True  # if contexts match
                    # left context
                    if left != ['']:
                        for i in idx:  # for each occurrence
                            for num, l in enumerate(left):
                                # evaluate that the current syllable of the context equals the corresponding one in words
                                # Todo: also check POS and regexes
                                if l.startswith('r'):
                                    print('is a regex')
                                elif l.isupper():
                                    print('is a POS')
                                else:
                                    if l != words[i[0] - (len(left) - num)]:
                                        ok = False

                    # right context
                    if right != ['']:
                        for i in idx:  # for each occurrence
                            # right context
                            for num, l in enumerate(right):
                                # evaluate that the current syllable of the context equals the corresponding one in words
                                # Todo: also check POS and regexes
                                if l.startswith('r'):
                                    print('is a regex')
                                elif l.isupper():
                                    print('is a POS')
                                else:
                                    if l != words[i[0] - (len(left) - num)]:
                                        ok = False

                    # the contexts correspond, so the elements are replaced in word[]
                    if ok:
                        words[i[0]:i[1]] = syls
                        applied = True

            # 2. apply all the modifications annotated in the list
            if applied:
                if '-' in ''.join(syls):
                    words = merge_list_items(words, '-')
                if '+' in ''.join(syls):
                    words = split_list_items(words, '+')

        return ' '.join(words)

    def segment(self, string, unknown=1, syl_segmented=0, space_at_punct=True, danying=False, reinsert_aa=False, distinguish_ra_sa=False):
        uncompound = self.basis_segmentation(string, unknown=unknown, syl_segmented=syl_segmented, space_at_punct=space_at_punct,
                                             reinsert_aa=reinsert_aa, distinguish_ra_sa=distinguish_ra_sa)
        compound = self.do_compound(uncompound)
        # ancient words
        if danying:
            for a in self.ancient:
                seg_a = self.do_compound(self.basis_segmentation(a, unknown=unknown, syl_segmented=syl_segmented, space_at_punct=space_at_punct,
                                         reinsert_aa=reinsert_aa, distinguish_ra_sa=distinguish_ra_sa))
                compound = compound.replace(seg_a, '#-{}-#'.format(seg_a))
        return compound


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
                text.append(seg.segment(line))

        # write output
        with open('../' + 'anttib_' + file, 'w', -1, 'utf-8-sig') as f:
            f.write('\n'.join(text))

if __name__ == '__main__':
    main()
