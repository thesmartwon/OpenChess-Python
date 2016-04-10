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

    def entryAdded(self, row, col):
        self.setCurrentIndex(self.model().index(row, col))

    def entryScrolled(self, moveNode):
        """
        Happens when game asks us to scroll without changing current tree
        """
        curItem = self.model().itemFromIndex(self.currentIndex())
        if type(curItem) == MoveTreeItem and curItem.gameNode != moveNode:
            # This is ridiculous. Has to be a better way to search
            for r in range(self.model().rowCount()):
                for c in range(self.model().columnCount()):
                    item = self.model().itemFromIndex(self.model().index(r, c))
                    if (type(item) == MoveTreeItem and
                            item.gameNode == moveNode):
                        self.setCurrentIndex(self.model().index(r, c))
                        print('found')
                        return

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
            self.scrollInDirection(-1, lambda i:
                                   i.gameNode.is_main_variation())
        elif keyCode in self.nextShortcuts:
            event.accept()
            self.scrollInDirection(1, lambda i: i.gameNode.is_main_variation())
        elif keyCode in self.prevVarShortcuts:
            if self.model().hasVariations:
                event.accept()
                self.scrollInDirection(-1, lambda i:
                                       not i.gameNode.is_main_variation())
        elif keyCode in self.nextVarShortcuts:
            if self.model().hasVariations:
                event.accept()
                self.scrollInDirection(1, lambda i:
                                       not i.gameNode.is_main_variation())

    def scrollInDirection(self, direction, stopCondition):
        numItems = self.model().rowCount() * self.model().columnCount()
        curNum = self.currentIndex().row() * 2 + self.currentIndex().column()
        while True:
            curNum += direction
            if curNum == numItems:
                curNum = numItems - 1
                # This makes it so that if the last item is not a MoveTreeItem,
                # we will go backwards until we find one
                direction *= -1
            elif curNum < 0:
                curNum = 0
                direction *= -1
            curIndex = self.model().index(curNum / 2, curNum % 2)
            curItem = self.model().itemFromIndex(curIndex)
            if type(curItem) == MoveTreeItem and stopCondition(curItem):
                break
        if self.currentIndex() != curIndex and curIndex.isValid():
            self.setCurrentIndex(curIndex)


class MoveTreeModel(QStandardItemModel):
    moveItemAdded = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        # self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
        #                                 strings.COLOR_SECOND])
        self.reset()

    def createMoveTreeItem(self, gameNode, notify=False):
        newItem = MoveTreeItem(gameNode)
        if gameNode.is_main_variation():
            self.setItem(self.curRow, self.curCol, newItem)
        else:
            if gameNode.board().turn:
                list = [newItem, QStandardItem('')]
            else:
                list = [QStandardItem(''), newItem]
            self.insertRow(self.curRow, list)
            print('made variation', gameNode.move)
            self.hasVariations = True
        header = str(gameNode.parent.board().fullmove_number)
        self.setHeaderData(self.curRow, Qt.Vertical, header)

        if notify:
            self.moveItemAdded.emit(self.curRow, self.curCol)

    def readTree(self, gameNode):
        turn = gameNode.board().turn
        self.curCol = int(not turn)
        # The mainline move goes first.
        if gameNode.variations:
            main_variation = gameNode.variations[0]
            self.createMoveTreeItem(main_variation)
            if not turn:
                self.curRow += 1
        # Then visit sidelines.
        for v in itertools.islice(gameNode.variations, 1, None):
            if not v.is_main_variation():
                self.createMoveTreeItem(v)
                self.curRow += 1
        # The mainline is continued last.
        if gameNode.variations:
            self.readTree(main_variation)

    def updateAfterMove(self, newNode):
        self.createMoveTreeItem(newNode, True)
        if self.curCol == 0:
            self.curCol = 1
        else:
            self.curRow += 1
            self.curCol = 0

    def reset(self, rootNode=None):
        self.clear()
        self.hasVariations = False
        self.setItem(0, 0, QStandardItem('...'))
        self.setItem(0, 1, QStandardItem(''))
        self.curRow = 0
        self.curCol = 0
        if rootNode:
            print('tree reset')
            self.readTree(rootNode.root())
            self.moveItemAdded.emit(0, 0)


class MoveTreeItem(QStandardItem):
    def __init__(self, gameNode):
        super().__init__()
        self.gameNode = gameNode
        self.moveSan = gameNode.parent.board().san(gameNode.move)
        self.setText(self.moveSan)
        self.setEditable(False)
        self.setToolTip(gameNode.comment)

        if not self.gameNode.is_main_variation():
            self.setBackground(Qt.yellow)

    def clicked(self, event):
        print('yea')

    def __repr__(self):
        i = self.index()
        return '%d, %d, move %s' % (i.row(), i.column(), self.moveSan)
