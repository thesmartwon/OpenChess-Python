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
        self.maxHeaderWidth = met.width('00000.')
        self.vScrollBarWidth = 17
        self.setMinimumWidth(maxItemWidth * 2 + self.maxHeaderWidth +
                             self.vScrollBarWidth)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.resizeCols(self.width())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.displayContextMenu)
        self.setSelectionMode(QTableView.SingleSelection)

    def addColumnSpans(self):
        for r in range(self.model().rowCount()):
            # Look at the first item where the variations are
            item = self.model().itemFromIndex(self.model().index(r, 0))
            if type(item) != BlankTreeItem:
                self.setSpan(r, 0, 1, 3)

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
            if newCur.row() == self.model().rowCount() - 1:
                self.scrollToBottom()
            else:
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
            if self.model().firstVariations:
                event.accept()
                self.scrolledInDirection.emit(-1, False, True)
        elif keyCode in self.nextVarShortcuts:
            if self.model().firstVariations:
                event.accept()
                self.scrolledInDirection.emit(1, False, True)

    def resizeCols(self, width):
        self.setColumnWidth(0, self.maxHeaderWidth)
        remaining = width - self.maxHeaderWidth - 2
        # if self.verticalScrollBar().isVisible():
        #     remaining -= self.vScrollBarWidth
        self.setColumnWidth(1, int(remaining / 2))
        self.setColumnWidth(2, int(remaining / 2))

    def onPositionChange(self, moveNode):
        self.resizeCols(self.width())
        self.addColumnSpans()

    def resizeEvent(self, event):
        self.resizeCols(event.size().width())


class MoveTreeModel(QStandardItemModel):
    moveItemAdded = pyqtSignal(pgn.GameNode)

    def __init__(self, parent):
        super().__init__(parent)
        # self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
        #                                 strings.COLOR_SECOND])
        self.setItemPrototype(BlankTreeItem())
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
            if curCol == 2:
                curRow += 1
                curCol = 1
            else:
                curCol += 1
        else:
            curRow = 0
            curCol = 1
        newItem = MoveTreeItem(gameNode)
        if gameNode.is_main_line():
            self.setItem(curRow, curCol, newItem)
            header = '{}.'.format(str(gameNode.parent.board().fullmove_number))
            self.setItem(curRow, 0, BlankTreeItem(header))
        else:
            curRow += 1
            self.insertRow(curRow, newItem)
            self.firstVariations.append(newItem)

    def readTree(self, gameNode):
        turn = gameNode.board().turn
        self.curCol = int(not turn)
        # The mainline move goes first.
        if gameNode.variations:
            main_variation = gameNode.variations[0]
            self.createMoveTreeItem(main_variation)
            self.readTree(main_variation)
        # Visit sidelines after all main lines.
        for v in itertools.islice(gameNode.variations, 1, None):
            if not v.is_main_variation():
                self.createMoveTreeItem(v)
            else:
                print('figuring it out')

    def updateAfterMove(self, newNode):
        if newNode.is_main_line():
            self.createMoveTreeItem(newNode)
        else:
            for i in self.firstVariations:
                if newNode.parent in i:
                    i.updateSan(newNode)
        self.moveItemAdded.emit(newNode)

    def reset(self, newCurrent=None):
        self.clear()
        self.firstVariations = []
        self.setItem(0, 0, BlankTreeItem('1.'))
        self.setItem(0, 1, BlankTreeItem('...'))
        self.setItem(0, 2, BlankTreeItem(''))
        if newCurrent:
            print('tree reset')
            self.readTree(newCurrent.root())
            self.moveItemAdded.emit(newCurrent)


class MoveTreeItem(QStandardItem):
    def __init__(self, gameNode):
        super().__init__()
        self.gameNode = gameNode
        self.childNodes = set()
        self.setEditable(False)
        self.setToolTip(gameNode.comment)

        if not self.gameNode.is_main_line():
            self.moveSan = str(gameNode)
            self.addChildren(gameNode)
            self.setBackground(Qt.yellow)
        else:
            self.moveSan = gameNode.parent.board().san(gameNode.move)
        self.setText(self.moveSan)

    def __repr__(self):
        i = self.index()
        return '%d, %d, move %s' % (i.row(), i.column(), self.moveSan)

    def __contains__(self, key):
        return key in self.childNodes

    def addChildren(self, node):
        for v in node.variations:
            self.childNodes.add(v)
            self.addChildren(v)

    def updateSan(self, newNode=None):
        self.childNodes.add(newNode)
        self.moveSan = str(self.gameNode)
        self.setText(self.moveSan)


class BlankTreeItem(QStandardItem):
    def __init__(self, text=None):
        super().__init__(text)
        self.setEditable(False)
