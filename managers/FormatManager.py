from PyQt5 import QtCore, QtGui, QtWidgets

# class Format(QtGui.QTextFormat):
#     def __init__(self):
#         super().__init__()
#
#     def toQColor(self, hex):
#         r, g, b = hex[1:3], hex[3:5], hex[5:7]
#         return QtGui.QColor(int(r, 16), int(g, 16), int(b, 16))

class FormatManager:
    LEVEL_FORMAT_COLORS = {
        1: '#87a840',
        2: '#ddc328',
        3: '#b63226',
        4: '#278da9',
        # 5: '#363d5c',
        None: '#363d5c'
    }
    LEVEL_FORMATS = {}  # generate by LEVEL_FORMAT_COLORS

    def __init__(self, editor):
        self.editor = editor

        for level, color in self.LEVEL_FORMAT_COLORS.items():
            format = QtGui.QTextCharFormat()
            format.setForeground(self.toQColor(color))
            self.LEVEL_FORMATS[level] = format

    def toQColor(self, hex):
        r, g, b = hex[1:3], hex[3:5], hex[5:7]
        return QtGui.QColor(int(r, 16), int(g, 16), int(b, 16))
