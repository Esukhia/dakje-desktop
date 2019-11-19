from PyQt5 import QtGui
from dakje.storage.models import Format

# class Format(QtGui.QTextFormat):
#     def __init__(self):
#         super().__init__()
#
#     def toQColor(self, hex):
#         r, g, b = hex[1:3], hex[3:5], hex[5:7]
#         return QtGui.QColor(int(r, 16), int(g, 16), int(b, 16))

class FormatManager:
    LEVEL_FORMAT_COLORS = dict()
    LEVEL_FORMATS = dict()  # generate by LEVEL_FORMAT_COLORS

    # default values
    LEVEL_FORMAT_COLORS = {
    1: '#87a840',
    2: '#ddc328',
    3: '#b63226',
    4: '#278da9',
    # 5: '#363d5c',
    None: '#363d5c'
    }

    for format in Format.objects.all():
        if format.level == 0:        
            LEVEL_FORMAT_COLORS[None] = format.color
        else:
            LEVEL_FORMAT_COLORS[format.level] = format.color
        # print('format.color', format.color)
        # print('format.level', format.level)

    POS_FORMAT_COLORS = {
        1: '#363d5c',
        2: '#87a840',
        3: '#ddc328'
    }
    POS_FORMATS = {}

    def __init__(self, editor):
        self.editor = editor

        for level, color in self.LEVEL_FORMAT_COLORS.items():
            format = QtGui.QTextCharFormat()
            format.setForeground(self.toQColor(color))
            self.LEVEL_FORMATS[level] = format

        for level, color in self.POS_FORMAT_COLORS.items():
            format = QtGui.QTextCharFormat()
            format.setForeground(self.toQColor(color))
            self.POS_FORMATS[level] = format

    def toQColor(self, hex):
        r, g, b = hex[1:3], hex[3:5], hex[5:7]
        return QtGui.QColor(int(r, 15), int(g, 16), int(b, 16))
