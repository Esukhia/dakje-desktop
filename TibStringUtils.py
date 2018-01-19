class TibString:
    def __init__(self, string):
        # basic types
        self.BASE = 0
        self.CONS = 1
        self.SUB_CONS = 2
        self.VOW = 3
        self.TSEK = 4
        self.SKRT_CONS = 5
        self.SKRT_SUB_CONS = 6
        self.SKRT_VOW = 7
        self.PUNCT = 8
        self.NUM = 9
        self.IN_SYL_MARK = 10
        self.SPECIAL_PUNCT = 11
        self.SYMBOLS = 12
        self.OTHER = 13
        self.SPACE = 14
        # all spaces from the unicode tables
        self.spaces = [" ", " ", "᠎", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "​", " ", " ", "　", "﻿"]

        self.string = string
        self.len = len(string)
        self.base_structure = {}
        self.__attribute_basic_types()

    def __attribute_basic_types(self):
        """
        the whole Tibetan Unicode Table was organized in meaningful lists
        """
        cons = "ཀཁགངཅཆཇཉཏཐདནཔཕབམཙཚཛཝཞཟའཡརལཤསཧཨཪ"
        sub_cons = "ྐྑྒྔྕྖྗྙྟྠྡྣྤྥྦྨྩྪྫྭྮྯྰྱྲླྴྶྷྸྺྻྼཱ"
        vow = "ིེོུ"
        tsek = "་༌"
        skrt_cons = "གྷཊཋཌཌྷཎདྷབྷཛྷཥཀྵཫཬ྅"
        skrt_sub_cons = "ྒྷྚྛྜྜྷྞྡྷྦྷྫྷྵྐྵ"
        skrt_vow = "ཱཱིུྲྀཷླྀཹ྄ཱཻཽྀྀྂྃ྆ཿ"
        normal_punct = "༄༅༆༈།༎༏༐༑༔༴༼༽"
        numerals = "༠༡༢༣༤༥༦༧༨༩"
        in_syl_marks = "༵༷༸ཾ"
        special_punct = "༁༂༃༒༇༉༊༺༻༾༿࿐࿑࿓࿔"
        symbols = "ༀ༓༕༖༗༘༙༚༛༜༝༞༟༪༫༬༭༮༯༰༱༲༳༶༹྇ྈྉྊྋྌྍྎྏ྾྿࿀࿁࿂࿃࿄࿅࿆࿇࿈࿉࿊࿋࿌࿎࿏࿒࿕࿖࿗࿘࿙࿚"
        for i in range(len(self.string)):
            char = self.string[i]
            if char in cons:
                self.base_structure[i] = {self.BASE: self.CONS}
            elif char in sub_cons:
                self.base_structure[i] = {self.BASE: self.SUB_CONS}
            elif char in vow:
                self.base_structure[i] = {self.BASE: self.VOW}
            elif char in tsek:
                self.base_structure[i] = {self.BASE: self.TSEK}
            elif char in skrt_cons:
                self.base_structure[i] = {self.BASE: self.SKRT_CONS}
            elif char in skrt_sub_cons:
                self.base_structure[i] = {self.BASE: self.SKRT_SUB_CONS}
            elif char in skrt_vow:
                self.base_structure[i] = {self.BASE: self.SKRT_VOW}
            elif char in normal_punct:
                self.base_structure[i] = {self.BASE: self.PUNCT}
            elif char in numerals:
                self.base_structure[i] = {self.BASE: self.NUM}
            elif char in in_syl_marks:
                self.base_structure[i] = {self.BASE: self.IN_SYL_MARK}
            elif char in special_punct:
                self.base_structure[i] = {self.BASE: self.SPECIAL_PUNCT}
            elif char in symbols:
                self.base_structure[i] = {self.BASE: self.SYMBOLS}
            elif char in self.spaces:
                self.base_structure[i] = {self.BASE: self.SPACE}
            else:
                self.base_structure[i] = {self.BASE: self.OTHER}


class TibStringUtil(TibString):
    """

    """
    def __init__(self, string):
        TibString.__init__(self, string)

    def chunk_nontib(self, start=None, end=None, yes='bo', no=None):
        if not start and not end:
            start, end = 0, self.len

        indices = self.__chunk(start, end, self.__is_tib_unicode)
        return [(yes, i[1], i[2]) if i[0] else (no, i[1], i[2]) for i in indices]

    def chunk_spaces(self, start=None, end=None, yes='space', no=None):
        if not start and not end:
            start, end = 0, self.len

        indices = self.__chunk(start, end, self.__is_space)
        return [(yes, i[1], i[2]) if i[0] else (no, i[1], i[2]) for i in indices]

    def get_chunked(self, indices):
        return [(t, self.string[start:start + length]) for t, start, length in indices]

    def __is_tib_unicode(self, string_idx):
        return self.base_structure[string_idx][self.BASE] != self.OTHER

    def __is_space(self, string_idx):
        return self.base_structure[string_idx][self.BASE] == self.SPACE

    @staticmethod
    def pipe_chunk(indices, piped_chunk, old_yes, new_yes):
        """

        :param indices:
        :param piped_chunk:
        :param old_yes:
        :param new_yes:
        :return:
        """
        for i, chunk in enumerate(indices):
            if chunk[0] == old_yes:
                new = piped_chunk(chunk[1], chunk[1]+chunk[2], yes=new_yes)
                if new:
                    del tib_nontib[i]
                    for j, n_chunk in enumerate(new):
                        if n_chunk[0] != new_yes:
                            tib_nontib.insert(i+j, (chunk[0], n_chunk[1], n_chunk[2]))
                        else:
                            tib_nontib.insert(i+j, n_chunk)

    @staticmethod
    def __chunk(start_idx, end_idx, condition):
        """

        :param start_idx:
        :param end_idx:
        :param condition:
        :return:
        """
        chunked = []
        start = start_idx
        length = 0
        prev_state = -1
        current_state = -1
        for i in range(start_idx, end_idx):
            current_state = condition(i)
            if prev_state == -1:
                prev_state = current_state

            if current_state == prev_state:
                length += 1
            else:
                chunked.append((prev_state, start, length))
                prev_state = current_state
                start += length
                length = 1
        # final element
        if length != 0:
            if current_state == prev_state:
                if start + length < end_idx:
                    length += 1
            chunked.append((prev_state, start, length))
        return chunked


if __name__ == '__main__':
    """
    test usage
    """
    mixed = ' བཀྲ་  tr ཤིས།'

    tsu = TibStringUtil(mixed)
    tib_nontib = tsu.chunk_nontib(yes='བོད་ཡིག')
    tsu.get_chunked(tib_nontib)
    # [('བོད་ཡིག', ' བཀྲ་  '), (None, 'tr'), ('བོད་ཡིག', ' ཤིས།')]

    tsu.pipe_chunk(tib_nontib, tsu.chunk_spaces, 'བོད་ཡིག', 'བར་སྟོང་།')

    tsu.get_chunked(tib_nontib)
    # [('བར་སྟོང་།', ' '), ('བོད་ཡིག', 'བཀྲ་'), ('བར་སྟོང་།', '  '), (None, 'tr'), ('བར་སྟོང་།', ' '), ('བོད་ཡིག', 'ཤིས།')]

    spaces = tsu.chunk_spaces(yes='བར་སྟོང་།')
    tsu.get_chunked(spaces)
    # [('བར་སྟོང་།', ' '), (None, 'བཀྲ་'), ('བར་སྟོང་།', '  '), (None, 'tr'), ('བར་སྟོང་།', ' '), (None, 'ཤིས།')]
