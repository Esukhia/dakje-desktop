from PyQt5 import QtCore, QtGui, QtWidgets


from horology import timed

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor

    @timed
    def highlightBlock(self, text):
        currentBlock = self.currentBlock()

        if self.editor.isLevelMode():

            highlightedLevels = self.editor.getHighlightedLevels()

            for token in self.editor.tokens:

                format = self.editor.formatManager.LEVEL_FORMATS[token.level]

                if self.editor.viewManager.isTagView():
                    # format text string
                    textLen = len(token.text)
                    textStart = (token.start - currentBlock.position())
                    textSpan = textLen
                    if token.level in highlightedLevels:
                        self.setFormat(textStart, textSpan, format)

                    # format tags
                    tagFormat = self.editor.formatManager.TAG_FORMAT
                    tagStart = (
                        token.start - currentBlock.position()) + textLen
                    tagSpan = token.length - textLen
                    self.setFormat(tagStart, tagSpan, tagFormat)

                else:
                    # only format what's in the level lists
                    if token.level in highlightedLevels:
                        self.setFormat(
                            token.start - currentBlock.position(), token.length, format)


        # else:  # editor mode
            # highlightedPoses = self.editor.getHighlightedPoses()
            # for token in self.editor.tokens:
            #     if token.pos not in highlightedPoses:
            #         continue
            #     self.setFormat(
            #         token.start - currentBlock.position(), token.length,
            #         self.editor.formatManager.POS_FORMATS[
            #             self.editor.getPosRank(token.pos)]
            #     )
