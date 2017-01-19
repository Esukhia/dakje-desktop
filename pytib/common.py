# coding: utf-8

from bisect import bisect_left
from collections import OrderedDict, Callable
from tempfile import NamedTemporaryFile
import re
import csv


def clean_string(string,
                 tabs2spaces=False, under2spaces=False, spaces2same=False,
                 single_spaces=False, single_returns=False, single_unders=False,
                 del_spaces=False, del_returns=False, del_dashes=False,
                 l_strip=False, r_strip=False, strip=False, ):


    # Replacements
    if tabs2spaces: string = string.replace('\t', ' ')
    if under2spaces: string = string.replace('_', ' ')
    if spaces2same: string = re.sub(r'\s', ' ', string)

    # Reducing to one element
    if single_spaces: string = re.sub(r' +', r' ', string)
    if single_returns: string = re.sub(r'\n+', r'\n', string)
    if single_unders: string = re.sub(r'_+', r'_', string)

    # Delete the given elements
    if del_spaces: string = string.replace(' ', '')
    if del_returns: string = string.replace('\n', '')
    if del_dashes: string = string.replace('-', '')

    # strips
    if l_strip: string = string.lstrip()
    if r_strip: string = string.rstrip()
    if strip: string = string.strip()

    return string


def find_sub_list_indexes(sl, l):
    # find the indexes of the first occurence of a sublist
    if sl == l:
        return 0, len(l)-1
    else:
        # from http://stackoverflow.com/a/17870684
        sll = len(sl)
        for ind in (i for i, e in enumerate(l) if e == sl[0]):
            if l[ind:ind + sll] == sl:
                return ind, ind + sll - 1


def get_longest_common_subseq(data, get_all_subseqs=False):
    """
    Adapted from http://stackoverflow.com/a/28869690
    The get_all_subseqs parameter was added.
    :param data: a list of iterables
    :param get_all_subseqs: returns all the subsequences if True
    :return:
                - the longest common subsequence
                - None if the two sequences are equal
                - [] if there is no subsequence
                - True if possible_subseq == seq
    """
    def is_subseq(possible_subseq, seq):
        if len(possible_subseq) > len(seq):
            return False

        def get_length_n_slices(n):
            for i in range(len(seq) + 1 - n):
                yield seq[i:i + n]

        for slyce in get_length_n_slices(len(possible_subseq)):
            if slyce == possible_subseq:
                return True
        return False

    def is_subseq_of_any(find, data):
        if len(data) < 1 and len(find) < 1:
            return False
        for i in range(len(data)):
            if not is_subseq(find, data[i]):
                return False
        return True
    substr = []
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                potential_subseq = data[0][i:i+j]
                if is_subseq_of_any(potential_subseq, data):
                    if not get_all_subseqs and j > len(substr):
                        substr = potential_subseq
                    if get_all_subseqs:
                        substr.append(potential_subseq)
    return substr


def split_in_two(string, substring, point):
    '''
    splits in two on the closest substring match from the point onwards
    :param string:
    :param substring:
    :param point:
    :return:
    '''
    str_split = pre_process(string, mode='syls')
    sub_split = pre_process(substring, mode='syls')

    index = 0
    c = 0
    for i in range(len(str_split)):
        if sub_split[0] == str_split[point]:
            index = str_split.index(sub_split[0], point)
            break
        else:
            if c < len(str_split) - 1:
                c += 1
            # looking left of middle
            if str_split[point - c] == sub_split[0]:
                index = str_split.index(sub_split[0], point - c)
                break
            # looking right of middle
            if str_split[point + c] == sub_split[0]:
                index = str_split.index(sub_split[0], point + c)
                break
    left = ''.join(str_split[:index])
    right = ''.join(str_split[index + len(sub_split):])
    return left, right


def write_file(file_path, content):
    with open(file_path, 'w', -1, 'utf8') as f:
        f.write(content)


def open_file(file_path):
    try:
        with open(file_path, 'r', -1, 'utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', -1, 'utf-16-le') as f:
            return f.read()


