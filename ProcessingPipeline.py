import re
import os
from pytib import getSylComponents
from RDRPOSTagger import models


class Pipeline:
    def __init__(self, tagger, words):
        self.words = words
        self.pos_tagger = POStagging(self.words, tagger)
        self.affixed_sep = 'ᛰ'

    def applyPipeline(self):
        # 1. RDR POS tagging
        self.pos_tagger.RDRPOSTagging(custom_initial_tagging=True)

        # 2. post-tagging attribute filling: UD POS tag, lemma, UD features
        #self.add_lemma_and_UD()

        # Temporary removed from the editor,
        # because there will be some errors occurred,
        # and we don't fully understand lemma, UD and "aa"
        #
        # UD, UD_feature, aa = self.words[i].partOfSpeech.split('_')
        # ValueError: not enough values to unpack (expected 3, got 1)

        self.finalFormatting()
        return self.words

    def add_lemma_and_UD(self):
        for i in range(len(self.words)):
            # create attributes
            self.words[i].lemma = '='
            self.words[i].UD_features = ''

            # update attributes if needed
            if self.affixed_sep in self.words[i].content:
                UD, UD_feature, aa = self.words[i].partOfSpeech.split('_')
                self.words[i].partOfSpeech = UD
                self.words[i].UD_features += UD_feature
                self.words[i].lemma = self.words[i].content.split(self.affixed_sep)[0] + aa

    def finalFormatting(self):
        for i in range(len(self.words)):
            # return spaces and remove affixed particle marks
            self.words[i].content = self.words[i].content.replace('_', ' ').replace(self.affixed_sep, '')


class POStagging:
    def __init__(self, words, tagger):
        self.words = words
        self.tagger = tagger
        self.expanded_vocab_path = models['{}_{}'.format(self.tagger.language,
                                                         self.tagger.mode)][1].replace('.DICT', '.EXPANDED')
        self.pos = self.get_expanded_vocab()
        self.helpers = Helpers()

    def RDRPOSTagging(self, custom_initial_tagging=False):
        tags = []
        batchWords = []
        for word in self.words:
            if word.content == '\n':
                if batchWords:
                    if custom_initial_tagging:
                        tagged = self.tagger.tag_raw_line(' '.join([w.content for w in batchWords]), self.initialTagging)
                    else:
                        tagged = self.tagger.tag_raw_line(' '.join([w.content for w in batchWords]))

                    for wordStr in tagged.split(' '):
                        partOfSpeech = wordStr.split('ᚽ')[1]
                        tags.append(partOfSpeech)
                tags.append('NOUN')
                batchWords = []
            else:
                batchWords.append(word)

        if batchWords:
            if custom_initial_tagging:
                tagged = self.tagger.tag_raw_line(' '.join([w.content for w in batchWords]), self.initialTagging)
            else:
                tagged = self.tagger.tag_raw_line(' '.join([w.content for w in batchWords]))

            for wordStr in tagged.split(' '):
                partOfSpeech = wordStr.split('ᚽ')[1]
                tags.append(partOfSpeech)

        for index, word in enumerate(self.words):
            word.partOfSpeech = tags[index]

        assert len(self.words) == len(tags)

    def initialTagging(self, sentence):
        words = sentence.strip().split()
        taggedSen = []
        for word in words:
            if self.helpers.is_punct(word):
                tag = 'PUNCT'
            elif word in self.pos.keys():
                tag = self.pos[word]
            # elif word in DEFAULTPOS:
            #     tag = DEFAULTPOS[word]
            else:
                tag = 'OOV'

            taggedSen.append(word + "ᚽ" + tag)

        return " ".join(taggedSen)

    def get_expanded_vocab(self, update=False):
        """
        Opens or generates the expanded lexicon from the DICT file
        :param update: if True, recreates the expanded lexicon even if it exists
        :return: a dict containing the expanded lexicon
        """
        sep = ' '
        if os.path.isfile(self.expanded_vocab_path) and not update:
            with open(self.expanded_vocab_path, 'r', encoding='utf-8') as f:
                content = f.read().strip().split('\n')
                return dict([tuple(line.split(sep)) for line in content])
        else:
            pos = self.tagger.dictionary
            pos.update(self.expandWithAffixes(pos))
            with open(self.expanded_vocab_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(['{}{}{}'.format(word, sep, tag) for word, tag in pos.items()]))
            return pos

    def expandWithAffixes(self, vocab):
        tsek = '་'
        yang_4 = ["ི", "ུ", "ེ", "ོ"]
        endings = {"འི": "ai", "ས": "s", "ར": "r", "འམ": "am", "འང": "ang", "འོ": "ao"}
        new_entries = {}
        sc = getSylComponents()
        words = vocab.keys()
        for word in words:
            ending = ''
            if word.endswith(tsek):
                ending += tsek
                word = word[:-1]
            starting = ''
            if word.startswith(tsek):
                starting += tsek
                word = word[1:]

            if sc.is_affixable(word):
                if tsek in word:
                    syls = word.split(tsek)
                    beginning = tsek.join(syls[:-1]) + tsek
                    root = syls[-1]
                else:
                    beginning = ''
                    root = word

                suffix = ''
                if root.endswith('འ'):
                    suffix += 'འ'
                    root = root[:-1]

                if len(suffix) > 0 and suffix[0] in yang_4:
                    root += suffix[0]
                    suffix = suffix[1:]

                for affix, feature in endings.items():
                    affixed = '{}{}{}ᛰ{}{}'.format(starting, beginning, root, affix, ending)
                    affixed_pos = '{}_{}_{}'.format(vocab[word+ending], feature, suffix)
                    new_entries[affixed] = affixed_pos
        return new_entries


class Helpers:
    def __init__(self):
        # separate non-tibetan punctuation from the rest (pytib does tib punct)
        self.non_bo_punct = re.compile(r'''[\!\"\#\$\%\&\'\[\]\*\+\,
                        \-\\\.\/0123456789\:\;\<\=\>\?\@\~\_\^
                        ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×÷
                        ‐‑‒–—―‖‗‘’‚‛“”„‟†‡•‣․‥…‧‰‱′″‴‵‶‷‸‹›
                        ※‼‽‾‿⁀⁁⁂⁃⁄⁅⁆⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁒⁓⁔⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞ƒ\(\)
                        、。〃〄々〆〇〈〉《》「」『』【】〒〓〔〕〖〗〘〙〚〛〜〝〞〟〠〡〢〣〤〥
                        〦〧〨〩〪〭〮〯〫〬〰〱〲〳〴〵〶〷〸〹〺〻〼〽〾〿
                        ①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⓪
                        ⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾⓿]+''', re.X)

    def is_punct(self, word):
        if re.findall(self.non_bo_punct, word):
            return True
        return False

    def normalize_punct_of(self, text):
        return re.sub(self.non_bo_punct, r' \g<0> ', text)
