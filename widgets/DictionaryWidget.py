import sys
import pkg_resources

from collections import OrderedDict

from PyQt5.QtCore import Qt, QStringListModel, QSize, QSortFilterProxyModel, QAbstractTableModel
from PyQt5.QtGui import QTextCursor, QPalette, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QWidget, QTextEdit, QCompleter, QComboBox, QPushButton, QMainWindow,
    QLabel, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, QDialog,

    QTableWidget, QTableWidgetItem, QHeaderView, QTableView
)

class TableModel(QAbstractTableModel):
    def __init__(self, parent, data, header):
        QAbstractTableModel.__init__(self, parent)
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
        return True

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None


class DictionaryEditorWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dict = self.getDictionary()
        self.tokens = []
        self.resize(400, 600)
        self.setWindowTitle('Dictionary Editor')
        self.setupTable()
        self.initUI()

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

        self.removeButton = QPushButton()
        self.removeButton.setFlat(True)
        self.removeButton.setIcon(QIcon('files/delete.png'))
        self.removeButton.setIconSize(QSize(30, 30))

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

    def getDictionary(self, fromPybo=True):
        dictionary = OrderedDict()

        if fromPybo:
            resourcePkg = 'pybo'
            resourcePath = '/'.join(('resources', 'trie', 'Tibetan.DICT'))

            reader = pkg_resources.resource_stream(resourcePkg, resourcePath)
        else:
            reader = open('Tibetan.DICT', 'rb')

        rows = reader.readlines()
        reader.close()

        for row in rows:
            content, tag = row.decode().split()
            dictionary.setdefault(content, tag)

        return dictionary
