import os

from collections import OrderedDict

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QAbstractTableModel
from PyQt5.QtGui import QTextCursor, QPalette, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton, QMainWindow,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QMessageBox
)

class TableModel(QAbstractTableModel):
    def __init__(self, parent, data, header):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.data = data
        self.header = header

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data[0])

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self.data[index.row()][index.column()]

    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.EditRole:
            return None
        self.data[index.row()][index.column()] = value
        self.saveDict()
        return True

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def saveDict(self):
        pyboDict = self.parent.pyboDict.copy()
        userDict = OrderedDict()

        warningBlank = False
        warningTags = False
        tags = self.parent.getAllTags()

        # user's words and pybo default words
        for key, value in self.data:
            # warning for blank fields
            if not key or not value:
                if not warningBlank:
                    QMessageBox.warning(
                        self.parent,
                        'Blank fields Warning!',
                        'The blank fields will not be saved.',
                        buttons=QMessageBox.Ok
                    )
                    warningBlank = True
                if key in pyboDict:
                    pyboDict.pop(key)
                continue

            # warning for non_existent tags
            if not warningTags:
                if value not in tags:
                    QMessageBox.warning(
                        self.parent,
                        'Tags Warning!',
                        'The tag "{}" is not used by other words.'.format(value),
                        buttons=QMessageBox.Ok
                    )
                    warningTags = True

            if key in pyboDict:
                if pyboDict[key] == value:
                    pyboDict.pop(key)
                    continue
            userDict[key] = value
            pyboDict.pop(key)

        # removed words
        for key, value in pyboDict.items():
            key = '--' + key
            userDict[key] = value

        # write user dict
        with open(self.parent.userDictPath, 'w', encoding='UTF-8') as f:
            for key, value in userDict.items():
                f.write(key + ' ' + value + '\n')

class DictionaryEditorWidget(QDialog):
    userDictPath = os.path.join('files', 'DICT', 'User.DICT')
    pyboDictPath = os.path.join('files', 'DICT', 'Tibetan.DICT')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.pyboDict = self.getPyboDict()
        self.userDict = self.getUserDict()
        self.tokens = []
        self.resize(400, 600)
        self.setWindowTitle('Dictionary Editor')
        self.setupTable()
        self.initUI()

    @property
    def dict(self):
        mergedDict = self.pyboDict.copy()
        for key, value in  self.userDict.items():
            removed = False
            if key.startswith('--'):
                removed = True
                key = key[2:]
            if removed:
                mergedDict.pop(key)
            else:
                mergedDict[key] = value
        return mergedDict

    def setupTable(self):
        self.model = TableModel(
            parent=self,
            header=('Text', 'Tag'),
            data=[[k, v] for k, v in self.dict.items()]
        )
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableView.setFixedHeight(500)
        self.tableView.setModel(self.proxyModel)

    def initUI(self):
        self.searchLabel = QLabel()
        self.searchLabel.setPixmap(
            QIcon('files/searching').pixmap(QSize(30, 30)))

        self.searchField = QLineEdit()
        self.searchField.textChanged.connect(self.search)

        hbox = QHBoxLayout()
        hbox.addWidget(self.searchLabel)
        hbox.addWidget(self.searchField)

        self.addButton = QPushButton()
        self.addButton.setFlat(True)
        self.addButton.setIcon(QIcon('files/add.png'))
        self.addButton.setIconSize(QSize(30, 30))
        self.addButton.clicked.connect(self.addWord)

        self.removeButton = QPushButton()
        self.removeButton.setFlat(True)
        self.removeButton.setIcon(QIcon('files/delete.png'))
        self.removeButton.setIconSize(QSize(30, 30))
        self.removeButton.clicked.connect(self.removeWord)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.addButton)
        hbox2.addStretch()
        hbox2.addWidget(self.removeButton)

        self.fbox = QFormLayout()
        self.fbox.addRow(hbox)
        self.fbox.addRow(hbox2)
        self.fbox.addRow(self.tableView)

        self.setLayout(self.fbox)

    def search(self, text):
        self.proxyModel.setFilterKeyColumn(-1)  # -1 means all cols
        self.proxyModel.setFilterFixedString(text)

    def getPyboDict(self):
        if not os.path.isfile(self.pyboDictPath):
            self.downloadPyboDict()
        return self.getDict(self.pyboDictPath)

    def downloadPyboDict(self):
        import pkg_resources
        resourcePkg = 'pybo'
        resourcePath = '/'.join(('resources', 'trie', 'Tibetan.DICT'))
        reader = pkg_resources.resource_stream(resourcePkg, resourcePath)
        file = reader.read()
        reader.close()

        with open(self.pyboDictPath, 'w', encoding='UTF-8') as f:
            f.write(file.decode())

    def getUserDict(self):
        if not os.path.isfile(self.userDictPath):
            with open(self.userDictPath, 'w', encoding='UTF-8') as f:
                f.write('')
        return self.getDict(self.userDictPath)

    def getDict(self, filename):
        dictionary = OrderedDict()
        with open(filename, 'r', encoding='UTF-8') as f:
            rows = f.readlines()
            for row in rows:
                content, tag = row.split()
                dictionary[content] = tag
        return dictionary

    def removeWord(self):
        rows = sorted(set(index.row() for index in
                          self.tableView.selectionModel().selectedIndexes()))
        for row in reversed(rows):
            self.model.data.pop(row)
        self.model.saveDict()

    def addWord(self):
        self.model.data.insert(0, ['...', '...'])
        self.model.layoutChanged.emit()

    def getAllTags(self):
         pyboTags = set(value for key, value in self.pyboDict.items())
         userTags = set(value for key, value in self.getUserDict().items())
         return pyboTags | userTags
