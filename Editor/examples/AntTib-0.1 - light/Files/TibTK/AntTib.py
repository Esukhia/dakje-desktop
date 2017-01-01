#!/usr/bin/env python
import re
from .common import strip_list

mark = '*'  # marker of unknown syllables. Can’t be a letter. Only 1 char allowed. Can’t be left empty.

class AntTib:
    """
    Pseudo-Wylie created for use in AntConc.
    The output only contains letters for the syllables, :; for the punctuation.
    All yigos are deleted
    """

    def __init__(self, roots, rareC, wazurC, NB, special, wazur, SC):

        # 1rst part of the syllable
        self.roots = roots
        self.rareC = rareC
        self.wazurC = wazurC
        self.A = {**self.roots, **self.rareC, **self.wazurC}
        # second part of the syllable
        self.NB = NB
        # exceptions
        self.special = special
        self.wazur = wazur
        self.exceptions = {**self.special, **self.wazur}
        # inversed lists
        self.C = {v: k for k, v in self.A.items()}
        self.D = {v: k for k, v in self.NB.items()}
        self.E = {v: k for k, v in self.exceptions.items()}

        self.SC = SC

        self.bad_line = '*** '*5+'BAD LINE '+'*** '*5+'\n'
        self.sep = '\t'
        self.nums = r'[.0-9]+\t'
        self.chars = r'[ a-zA-Z]+'
        self.conv = 0  # value to return if file already converted

    def to_ant_syl(self, components):
        """

        :param components: the tuple outputed by SylComponents().get_parts(<syl>)
        :return: the AntTib of that syllable
        """
        if type(components) == 'list' or not components:
            return '***'
        else:
            part1 = components[0]
            part2 = components[1]
            if part1 not in self.A and part1 not in self.exceptions:
                return '***'
            else:
                # first part of the syllable
                if part1 in self.exceptions:
                    a = self.exceptions[part1]
                else:
                    a = self.A[part1]
                # second part of the syllable
                b = ''
                if part2 == '':
                    b = 'a'
                elif part2 != 'x':
                    b = self.NB[part2]
                return a + b

    def from_ant_syl(self, syl):
        """

        :param syl: takes as input a AntTib syllable
        :return: its Tibetan unicode counterpart
        """
        if syl == '***':
            return '***'
        elif syl == '':
            return ''
        else:
            a = ''
            if syl in self.E:
                return self.E[syl]
            elif syl in self.C:
                return self.C[syl]
            else:
                i = len(syl) - 1
                while i >= 0:
                    if syl[:i] in self.C:
                        a = syl[:i]
                        break
                    i -= 1
            b = syl[len(a):]
            if b.startswith('v') or b.startswith('r') or b.startswith('l') or b.startswith('s'):
                b = 'a' + b
            if b == 'a':
                return self.C[a]
            if a in self.C and b in self.D:  # in order not to fail, returns *** in all non-standard cases
                return self.C[a] + self.D[b]
            else:
                return '***'

    def __is_punct(self, string):
        if '།' in string or '༎' in string or '༏' in string or '༐' in string or '༑' in string or '༔' in string or ';' in string or ':' in string:
            return True
        else:
            return False

    def __trim_punct(self, l):
        """
        :param l:    a list splitted on the punctuation with re.split() where the regex was
                        something like ((<punct>|<punct>)+)
        :return: the same list, only keeping one of the two punctuation elements re.split() gave
        """
        i = 0
        while i < len(l) - 1:
            if self.__is_punct(l[i]) and self.__is_punct(l[i + 1]):
                del l[i + 1]
            i += 1

    def to_ant_text(self, string):
        """

        :param string: a Tibetan text string
        :return: its counterpart in AntTib with the punctuation diminished to shads(;) and tershe(:)
        """
        # Todo : make a new class to deal with the punctuation instead of doing it here
        # Prepare the string : delete all extra punctuations
        # replace the tabs by normal spaces
        string = string.replace('   ', ' ')
        # replace all non-breaking tsek by a normal tshek
        string = string.replace('༌', '་')
        # replace multiple tsek by a single one
        string = re.sub(r'་+', r'་', string)
        # delete all yigos
        string = re.sub('(༄༅+|༆|༇|༈)།?༎? ?།?༎?', '', string)
        # split on the punctuation. here, a paragraph is just a chunk of text separated by shads.

        # split on remaining punctuation
        paragraphs = re.split(r'(( *། *| *༎ *| *༏ *| *༐ *| *༑ *| *༔ *)+)', string)
        # trim the extra punctuation
        self.__trim_punct(paragraphs)
        strip_list(paragraphs)  # delete empty elements beginning or ending the list

        # replace all shads by a ';' and the tershe by a ':'
        for num, element in enumerate(paragraphs):
            if '།' in element or '༏' in element or '༐' in element or '༑' in element:
                paragraphs[num] = element.replace('།', ';').replace('༎', ';').replace('༏', ';').replace('༐', ';').replace('༑', ';')
            elif '༎' in element:
                paragraphs[num] = element.replace('༎', ';;')
            elif '༔' in element:
                paragraphs[num] = element.replace('༔', ':')

        # translate the syllables into pseudo-wylie
        ant_text = []
        for par in paragraphs:
            if ';' not in par and ':' not in par:
                par = re.sub(r'([^་\*]) ', r'\1-', par)  # adds a - everywhere a space is not preceded by a tsek to find the merged particles
                par = re.sub(r'་$', '', par.replace('་ ', ' '))  # delete all tsek at the end of words
                ant_par = []
                words = par.split(' ')
                for word in words:
                    syls = word.split('་')
                    ant_word = []
                    for syl in syls:
                        # deals with the fusioned particles like མཐར་ that have become མཐའ ར་. we want to see 'mthav r'
                        # it is a bit of a hack because I already add a space instead of doing it with ' '.join()
                        if '-' in syl:
                            if syl.startswith(mark) and not syl.startswith(mark*3):  # passes the test if the syllable only starts with one *
                                psyl = syl[1:].split('-')
                                psyl_a = mark + self.to_ant_syl(self.SC.get_parts(psyl[0]))
                                psyl_b = self.to_ant_syl(self.SC.get_parts(psyl[1]))
                                if psyl_b.startswith('a'):
                                    psyl_b = psyl_b[1:]
                                elif psyl_b.endswith('a'):
                                    psyl_b = psyl_b[:-1]
                                ant_word.append(psyl_a + ' ' + psyl_b)
                            else:
                                psyl = syl.split('-')
                                psyl_a = self.to_ant_syl(self.SC.get_parts(psyl[0]))
                                psyl_b = self.to_ant_syl(self.SC.get_parts(psyl[1]))
                                if psyl_b.startswith('a'):
                                    psyl_b = psyl_b[1:]
                                elif psyl_b.endswith('a'):
                                    psyl_b = psyl_b[:-1]
                                ant_word.append(psyl_a + ' ' + psyl_b)
                        else:
                            if syl.startswith(mark) and not syl.startswith(mark*3):
                                # needed to this condition to not end up with ****
                                psyl_c = self.to_ant_syl(self.SC.get_parts(syl[1:]))
                                if psyl_c == mark*3:
                                    ant_word.append(psyl_c)
                                else:
                                    ant_word.append(mark + psyl_c)
                            else:
                                ant_word.append(self.to_ant_syl(self.SC.get_parts(syl)))
                    ant_par.append('x'.join(ant_word))
                ant_text.append(' '.join(ant_par))
            else:
                ant_text.append(par)
        return ''.join(ant_text)

    def from_ant_text(self, string):
        """

        :param string: an AntTib string
        :return: its counterpart in Tibetan unicode
        """
        paragraphs = re.split(r'(( *; *| *: *)+)', string)
        # delete the last element of the list if it is an empty string
        strip_list(paragraphs)
        # trim the extra punctuation (see comment in to_pw_text)
        self.__trim_punct(paragraphs)
        ant_text = []
        for par in paragraphs:
            if ';' not in par and ':' not in par:
                ant_par = []
                par = re.sub(r' (r|s|vi|vo|vang|vam)( |$)', r'-\1\2', par)  # all the Csuffixes
                words = par.split(' ')
                for word in words:
                    if word.endswith('x'):  # delete the x at the end of words
                        word = word[:-1]
                    syls = word.split('x')
                    ant_word = []
                    for syl in syls:
                        # deals with the fusioned particles
                        # is a similar hack as for the previous function
                        if '-' in syl:
                            if syl.startswith(mark) and not syl.startswith(mark*3):
                                psyl = syl[1:].split('-')
                                ant_word.append(mark + self.from_ant_syl(psyl[0]) + ' ' + self.from_ant_syl(psyl[1]))
                            else:
                                psyl = syl.split('-')
                                ant_word.append(self.from_ant_syl(psyl[0]) + ' ' + self.from_ant_syl(psyl[1]))
                        else:
                            if syl.startswith(mark) and not syl.startswith(mark*3):
                                ant_word.append(mark + self.from_ant_syl(syl[1:]))
                            else:
                                ant_word.append(self.from_ant_syl(syl))
                    ant_par.append('་'.join(ant_word) + '་')
                ant_text.append(' '.join(ant_par))
            else:
                ant_text.append(par.replace(';', '།').replace(':', '༔'))
        ant_text = ''.join(ant_text)
        ant_text = re.sub(r'([^ང])་([༔།])', r'\1\2', ant_text)
        return ant_text

    def no_space(self, string):
        """

        :param string: a segmented Tibetan unicode string
        :return: the same string without the spaces between syllables (keeps all spaces at punctuation)
        """
        regexes = [r'([་|༌])\s',  # spaces preceded by a tsek
                   r'(ང[་|༌])\s',  # ང་ plus space
                   r'\s(ར)',  # idem for the rest
                   r'\s(ས)',
                   r'\s(འི)',
                   r'\s(འོ)']
        for regex in regexes:
            string = re.sub(regex, r'\1', string)
        return string


    def __add_dash(self, ant, tib):
        """
        :param ant: a syllable in ant
        :param tib: the same syllable converted to unicode
        :return: the syllable in unicode with a dash for merged particles
        """
        if ant in ['vi', 'vam', 'vo', 'vang', 'r', 's']:
            return '-' + tib
        else:
            return tib

    def __process(self, lines, comments, num, l_regex):
        """
        Serves as the common part of all AntConc lists to be processed
        :param lines: list to be processed
        :param comments: the number of first lines starting with #
        :param num: number of columns filled with numbers
        :param l_regex: ensures the line is correctly formed and can be processed
        :return: returns the string with the AntTib converted to Unicode
        """
        out = ''
        # put the three first lines in out and delete them from lines[]
        for line in lines[0:comments]:
            out +=line+'\n'
        del lines[0:comments]

        # process the whole file
        for line in lines:
            if re.match(l_regex, line):
                l_out = ''
                parts = line.split('\t')
                for i in range(num):
                    l_out += parts[i]+self.sep
                tib = self.from_ant_text(parts[num])
                tib = self.__add_dash(parts[num], tib)
                l_out += tib+self.sep
                out += l_out+'\n'
            else:
                out += self.bad_line
        return out

    def keyword_list(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        comments = 3  # number of commented lines at the beginning
        num = 3  # number of columns with numbers
        l_regex = self.nums * num + self.chars
        if re.match(r'#Types Before Cut: [.0-9]+', lines[0]) and re.match(r'#Types After Cut: [.0-9]+', lines[1]) and re.match(r'#Search Hits: [.0-9]+', lines[2]) and re.match(l_regex, lines[3]):
            process = self.__process(lines, comments, num, l_regex)
            if not process:
                return None
            else:
                return process
        else:
            return None

    def cluster(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        comments = 2  # number of commented lines at the beginning
        num = 3  # number of columns with numbers
        l_regex = self.nums * num + self.chars
        if re.match(r'#Total No. of Cluster Types: [0-9]+', lines[0]) and re.match(r'#Total No. of Cluster Tokens: [0-9]+', lines[1]) and re.match(l_regex, lines[2]):
            process = self.__process(lines, comments, num, l_regex)
            if not process:
                return None
            else:
                return process
        else:
            return None

    def collocates(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        comments = 2  # number of commented lines at the beginning
        num = 5  # number of columns with numbers
        l_regex = self.nums * num + self.chars
        if re.match(r'#Total No. of Collocate Types: [0-9]+', lines[0]) and re.match(r'#Total No. of Collocate Tokens: [0-9]+', lines[1]) and re.match(l_regex, lines[2]):
            process = self.__process(lines, comments, num, l_regex)
            if not process:
                return None
            else:
                return process
        else:
            return None

    def ngram(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        comments = 2  # number of commented lines at the beginning
        num = 3  # number of columns with numbers
        l_regex = self.nums * num + self.chars
        if re.match(r'#Total No. of N-Gram Types: [0-9]+', lines[0]) and re.match(r'#Total No. of N-Gram Tokens: [0-9]+', lines[1]) and re.match(l_regex, lines[2]):
            process = self.__process(lines, comments, num, l_regex)
            if not process:
                return None
            else:
                return process
        else:
            return None

    def word_list(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        comments = 3  # number of commented lines at the beginning
        num = 2  # number of columns with numbers
        l_regex = self.nums * num + self.chars
        if re.match(r'#Word Types: [0-9]+', lines[0]) and re.match(r'#Word Tokens: [0-9]+', lines[1]) and re.match(r'#Search Hits: [0-9]+', lines[2]) and re.match(l_regex, lines[3]):
            process = self.__process(lines, comments, num, l_regex)
            if not process:
                return None
            else:
                return process
        else:
            return None

    def concordance(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        l_regex = self.nums+r'[ ;:*a-zA-Z]+\t'*2+r'[^\.]+\.txt'+r'\t[.0-9]+'*2
        if re.match(l_regex, lines[0]):
            out = ''
            for line in lines:
                if re.match(l_regex, line):
                    l_out = ''
                    parts = line.split('\t')
                    l_out += parts[0] + self.sep
                    for i in range(2):
                        l_out += self.from_ant_text(parts[i+1].strip()) + self.sep
                    for i in range(3):
                        l_out += parts[i+3] + self.sep
                    out += l_out + '\n'
                else:
                    out += self.bad_line
            return out
        else:
            return None

    def profiler_tags(self, string):
        """
        serves for 'level tags' files and for 'non level tags' files
        :param string:
        :return:
        """
        # check for already converted file
        if '་' in string:
            return self.conv

        words = string.split(' ')

        converted = []
        for word in words:
            if '_' in word:
                parts = re.split(r'(_.)', word)
                converted.append(self.from_ant_text(parts[0])+parts[1])
            else:
                converted.append(self.from_ant_text(word))
        return ' '.join(converted)

    def profiler_stats(self, string):
        # check for already converted file
        if '་' in string:
            return self.conv

        lines = string.split('\n')
        strip_list(lines)

        l_regex = self.chars+'\t'+self.nums+r'[0-9]+'
        if re.match(r'Group Range   Freq    uf_1', lines[32]) and re.match(l_regex, lines[33]):
                out = ''
                out += ('\n'.join(lines[:33])+'\n').replace('\t', self.sep)
                del lines[:33]

                for line in lines:
                    if re.match(l_regex, line):
                        parts = line.split('\t')
                        l_out = self.from_ant_text(parts[0]) + self.sep
                        l_out = self.__add_dash(parts[0], l_out)
                        l_out += self.sep.join(parts[1:])
                        out += l_out + '\n'
                    else:
                        out += self.bad_line
                return out
        else:
            return None

    def words(self, string):
        """
        Serves for both 'level list' output files and for '1 - 1000 words' files
        :param string:
        :return:
        """
        # check for already converted file
        if '་' in string:
            return self.conv

        if '\r\n' in string:
            lines = string.split('\r\n')
        else:
            lines = string.split('\n')
        strip_list(lines)
        words = []
        for word in lines:
            if word != '':
                parts = re.split(r'([\s\t]+)', word)
                w = ''
                if len(parts) > 1:
                    w += ''.join(parts[:-1])
                    tib = self.from_ant_text(parts[-1])
                    w += self.__add_dash(parts[-1], tib)
                else:
                    tib = self.from_ant_text(parts[0])
                    w += self.__add_dash(parts[0], tib)
                words.append(w)
            else:
                words.append(word)
        return '\n'.join(words)