def write_csv(path, rows, header=None, delimiter=',', dialect='excel'):
    """
    wrapper to write csv module that normalises the length of rows
    :param path: writes the csv to the given path
    :param rows: list of iterables corresponding to rows
    :param header: optional first row to include
    :param delimiter: optional.
    :param dialect: optional dialect that csv will use
    :return: writes a file
    """
    def normalise(rows):
        """
        calculates the longest line and adds the necessary empty strings so that all rows have the same length
        :param rows: list of iterables
        :return: a list of rows where each row is a list.
        """
        # calculate longest
        longest_row = 0
        for r in rows:
            if len(r) > longest_row:
                longest_row = len(r)
        # normalise rows
        norm_rows = []
        for r in rows:
            if len(r) < longest_row:
                norm_rows.append([a for a in r]+['' for i in range(longest_row-len(r))])
            else:
                norm_rows.append(r)
        return norm_rows

    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect=dialect, delimiter=delimiter)
        if header:
            rows = [header]+rows
            rows = normalise(rows)
            for row in rows:
                writer.writerow(row)


def temp_object(content):
    temp = NamedTemporaryFile(delete=True)
    temp.write(str.encode(content))
    return temp


def de_pre_process(l):
    return ''.join(l).replace('_', ' ')


def pre_process(raw_string, mode='words'):
    """
    Splits a raw Tibetan orig_list by the punctuation and syllables or words
    :param raw_string:
    :param mode: words for splitting on words, syls for splitting in syllables. Default value is words
    :return: a list with the elements separated from the punctuation
    """
    # replace all underscore if the string contains any
    if '_' in raw_string:
        raw_string = raw_string.replace('_', ' ')

    def is_punct(string):
        # put in common
        if '༄' in string or '༅' in string or '༆' in string or '༇' in string or '༈' in string or \
            '།' in string or '༎' in string or '༏' in string or '༐' in string or '༑' in string or \
            '༔' in string or ';' in string or ':' in string:
            return True
        else:
            return False

    def trim_punct(l):
        i = 0
        while i < len(l) - 1:
            if is_punct(l[i]) and is_punct(l[i + 1]):
                del l[i + 1]
            i += 1

    yigo = r'((༄༅+|༆|༇|༈)།?༎? ?།?༎?)'
    text_punct = r'(( *། *| *༎ *| *༏ *| *༐ *| *༑ *| *༔ *)+)'
    splitted = []
    # replace unbreakable tsek and tabs
    raw_string = raw_string.replace('༌', '་').replace('   ', ' ')
    # split the raw orig_list by the yigos,
    for text in re.split(yigo, raw_string):
        # add the yigos to the list
        if re.match(yigo, text):
            splitted.append(text.replace(' ', '_'))
        elif text != '':
            # split the orig_list between yigos by the text pre_process
            for par in re.split(text_punct, text):
                # add the pre_process to the list
                if is_punct(par):
                    splitted.append(par.replace(' ', '_'))
                elif par != '':
                    # add the segmented text split on words
                    if mode == 'words':
                        splitted.extend(par.split(' '))
                    # add the non-segmented text by splitting it on syllables.
                    elif mode == 'syls':
                        temp = []
                        for chunk in par.split(' '):
                            if '་' in chunk:
                                word = ''
                                for c in chunk:
                                    if c == '་':
                                        word += c
                                        temp.append(word)
                                        word = ''
                                    else:
                                        word += c
                                # adding the last word in temp[]
                                if word != '':
                                    temp.append(word)
                            else:
                                temp.append(chunk)
                        splitted.extend(temp)
                    else:
                        print('non-valid splitting mode. choose either "words" or "syls".')
                        break
    # trim the extra pre_process
    trim_punct(splitted)
    return splitted


def search(l, entry, len_l):
    """
    :param l: list on which to apply bisect
    :param entry: element of this list to find
    :param len_l: lenght of list (needed to return a correct index)
    :return: True or False
    """
    index = bisect_left(l, entry, 0, len_l)
    if index != len_l and l[index] == entry:
        return True
    else:
        return False


