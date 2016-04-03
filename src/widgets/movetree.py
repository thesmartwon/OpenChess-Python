from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QBrush, QColor
from PyQt5.QtWidgets import (QMenu, QGraphicsView,
                             QGraphicsScene, QGraphicsTextItem,
                             QGraphicsItemGroup)
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
import chess
import json
import constants
import strings
import userConfig


class MoveTreeView(QGraphicsView):
    def __init__(self, parent, scene):
        super().__init__(parent)
        self.setScene(scene)
        if QGLFormat.hasOpenGL():
            self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        self.initUI()

    def initUI(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(Qt.blue))
        met = QFontMetrics(self.font())
        maxFileWidth = max([met.width(c) for c in strings.FILE_NAMES])
        maxRankWidth = max([met.width(c) for c in strings.RANK_NAMES])
        maxPieceWidth = max([met.width(c) for c in strings.PIECE_SYMBOLS])
        maxEndWidth = max([met.width(c) for c in ['+', '#']])
        maxTakeWidth = met.width('x')
        maxColWidth = maxPieceWidth + maxRankWidth * 2 + maxFileWidth * 2 +\
            maxTakeWidth + maxEndWidth
        self.vScrollBarWidth = 17
        self.setMinimumWidth(maxColWidth * 2 + self.vScrollBarWidth)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("scrollarea1")
        menu.addAction("scrollarea2")
        menu.popup(event.globalPos())

    def resizeEvent(self, event):
        # This kinda defeats the purpose of scene/view, but oh well.
        self.scene().resizeEvent(event, self.scene().height() > self.height())


class MoveTreeScene(QGraphicsScene):
    """
    This is the table of moves.
    """
    scrollToMove = pyqtSignal(chess.pgn.GameNode)

    def __init__(self, parent, gameRoot):
        super().__init__(parent)
        self.gameRoot = gameRoot
        try:
            f = open(constants.RESOURCES_PATH + '/openings/eco.json', 'r')
            self.openingsJson = json.load(f)
        except IOError:
            # TODO: use an error stream or something
            self.openingsJson = {}
        self.rowHeight = 25
        self.selectedItem = None
        self.row = 0
        self.col = 0
        header = HeaderWidget('A00', " King's Pawn ")
        header.setPos(0, 0)
        self.addItem(header)
        self.setBackgroundBrush(QBrush(Qt.blue))

    def updateTree(self, gameNode):
        for v in gameNode.variations:
            turn = v.parent.board().turn
            plies = len(v.parent.board().move_stack)
            self.col = int(not turn)
            if v.is_main_line():
                if turn:
                    self.row += 1
                if plies % 2 == 0:
                    header = HeaderWidget(str(int(plies / 2 + 1)))
                    print('making moveHeader', self.row, 0)
                    header.setPos(0, self.row * self.rowHeight)
                    self.addItem(header)
                move = MoveWidget(v)
                print('making moveWidg', self.row, self.col)
                move.setPos(self.movePadding + self.col * self.colWidth,
                            self.row * self.rowHeight)
                self.addItem(move)
                if not v.is_end():
                    self.updateTree(v)
            else:
                print('making variation', self.row, self.col)
                self.row += 1
                variation = VariationWidget(v)
                variation.setPos(0, self.row * self.rowHeight)
                self.addItem(variation)

    def updateAfterMove(self, gameNode):
        self.reset()
        header = HeaderWidget("King's Pawn ", 'A00')
        header.setPos(0, 0)
        self.addItem(header)
        self.updateTree(gameNode.root())
        for i in self.items():
            if type(i) == MoveWidget:
                if i.gameNode == gameNode:
                    self.selectedItem = i
                    i.selected = True

    def reset(self, newGame=None):
        for i in self.items():
            self.removeItem(i)
        self.row = 0
        self.col = 0
        if newGame:
            self.updateAfterMove(newGame.root())

    def resizeEvent(self, event, scrollbarWidth=0):
        dummyRect = HeaderWidget('100').boundingRect()
        self.movePadding = dummyRect.width()
        self.rowHeight = dummyRect.height()
        print('scene is now', event.size().width(), event.size().height(),
              'row height', self.rowHeight)
        extra = self.movePadding + scrollbarWidth
        self.colWidth = (event.size().width() - extra) / 2
        self.setSceneRect(0, 0, event.size().width(),
                          max(event.size().height(),
                              self.sceneRect().height()))


class HeaderWidget(QGraphicsTextItem):
    """
    The move number or opening title.
    """
    def __init__(self, text='', boldText=''):
        super().__init__()
        font = self.font()
        conf = userConfig.config['MOVETREE']
        font.setPointSize(int(conf['movefontpoint']))
        self.setFont(font)
        self.setDefaultTextColor(Qt.darkGreen)
        if text and not boldText:
            met = QFontMetrics(self.font())
            digits = [chr(i) for i in range(48, 58)]
            # TODO: this is a little buggy it seems
            maxwidth = max(met.width(d) for d in digits) * 4
            self.setTextWidth(maxwidth)
            self.setPlainText(text)
        else:
            self.makeText(text, boldText)

    def makeText(self, text, boldText):
        myText = """<span style='font-size:14pt; font-weight:600; color:
                 #aa0000;'>%s</span><span style='font-size:11pt;
                 font-weight:600; color:#00aa00;'>%s</span>""" \
                 % (boldText, text)
        self.setHtml(myText)

    def setFromFen(self, jsonDict, fen):
        opening = [jsonDict[k] for k, v in jsonDict.items() if v['fen'] == fen]
        if opening:
            self.makeText(opening[0]['eco'], opening[0]['name'])

    def paint(self, painter, option, widget):
        col = QColor(userConfig.config['MOVETREE']['moveheadercolor'])
        painter.setBrush(QBrush(col))
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)


class MoveWidget(QGraphicsTextItem):
    """
    The text associated with a move
    from a game state. The gameNode must have
    a parent (ie don't send the root node).
    """
    def __init__(self, gameNode, isVariation=False):
        super().__init__()
        font = self.font()
        font.setPointSize(int(userConfig.config['MOVETREE']['movefontpoint']))
        self.setFont(font)
        self.gameNode = gameNode
        moveText = self.gameNode.parent.board().san(self.gameNode.move)
        self.setPlainText(moveText)
        self.selected = False
        self.setAcceptHoverEvents(True)

    def paint(self, painter, option, widget):
        if not self.selected:
            col = QColor(userConfig.config['MOVETREE']['movetilecolor'])
        else:
            col = QColor(Qt.yellow)
        painter.setBrush(QBrush(col))
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

    def mousePressEvent(self, event):
        print('step 1')
        if (event.button() == Qt.LeftButton):
            print('item', self.toPlainText(), 'clicked')
            self.scene().scrollToMove.emit(self.gameNode)

    def displayContextMenu(self, point):
        menu = QMenu(self)
        menu.addAction("Dummy1")
        menu.addAction("Dummy2")
        menu.popup(self.mapToGlobal(point))

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)


class VariationWidget(QGraphicsItemGroup):
    def __init__(self, parent, gameNode):
        super().__init__(parent)
        self.gameNode = gameNode
        self.mainNodeCount = 0
        self.addMoveText(gameNode)
        # Display first few moves following this variation

    def addMoveText(self, gameNode):
        if self.mainNodeCount > 4:
            return
        for v in gameNode.variations:
            if not v.is_main_line() and v.is_main_variation():
                MoveWidget(self, v, True)
                self.mainNodeCount += 1

    def clicked(self):
        # Expands the variation to show other variations and
        # the entirity of this variation
        self.setMinimumHeight(200)
