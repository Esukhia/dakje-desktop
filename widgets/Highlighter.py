import time
import logging
from functools import wraps
from PyQt5 import QtCore, QtGui, QtWidgets


logger = logging.getLogger(__name__)

# Timed decorator
def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(
            func.__name__, round(end - start, 5)))
        return result
    return wrapper


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
    
    # @timed
    def highlightBlock(self, p_str):
        currentBlock = self.currentBlock()

        # the positions here are relative to the current block
        # FIXME: Temporally Highlight All Words

        if self.editor.isLevelMode():
            highlightedLevels = self.editor.getHighlightedLevels()
            for token in self.editor.tokens:
                if token.level not in highlightedLevels:
                    continue

                self.setFormat(
                    token.start - currentBlock.position(), token.length,
                    self.editor.formatManager.LEVEL_FORMATS[token.level]
                )

        else:  # editor mode
            highlightedPoses = self.editor.getHighlightedPoses()
            for token in self.editor.tokens:
                if token.pos not in highlightedPoses:
                    continue

                self.setFormat(
                    token.start - currentBlock.position(), token.length,
                    self.editor.formatManager.POS_FORMATS[
                        self.editor.getPosRank(token.pos)]
                )
