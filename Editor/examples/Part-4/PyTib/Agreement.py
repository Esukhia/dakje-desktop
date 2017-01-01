import re


class Agreement:
    def __init__(self, particles, corrections, SC):
        self.SC = SC
        self.cases = []
        for part in particles:
            self.cases.append((particles[part], corrections[part]))


    def part_agreement(self, previous_syl, particle):
        """
        proposes the right particle according to the previous syllable.
            In case of an invalid previous syllable, returns the particle preceded by *
            limitation : particle needs to be a separate syllabes. (the problems with wrong merged agreement will be flagged by get_mingzhi )
            input : previous syllable, particle
        :param previous_syl: preceding syllable
        :param particle: particle at hand
        :return: the correct agreement for the preceding syllable
        """
        previous = self.SC.get_info(previous_syl)
        mingzhi = self.SC.get_mingzhi(previous_syl)
        final = ''
        if previous == 'dadrag':
            final = 'ད་དྲག'
        elif previous == 'thame':
            # the agreement of thame syllable often depend on their ending and not on their mingzhi
            # a thame syllable can end this way : [ྱྲླྭྷ]?[ིེོུ]?(འ[ིོུ]|ར|ས)
            ssyl = re.sub(r'[ིེོུ]$', '', previous_syl)  # removes vowels occurring after འ
            if ssyl[-1] == mingzhi:  # if the mingzhi was only followed by a vowel
                final = 'མཐའ་མེད'
            elif ssyl.endswith('འ'):  # if the syllable ended either by འི, འུ or འོ
                final = 'འ'
            elif ssyl.endswith('ར'):  # if the syllable ended with a ར
                final = 'ར'
            elif ssyl.endswith('ས'):  # if the syllable ended with a ས
                final = 'ས'
            elif ssyl[-2] == mingzhi:  # if the syllable ended with [ྱྲླྭྷ] plus a vowel
                final = 'མཐའ་མེད'
            else:  # catch all other cases
                final = None
        else:
            final = previous[-1]
            if final not in ['ག', 'ང', 'ད', 'ན', 'བ', 'མ', 'འ', 'ར', 'ལ', 'ས']:
                final = None

        if final:
            # added the ད་དྲག་ for all and the མཐའ་མེད་ for all in provision of all cases
            # where an extra syllable is needed in verses
            # dadrag added according to Élie’s rules.

            correction = ''
            for case in self.cases:
                if particle in case[0]:
                    correction = case[1][final]
            return correction
        else:
            return '*' + particle
