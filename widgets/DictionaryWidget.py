import os

from collections import OrderedDict

from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel, QAbstractTableModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QFormLayout, QHBoxLayout,
    QDialog, QHeaderView, QTableView, QMessageBox
)

from pybo import BasicTrie, PyBoTrie, Config
from pybo import BoSyl
from pathlib import Path

from storage.models import Dict


class TableModel(QAbstractTableModel):
    def __init__(self, parent, data, header):
        QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.data = data
        self.header = header

    @property
    def editor(self):
        return self.parent.parent

    @property
    def bt(self):
        return self.editor.bt

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
        # TODO: using cache (compare self.data before & after)
        pyboDict = self.parent.pyboDict.copy()

        warningBlank = False
        warningTags = False
        tags = self.parent.getAllTags()

        for key, value in self.data:
            if not key or not value:
                # warning for blank fields
                if not warningBlank:
                    QMessageBox.warning(
                        self.parent,
                        'Blank fields Warning!',
                        'The blank fields will not be saved.',
                        buttons=QMessageBox.Ok
                    )
                    warningBlank = True

            # key and value
            else:
                # warning for non_existent tags
                if not warningTags:
                    if value not in tags:
                        QMessageBox.warning(
                            self.parent,
                            'Tags Warning!',
                            'The tag "' + value + '" is not used by other words.',
                            buttons=QMessageBox.Ok
                        )
                        warningTags = True

                # save normals
                if key in pyboDict:
                    pos = pyboDict[key]

                    del pyboDict[key]
                    # the remains means tokens to be deleted

                    if pos == value:
                        # totally same with pybo
                        continue
                try:
                    # if record exists, cover it
                    dict = Dict.objects.get(content=key)
                    dict.pos = value
                    dict.save()

                except Dict.DoesNotExist:
                    # create new
                    Dict.objects.create(content=key, pos=value,
                                        action=Dict.ACTION_ADD)

        for key, value in pyboDict.items():
            Dict.objects.get_or_create(content=key, pos=value,
                                       action=Dict.ACTION_DELETE)

        self.editor.refreshView()
        self.editor.refreshCoverage()


class DictionaryEditorWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.pyboDict = dict()
        self.initPyboDict()

        self.tokens = []
        self.resize(400, 600)
        self.setWindowTitle('Dictionary Editor')
        self.setupTable()
        self.initUI()

    def getDict(self):
        mergedDict = self.pyboDict.copy()
        # mergedDict = {'ཉམ་ཐག་པ': 'VERB'}

        for dict in Dict.objects.all():
            if dict.action == Dict.ACTION_ADD:
                mergedDict[dict.content] = dict.pos
            else:  # Dict.ACTION_DELETE
                del mergedDict[dict.content]

        return mergedDict

    def setupTable(self):
        dict = self.getDict()
        self.model = TableModel(
            parent=self,
            header=('Text', 'Tag'),
            data=[[k, v] for k, v in dict.items()]
        )

        # print(self.model.bt.has_word('ནང་ཆོས་'))

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.eventFilter = lambda: self.removeButton.setDisabled(True)

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
        self.addButton.setIcon(QIcon('icons/add.png'))
        self.addButton.setIconSize(QSize(30, 30))
        self.addButton.clicked.connect(self.addWord)

        self.removeButton = QPushButton()
        self.removeButton.setFlat(True)
        self.removeButton.setIcon(QIcon('icons/delete.png'))
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

    def initPyboDict(self):
        import pkg_resources
        resourcePkg = 'pybo'
        resourcePath = '/'.join(('resources', 'trie', 'Tibetan.DICT'))
        reader = pkg_resources.resource_stream(resourcePkg, resourcePath)
        file = reader.read()

        for line in file.decode().splitlines():
            key, val = line.split()
            self.pyboDict[key] = val

        file.decode()
        reader.close()

    def removeWord(self):
        rows = sorted(set(index.row() for index in
                          self.tableView.selectionModel().selectedIndexes()))
        for row in reversed(rows):
            self.model.data.pop(row)
        self.model.saveDict()

    def addWord(self, content=None):
        if content is not None:
            self.model.data.insert(0, [content, ''])
        else:
            self.model.data.insert(0, ['', ''])
        self.model.layoutChanged.emit()

    def getAllTags(self):
         return set(self.getDict().values())
