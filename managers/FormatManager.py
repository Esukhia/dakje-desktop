from PyQt5 import QtCore, QtGui, QtWidgets
from storage.models import Format

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

    # default values based on Ayu theme
    LEVEL_FORMAT_COLORS = {
    1: '#f29718', # yellow
    2: '#8EB811', # green
    3: '#00A0EC', # blue
    # 2: '#a478ce', # purple
    # 4: 'f2590c', # orange
    None: 'f2590c'
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
