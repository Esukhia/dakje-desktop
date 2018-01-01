# -*- coding: utf-8 -*-
import re


def is_punct(word):
    non_bo_punct = re.compile(r'''[\!\"\#\$\%\&\'\[\]\*\+\,
                \-\\\.\/0123456789\:\;\<\=\>\?\@\~\_\^
                ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿×÷
                ‐‑‒–—―‖‗‘’‚‛“”„‟†‡•‣․‥…‧‰‱′″‴‵‶‷‸‹›
                ※‼‽‾‿⁀⁁⁂⁃⁄⁅⁆⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁒⁓⁔⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞ƒ\(\)
                、。〃〄々〆〇〈〉《》「」『』【】〒〓〔〕〖〗〘〙〚〛〜〝〞〟〠〡〢〣〤〥
                〦〧〨〩〪〭〮〯〫〬〰〱〲〳〴〵〶〷〸〹〺〻〼〽〾〿
                ①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⓪
                ⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾⓿]+''', re.X)
    if re.findall(non_bo_punct, word):
        return True
    return False


def initializeBoSentence(FREQDICT, sentence):
    words = sentence.strip().split()
    taggedSen = []
    for word in words:
        if is_punct(word):
            tag = 'PUNCT'
        elif word in FREQDICT:
            tag = FREQDICT[word]
        # elif word in DEFAULTPOS:
        #     tag = DEFAULTPOS[word]
        else:
            tag = 'OOV'

        taggedSen.append(word + "ᚽ" + tag)

    return " ".join(taggedSen)


def initializeBoCorpus(FREQDICT, inputFile, outputFile):
    lines = open(inputFile, "r").readlines()
    with open(outputFile, "w") as fileOut:
        for line in lines:
            fileOut.write(initializeBoSentence(FREQDICT, line) + "\n")
