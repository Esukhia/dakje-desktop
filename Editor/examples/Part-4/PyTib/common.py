# coding: utf-8

from bisect import bisect_left


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
    :param seq: sub-list
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
    return False


def non_tib_chars(string):
    """
    :param string:
    :return: list of non-tibetan non-tibetan-punctuation characters found within a string
    """
    punct = ['༄', '༅', '།', '་', '༌', '༑', '༎', '༏', '༐', '༔']
    chars = []
    for character in string:
        if not is_tibetan_letter(character) and character not in chars and character not in punct:
            chars.append(character)
    return chars


