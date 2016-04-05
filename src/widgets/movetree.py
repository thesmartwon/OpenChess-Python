from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics)
from PyQt5.QtWidgets import QTableView, QMenu, QHeaderView
from chess import pgn
import strings


class MoveTreeView(QTableView):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setModel(model)
        self.initUI()

    def initUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.red)
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
        self.setSelectionBehavior(QTableView.SelectItems)
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


class MoveTreeModel(QStandardItemModel):
    moveItemClicked = pyqtSignal(pgn.GameNode)

    def __init__(self):
        super().__init__()
        # self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
        #                                 strings.COLOR_SECOND])
        self.setItem(0, 0, QStandardItem('...'))
        self.setItem(0, 1, QStandardItem(''))
        self.curRow = 0
        self.curCol = 0

    def updateTree(self, gameNode):
        # TODO: this is slow. maybe use visitors?
        for v in gameNode.variations:
            turn = v.parent.board().turn
            self.col = int(not turn)
            if v.is_main_line():
                fullMoveNum = v.parent.board().fullmove_number
                turn = v.parent.board().turn
                itemThere = self.item(self.row, self.col)
                if not itemThere or type(itemThere) == QStandardItem:
                    newItem = MoveTreeItem(v)
                    self.setItem(self.row, self.col, newItem)
                    self.setHeaderData(self.row, Qt.Vertical, str(fullMoveNum))
                    print('made moveWidg', newItem)
                if not turn:
                    self.row += 1
                if not v.is_end():
                    self.updateTree(v)
            else:
                print('making variation', self.row, self.col)
                self.row += 1

    def updateAfterMove(self, newGameNode):
        # self.updateTree(newGameNode.root())
        if newGameNode.is_main_line():
            fullMoveNum = newGameNode.parent.board().fullmove_number
            turn = newGameNode.parent.board().turn
            newItem = MoveTreeItem(newGameNode)
            self.setItem(self.curRow, self.curCol, newItem)
            self.setHeaderData(self.curRow, self.curCol, str(fullMoveNum))
            if self.curCol == 0:
                self.curCol += 1
            else:
                self.curRow += 1
                self.curCol = 0
        else:
            print('making variation')

    def reset(self, newGame):
        # TODO: implement
        self.clear()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])

    def eraseAfterPly(self, plyNumber):
        rowNumber = int(plyNumber / 2) + 1
        numToErase = self.rowCount() - int(plyNumber / 2) - 1
        self.removeRows(rowNumber, numToErase)
        if plyNumber % 2 == 0:
            self.setItem(int(plyNumber) / 2, 1, QStandardItem())

    def itemClicked(self, current):
        # Because of self.setSelectionMode(QTableView.SingleSelection)
        # current will always be the selected move
        if current.isValid():
            moveItem = self.itemFromIndex(current)
            # current.model().itemFromIndex(current)
            if type(moveItem) == MoveTreeItem:
                print('clicked', moveItem)
                self.moveItemClicked.emit(moveItem.moveNode)


class MoveTreeItem(QStandardItem):
    def __init__(self, moveNode):
        super().__init__()
        self.moveNode = moveNode
        self.moveSan = moveNode.parent.board().san(moveNode.move)
        self.setText(self.moveSan)

    def clicked(self, event):
        print('yea')

    def __repr__(self):
        i = self.index()
        return '%d, %d, move %s' % (i.row(), i.column(), self.moveSan)
