import os
import logging

def createLogger(loggerName='', loggingFile=None, loggingLevel=logging.INFO,
                 formatter=None, clear=False):
    """
    Create specified logger with our default configuration for package.

    @param loggerName Logger name.
    @param loggingFile Logging file, None if you want to output to stdout.
    @param loggingLevel Logging level.
    @param formatter Logging format, None if you want to use our default.
    @param clear Clear existed logging file if True.
    @return Logger.
    """
    # Set up a specific logger with our desired output level.
    logger = logging.getLogger(loggerName)
    logger.setLevel(loggingLevel)

    created = False
    if logger.handlers:
        if loggingFile:
            absoultPath = os.path.abspath(loggingFile)
            for _handler in logger.handlers:
                if (isinstance(_handler, logging.FileHandler)) and (
                    absoultPath == _handler.baseFilename):
                    created = True
                    break
        else:
            for _handler in logger.handlers:
                if isinstance(_handler, logging.StreamHandler):
                    created = True
                    break
    if not created: # Add the log message handler to the logger.
        if loggingFile:
            handler = logging.FileHandler(loggingFile)
            if clear and os.path.exists(loggingFile):
                try:
                    os.remove(loggingFile)
                except:
                    pass
        else:
            handler = logging.StreamHandler()

        if not formatter:
            formatter = (
                "%(asctime)s - %(levelname)s - "
                "Thread: %(threadName)s(%(thread)d) - %(name)s - %(message)s")
            formatter = logging.Formatter(formatter)

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def createDebugLogger(name, fileName, formatter=None, clear=False):
    """
    Shortcut to create logger for debugging.

    @param name Logger name.
    @param fileName Logging file, None if you want to output to stdout.
    @param formatter Logging format, None if you want to use our default.
    @param clear Clear existed logging file if True.
    @return Logger.
    """
    return createLogger(name, fileName, logging.DEBUG, formatter, clear)

import pybo
import botok
import re

#for en
class MyToken(botok.tokenizers.token.Token):
    def __init__(self, text=""):
        super().__init__()
        self.text = f'{text} '

    @property
    def text_unaffixed(self):
        return self.text.strip(' ')

class EngTokenizer(pybo.WordTokenizer):
    def tokenize(self, string, split_affixes=True, spaces_as_punct=False, debug=False):
        if string == '\n':
            result = [MyToken(string)]
            result[-1].text = result[-1].text.strip(' ') # 最後一個token 不要加空白
#             result[0].text = f'{result[0].text}\n'
        elif '＃' in string or '\n' in string or ' ' in string:
            tokens = re.split('＃| ', string)
            indexs = [i for i, s in enumerate(tokens) if '\n' in s]
            if indexs:
                tokens = re.split('＃| |\n', string)

            result = [MyToken(t) for t in tokens]
            insertBreakLineCount = 0
            for i, index in enumerate(indexs):
                if i != 0:
                    # 用 \n 分完會多 token 為 " "，第二個後 \n 前面沒有，所以不用加
                    index = index + i + insertBreakLineCount

                currentResultLen = len(result)
                if index + 1 <= currentResultLen - 1:
                    result.insert(index + 1, MyToken('\n'))
                    # 換行那行不要加空白
                    result[index + 1].text = result[index + 1].text.strip(' ')
                    insertBreakLineCount += 1

            beDelList = []
            for i, e in enumerate(result):
                if e.text == '\n':
                    # 換行前與當前 token 的字不要加空白
                    result[i - 1].text = result[i - 1].text.strip(' ')
                    result[i].text = result[i].text.strip(' ')

                if not result[i].text or result[i].text == " ":
                    beDelList.append(i)

            for i, beDel in enumerate(beDelList):
                del result[beDel - i]

            result[-1].text = result[-1].text.strip(' ') # 最後一個token 不要加空白

        else:
            result = []


        return result

