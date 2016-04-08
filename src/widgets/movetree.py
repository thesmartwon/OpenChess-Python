from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics)
from PyQt5.QtWidgets import QTableView, QMenu, QHeaderView
import itertools
from chess import pgn
import strings


class MoveTreeView(QTableView):
    moveItemScrolled = pyqtSignal(pgn.GameNode)

    def __init__(self, parent, model):
        super().__init__(parent)
        self.setModel(model)
        self.initUI()

    def initUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.blue)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        met = QFontMetrics(self.font())
        maxFile = max([met.width(c) for c in strings.FILE_NAMES])
        maxRank = max([met.width(c) for c in strings.RANK_NAMES])
        maxPiece = max([met.width(c) for c in strings.PIECE_SYMBOLS])
        maxEnd = max([met.width(c) for c in ['+', '#']])
        maxTake = met.width('x')
        maxItemWidth = maxPiece + maxRank * 2 + maxFile * 2 + maxTake + maxEnd
        self.maxHeaderWidth = met.width('000')
        self.vScrollBarWidth = 17
        self.setMinimumWidth(maxItemWidth * 2 + self.maxHeaderWidth +
                             self.vScrollBarWidth)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.displayContextMenu)
        self.setSelectionMode(QTableView.SingleSelection)

    def displayContextMenu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            # self.model().itemFromIndex(index)
            menu = QMenu(self)
            flipAction = menu.addAction("Flip board")
            newGameAction = menu.addAction("New game")
            action = menu.popup(self.mapToGlobal(point))
        else:
            menu = QMenu(self)
            flipAction = menu.addAction("movetreeviewstuff")
            newGameAction = menu.addAction("movetreeviewstuff2")
            action = menu.popup(self.mapToGlobal(point))

    def entryAdded(self, row, col):
        if row == self.model().rowCount() - 1:
            self.scrollToBottom()
        else:
            self.scrollTo(self.model().index(row, col))
        self.setCurrentIndex(self.model().index(row, col))

    def currentChanged(self, newCur, oldCur):
        if newCur.isValid():
            moveItem = self.model().itemFromIndex(newCur)

            if type(moveItem) == MoveTreeItem:
                self.moveItemScrolled.emit(moveItem.gameNode)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            pass
        event.ignore()


class MoveTreeModel(QStandardItemModel):
    moveItemAdded = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        # self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
        #                                 strings.COLOR_SECOND])
        self.reset()

    def readTree(self, gameNode):
        turn = gameNode.board().turn
        self.curCol = int(not turn)
        # The mainline move goes first.
        if gameNode.variations:
            main_variation = gameNode.variations[0]
            fullMoveNum = main_variation.parent.board().fullmove_number
            itemThere = self.item(self.curRow, self.curCol)
            if not itemThere or type(itemThere) == QStandardItem:
                newItem = MoveTreeItem(main_variation)
                self.setItem(self.curRow, self.curCol, newItem)
                self.setHeaderData(self.curRow, Qt.Vertical,
                                   str(fullMoveNum))
                # print('made moveWidg', newItem)
            if not turn:
                self.curRow += 1
        # Then visit sidelines.
        for v in itertools.islice(gameNode.variations, 1, None):
            if not v.is_main_variation():
                newItem = QStandardItem('var' + str(v.move))
                self.setItem(self.curRow, self.curCol, newItem)
                # print('made variation', self.curRow, self.curCol, v.move)
                self.curRow += 1
        # The mainline is continued last.
        if gameNode.variations:
            self.readTree(main_variation)

    def updateAfterMove(self, newNode):
        if newNode.is_main_line():
            fullMoveNum = newNode.parent.board().fullmove_number
            newItem = MoveTreeItem(newNode)
            self.setItem(self.curRow, self.curCol, newItem)
            self.setHeaderData(self.curRow, self.curCol, str(fullMoveNum))
            self.moveItemAdded.emit(self.curRow, self.curCol)
            if self.curCol == 0:
                self.curCol = 1
            else:
                self.curRow += 1
                self.curCol = 0
        else:
            print('making variation')

    def reset(self, rootNode=None):
        self.clear()
        self.setItem(0, 0, QStandardItem('...'))
        self.setItem(0, 1, QStandardItem(''))
        self.curRow = 0
        self.curCol = 0
        if rootNode:
            print('tree reset')
            self.readTree(rootNode.root())
            self.moveItemAdded.emit(self.curRow, self.curCol)

    # def itemClicked(self, current):
    #     # Because of self.setSelectionMode(QTableView.SingleSelection)
    #     # current will always be the selected move
    #     if current.isValid():
    #         moveItem = self.itemFromIndex(current)
    #         # current.model().itemFromIndex(current)
    #         if type(moveItem) == MoveTreeItem:
    #             self.moveItemClicked.emit(moveItem.gameNode)


class MoveTreeItem(QStandardItem):
    def __init__(self, gameNode):
        super().__init__()
        self.gameNode = gameNode
        self.moveSan = gameNode.parent.board().san(gameNode.move)
        self.setText(self.moveSan)

    def clicked(self, event):
        print('yea')

    def __repr__(self):
        i = self.index()
        return '%d, %d, move %s' % (i.row(), i.column(), self.moveSan)
