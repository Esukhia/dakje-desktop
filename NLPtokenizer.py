from NLPpipeline import Helpers


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
