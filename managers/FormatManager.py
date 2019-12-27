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
    TAG_FORMAT = QtGui.QTextCharFormat()

    # default values based on Ayu theme
    LEVEL_FORMAT_COLORS = {
    1: '#10a4ed', # blue
    2: '#8EB811', # green
    3: '#f29718', # yellow
    # 3: '#10a4ed', # blue
    4: '#a782d2', # purple
    # 5: 'f2590c', # orange
    None: '#e01a1a' # red
    }

    for format in Format.objects.all():
        if format.level == 0:        
            LEVEL_FORMAT_COLORS[None] = format.color
        else:
            LEVEL_FORMAT_COLORS[format.level] = format.color

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

        self.TAG_FORMAT.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
        self.TAG_FORMAT.setForeground(self.toQColor('#a0a0a4'))

    def toQColor(self, hex):
        r, g, b = hex[1:3], hex[3:5], hex[5:7]
        return QtGui.QColor(int(r, 16), int(g, 16), int(b, 16))