def strip_list(l):
    """
    :param l: list to strip
    :return: the list without 1rst and last element if they were empty elements
    """
    while len(l) > 0 and l[0] == '':
        del l[0]
    while len(l) > 0 and l[len(l) - 1] == '':
        del l[len(l) - 1]


def occ_indexes(l, sub_l):
    """
    used for finding the concordances
    :param l: list
    :param sub_l: sub-list
    :return: indexes (x, y) for all occurrences of the sub-list in the list, an empty list if none found
    """
    return [(i, i+len(sub_l)) for i in range(len(l)) if l[i:i+len(sub_l)] == sub_l]


def merge_list_items(l, char):
    """
    merges the current item and the next in char is in the current item
    :param l: list to process
    :param char: character indicating where to merge
    :return: processed list
    """
    c = 0
    while c <= len(l) - 1:
        while char in l[c]:
            l[c:c + 2] = [''.join(l[c].replace(char, '') + l[c + 1])]
        c += 1
    return l


def split_list_items(l, char):
    """
    splits the current item and the next in char is in the current item
    :param l: list to process
    :param char: character indicating where to splits
    :return: processed list
    """
    c = 0
    while c <= len(l) - 1:
        while char in l[c]:
            l[c:c] = l.pop(c).split(char)
        c += 1
    return l


def is_tibetan_letter(char):
    """
    :param char: caracter to check
    :return: True or False
    """
    if (char >= 'ༀ' and char <= '༃') or (char >= 'ཀ' and char <= 'ྼ'):
        return True
    else:
        return False


def is_sskrt(syl):
    # Source for regexes : Paul Hackett Visual Basic script
    # Now do Sanskrit: Skt.vowels, [g|d|b|dz]+_h, hr, shr, Skt
    regex1 = r"([ཀ-ཬཱ-྅ྐ-ྼ]{0,}[ཱཱཱིུ-ཹཻཽ-ྃ][ཀ-ཬཱ-྅ྐ-ྼ]{0,}|[ཀ-ཬཱ-྅ྐ-ྼ]{0,}[གཌདབཛྒྜྡྦྫ][ྷ][ཀ-ཬཱ-྅ྐ-ྼ]{0,}|[ཀ-ཬཱ-྅ྐ-ྼ]{0,}[ཤཧ][ྲ][ཀ-ཬཱ-྅ྐ-ྼ]{0,}|[ཀ-ཬཱ-྅ྐ-ྼ]{0,}[གྷཊ-ཎདྷབྷཛྷཥཀྵ-ཬཱཱཱིུ-ཹཻཽ-ྃྒྷྚ-ྞྡྷྦྷྫྷྵྐྵ-ྼ][ཀ-ཬཱ-྅ྐ-ྼ]{0,})"
    # more Sanskrit: invalid superscript-subscript pairs
    regex2 = r"([ཀ-ཬཱ-྅ྐ-ྼ]{0,}[ཀཁགང-ཉཏ-དན-བམ-ཛཝ-ཡཤཧཨ][ྐ-ྫྷྮ-ྰྴ-ྼ][ཀ-ཬཱ-྅ྐ-ྼ]{0,})"
    # tsa-phru mark used in Chinese transliteration
    regex3 = r"([ཀ-ཬཱ-྅ྐ-ྼ]{0,}[༹][ཀ-ཬཱ-྅ྐ-ྼ]{0,})"
    if re.search(regex1, syl) or re.search(regex2, syl) or re.search(regex3, syl):
        return True
    else:
        return False


def non_tib_chars(string):
    """
    :param string:
    :return: list of non-tibetan non-tibetan-pre_process characters found within a orig_list
    """
    punct = ['༄', '༅', '།', '་', '༌', '༑', '༎', '༏', '༐', '༔']
    chars = []
    for character in string:
        if not is_tibetan_letter(character) and character not in chars and character not in punct:
            chars.append(character)
    return chars


class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self):
        import copy
        return type(self)(self.default_factory, copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory, OrderedDict.__repr__(self))
