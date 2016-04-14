from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics, QKeySequence)
from PyQt5.QtWidgets import QTableView, QMenu, QHeaderView
import itertools
from chess import pgn
import strings
import userConfig


class MoveTreeView(QTableView):
    moveItemScrolled = pyqtSignal(pgn.GameNode)
    scrolledInDirection = pyqtSignal(int, bool, bool)
    prevShortcuts = [QKeySequence(s.strip())[0] for s in
                     userConfig.config['HOTKEYS']['prevmove'].split(',')]
    nextShortcuts = [QKeySequence(s.strip())[0] for s in
                     userConfig.config['HOTKEYS']['nextmove'].split(',')]
    nextVarShortcuts = [QKeySequence(s.strip())[0] for s in userConfig
                        .config['HOTKEYS']['nextvariation'].split(',')]
    prevVarShortcuts = [QKeySequence(s.strip())[0] for s in userConfig
                        .config['HOTKEYS']['prevvariation'].split(',')]

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

    def entryScrolled(self, moveNode):
        """
        Happens when game or model asks us to scroll without changing the
        current tree
        """
        item = self.model().findNode(moveNode)
        if item:
            self.setCurrentIndex(item)
        else:
            self.clearSelection()

    def currentChanged(self, newCur, oldCur):
        if newCur.isValid():
            moveItem = self.model().itemFromIndex(newCur)
            self.scrollTo(newCur)
            if type(moveItem) == MoveTreeItem:
                self.moveItemScrolled.emit(moveItem.gameNode)

    def keyPressEvent(self, event):
        keyCode = QKeySequence(event.modifiers() | event.key())[0]
        if keyCode in self.prevShortcuts:
            event.accept()
            self.scrolledInDirection.emit(-1, True, False)
        elif keyCode in self.nextShortcuts:
            event.accept()
            self.scrolledInDirection.emit(1, True, False)
        elif keyCode in self.prevVarShortcuts:
            if self.model().hasVariations:
                event.accept()
                self.scrolledInDirection.emit(-1, False, True)
        elif keyCode in self.nextVarShortcuts:
            if self.model().hasVariations:
                event.accept()
                self.scrolledInDirection.emit(1, False, True)


class MoveTreeModel(QStandardItemModel):
    moveItemAdded = pyqtSignal(pgn.GameNode)

    def __init__(self, parent):
        super().__init__(parent)
        # self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
        #                                 strings.COLOR_SECOND])
        self.reset()

    def findNode(self, gameNode):
        # This is ridiculous. Has to be a better way to search
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                item = self.itemFromIndex(self.index(r, c))
                if type(item) == MoveTreeItem and item.gameNode == gameNode:
                    return self.index(r, c)
        return None

    def createMoveTreeItem(self, gameNode):
        if gameNode.parent.parent:
            prevItem = self.findNode(gameNode.parent)
            curRow = prevItem.row()
            curCol = prevItem.column()
            if curCol == 1:
                curRow += 1
                curCol = 0
            else:
                curCol += 1
        else:
            curRow = 0
            curCol = 0
        print('cur', curRow, curCol)
        newItem = MoveTreeItem(gameNode)
        if gameNode.is_main_line():
            self.setItem(curRow, curCol, newItem)
        elif gameNode.is_main_variation():
            self.setItem(curRow, curCol, newItem)
            print('made variation line', gameNode.move)
        else:
            if gameNode.board().turn:
                list = [newItem, QStandardItem('')]
            else:
                list = [QStandardItem(''), newItem]
            self.insertRow(curRow, list)
            print('made variation', gameNode.move)
            self.hasVariations = True
        header = str(gameNode.parent.board().fullmove_number)
        self.setHeaderData(curRow, Qt.Vertical, header)

    def readTree(self, gameNode):
        turn = gameNode.board().turn
        self.curCol = int(not turn)
        # The mainline move goes first.
        if gameNode.variations:
            main_variation = gameNode.variations[0]
            self.createMoveTreeItem(main_variation)
        # Then visit sidelines.
        for v in itertools.islice(gameNode.variations, 1, None):
            self.createMoveTreeItem(v)
            self.readTree(v)
        # The mainline is continued last.
        if gameNode.variations:
            self.readTree(main_variation)

    def updateAfterMove(self, newNode):
        self.createMoveTreeItem(newNode)
        self.moveItemAdded.emit(newNode)

    def reset(self, newCurrent=None):
        self.clear()
        self.hasVariations = False
        self.setItem(0, 0, QStandardItem('...'))
        self.setItem(0, 1, QStandardItem(''))
        if newCurrent:
            print('tree reset')
            self.readTree(newCurrent.root())
            self.moveItemAdded.emit(newCurrent)


class MoveTreeItem(QStandardItem):
    def __init__(self, gameNode):
        super().__init__()
        self.gameNode = gameNode
        self.moveSan = gameNode.parent.board().san(gameNode.move)
        self.setText(self.moveSan)
        self.setEditable(False)
        self.setToolTip(gameNode.comment)

        if not self.gameNode.is_main_line():
            self.setBackground(Qt.yellow)

    def clicked(self, event):
        print('yea')

    def __repr__(self):
        i = self.index()
        return '%d, %d, move %s' % (i.row(), i.column(), self.moveSan)
