from PyQt5.QtCore import (Qt, QRectF, QLineF, QPointF, QSizeF,
                          QPropertyAnimation, QByteArray,
                          QParallelAnimationGroup, pyqtSignal)
from PyQt5.QtGui import (QPixmap, QPainter, QColor, QTransform,
                         QBrush, QPen, QPolygonF)
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsPixmapItem,
                             QGraphicsView, QMenu, QGraphicsItem)
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from widgets.square import SquareWidget, PieceItem, DummySquareItem
import copy
import math
import userConfig
import chess
import constants
# THIS CLASS IS VERY IMPORTANT TO ME, LET'S KEEP IT PRETTY


class BoardSceneView(QGraphicsView):
    def __init__(self, parent, scene):
        super().__init__(parent)
        self.setScene(scene)
        if QGLFormat.hasOpenGL():
            self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))

    def initUI(self, initialSceneWidth):
        self.initialSceneWidth = initialSceneWidth
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(Qt.red))
        self.setMinimumWidth(200)
        self.setMinimumHeight(200)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        newGameAction = menu.addAction("New game")
        newGameAction.triggered.connect(self.parent().openGame.newGame)
        flipAction = menu.addAction("Flip board")
        flipAction.triggered.connect(self.scene().flipBoard)
        menu.popup(self.mapToGlobal(event.pos()))

    def resizeEvent(self, event):
        sceneWidth = min(event.size().width(), event.size().height())
        trans = QTransform()
        trans.scale(sceneWidth / self.initialSceneWidth,
                    sceneWidth / self.initialSceneWidth)
        self.setTransform(trans)
        self.centerOn(sceneWidth / 2.0, sceneWidth / 2.0)


class BoardScene(QGraphicsScene):
    """
    Contains and manages SquareWidgets interacting
    with each other.
    Sends moves and premoves through signals.
    """
    moveInputted = pyqtSignal(chess.Move)

    def __init__(self, parent, board):
        super().__init__(parent)
        self.board = copy.deepcopy(board)
        self.squareWidgets = []
        self.squareWidth = 0
        self.dragPieceBehind = None
        self.dragPieceAhead = None
        self.lastMouseSquare = None
        self.selectedSquare = -1
        # For arrows
        self.longestPV = []
        self.effectItems = []
        self.heroColor = chess.WHITE

    def initSquares(self, squareWidth):
        """
        Initializes squares and pieces with dimensions
        given by squareWidth.
        """
        self.squareWidth = squareWidth
        constants.PIECE_PADDING_RIGHT = constants.PIECE_PADDING_RIGHT * \
            squareWidth
        constants.PIECE_PADDING_BOT = constants.PIECE_PADDING_BOT * squareWidth
        for s in chess.SQUARES:
            newSquareWidget = SquareWidget(s, squareWidth)
            newSquareWidget.pieceReleased.connect(self.sendMove)
            newSquareWidget.invalidDrop.connect(self.deselectSquares)
            if self.board.piece_at(s) is not None:
                piece = self.createPiece(self.board.piece_at(s))
                newSquareWidget.addPiece(piece)
            self.addItem(newSquareWidget)
            self.squareWidgets.append(newSquareWidget)
        self.setSceneRect(0, 0, int(squareWidth * 8), int(squareWidth * 8))

    # Helper methods
    def sendMove(self, toSquare, fromSquare=None):
        """
        Passes the move to the parent. Then updates the board graphics.
        Does not validate move, although it should be valid.
        """
        if fromSquare is None:
            fromSquare = self.selectedSquare
        m = chess.Move(fromSquare, toSquare)
        print("attempting", m)
        self.updateAfterMove(m)
        self.moveInputted.emit(m)

    def updateSelectionGraphics(self, lastSelection, square):
        # Clicking on a new piece selects it.
        if lastSelection != square:
            self.squareWidgets[square].isSelected = True
            self.squareWidgets[square].addEffectItem(SquareWidget.Selected)
        else:
            # Same piece deselects
            self.selectedSquare = -1
            return
        # Add the valid move squares
        for m in self.board.legal_moves:
            if m.from_square == self.selectedSquare:
                self.squareWidgets[m.to_square].addEffectItem(
                    SquareWidget.ValidMove)
                self.squareWidgets[m.to_square].isValidMove = True

    def squareWidgetAt(self, pos):
        for i in self.items(pos):
            if type(i) == DummySquareItem:
                return i.parentItem()
        return None

    def createPiece(self, piece, scale=None):
        newPieceItem = PieceItem(piece)
        newPieceItem.pieceClicked.connect(self.pieceClicked)
        newPieceItem.pieceDragStarting.connect(self.pieceDragStarting)
        newPieceItem.pieceDragHappening.connect(self.pieceDragHappening)
        newPieceItem.pieceDragStopping.connect(self.pieceDragStopping)
        if scale is None:
            scale = (float(self.squareWidth) /
                     newPieceItem.boundingRect().width())
        newPieceItem.setScale(scale)
        return newPieceItem

    def updateSquareEffectsAfterMove(self, move):
        # Note that updating engine items is called
        # automatically by the engine widget, not here.
        for s in self.squareWidgets:
            p = self.board.piece_at(s.square)
            if s.square == move.from_square or s.square == move.to_square:
                s.clearEffectItems()
                s.addEffectItem(SquareWidget.LastMove)
            elif (self.board.is_check() and p is not None and
                    p.piece_type == chess.KING and
                    p.color == self.board.turn):
                s.addEffectItem(SquareWidget.CheckSquare)
            else:
                s.clearEffectItems()
            s.isValidMove = False
        self.selectedSquare = -1

    def updateAfterMove(self, move, oldBoard=None):
        """
        Updates the board graphics one valid move forward.
        This is faster than calling refreshPosition.
        :param move: the move that happened on the board
        :param isEnPassant: whether the move that just occured was an ep
        :return: void
        """
        if oldBoard:
            self.board = oldBoard
        if move.promotion is None:
            fromPieceItem = self.squareWidgets[move.from_square].pieceItem
            self.squareWidgets[move.from_square].removePiece()
        else:
            fromPieceItem = self.createPiece(chess.Piece(move.promotion,
                                             self.board.turn))
            self.squareWidgets[move.from_square].removePiece(True)
        if self.board.is_queenside_castling(move):
            # Fix rook, move.to_square is the rook square
            if self.board.turn == chess.WHITE:
                rookSquare = chess.A1
                move.to_square = chess.C1
            else:
                rookSquare = chess.A8
                move.to_square = chess.C8
            rookWid = self.squareWidgets[rookSquare]
            rookItem = rookWid.pieceItem
            rookWid.removePiece()
            self.squareWidgets[rookSquare + 3].addPiece(rookItem)
        elif self.board.is_kingside_castling(move):
            # Fix rook, move.to_square is the rook square
            if self.board.turn == chess.WHITE:
                rookSquare = chess.H1
                move.to_square = chess.G1
            else:
                rookSquare = chess.H8
                move.to_square = chess.G8
            rookWidg = self.squareWidgets[rookSquare]
            rookItem = rookWidg.pieceItem
            rookWidg.removePiece()
            self.squareWidgets[rookSquare - 2].addPiece(rookItem)
        elif self.board.is_en_passant(move):
            # remember we are updating after the move has occurred
            if self.board.turn == chess.WHITE:
                self.squareWidgets[move.to_square - 8].removePiece()
            else:
                self.squareWidgets[move.to_square + 8].removePiece()

        self.squareWidgets[move.to_square].removePiece()
        self.squareWidgets[move.to_square].addPiece(fromPieceItem)

        self.board.push(move)
        self.updateSquareEffectsAfterMove(move)

    def createEffectItem(self, itemClass, move=None, hero=True, opacity=1.0):
        if itemClass == ArrowGraphicsItem.Type:
            assert move is not None
            fromSquare = self.squareWidgets[move.from_square]
            toSquare = self.squareWidgets[move.to_square]
            item = ArrowGraphicsItem(hero, move, fromSquare, toSquare,
                                     self.squareWidth)
            item.setOpacity(opacity)
            return item
        return None

    def addEffectItem(self, itemClass, move=None, hero=True, zValue=0,
                      opacity=1.0):
        effectItem = self.createEffectItem(itemClass.Type, move, hero, opacity)
        if effectItem is not None:
            effectItem.setZValue(151 + zValue)
            self.effectItems.append(effectItem)
            self.addItem(effectItem)
            # print('adding', effectItem.move, self.effectItems)
        else:
            print('tried to add an invalid effect item', itemClass)

    def removeEffectItem(self, effectItem):
        assert effectItem in self.effectItems
        self.effectItems.remove(effectItem)
        effectItem.setParentItem(None)
        self.removeItem(effectItem)
        # print('removing', effectItem.move, self.effectItems)

    def clearEffectItems(self, item=None):
        # TODO: fix this ugly. for some reason I cant remove elements
        # while iterating.
        itemsCopy = self.effectItems.copy()
        for i in itemsCopy:
            if item is not None and i.type() == item.Type:
                self.removeEffectItem(i)
            elif item is None:
                self.removeEffectItem(i)
        assert not self.effectItems

    # Events + called from elsewhere
    def refreshPosition(self):
        """
        Clears all pieces and creates new pieces according to
        self.board.
        Also clears the selected square and adds check effects if in check.
        :return: Void
        """
        for s in self.squareWidgets:
            s.clearEffectItems()
            s.removePiece()
            p = self.board.piece_at(s.square)
            if p is not None:
                newPieceItem = self.createPiece(p)
                s.addPiece(newPieceItem)
        if self.board.is_check():
            kingSet = self.board.pieces(chess.KING, self.board.turn)
            assert len(kingSet) == 1
            kingSquare = self.squareWidgets[list(kingSet)[0]]
            kingSquare.addEffectItem(SquareWidget.CheckSquare)
        self.selectedSquare = -1

    def updateEngineItems(self, longestPV):
        if not longestPV:
            self.clearEffectItems(ArrowGraphicsItem)
            return
        self.longestPV = longestPV
        length = min(len(longestPV),
                     int(userConfig.config['BOARD']['numArrows']))

        # Arrows
        moveList = longestPV[:length]
        # Remove all non-repeated arrows
        curArrows = [a for a in self.effectItems if a.type() ==
                     ArrowGraphicsItem.Type]
        for a in curArrows.copy():
            if a.move not in moveList:
                self.removeEffectItem(a)
                curArrows.remove(a)
        # Add new arrows, or modify existing ones
        for i, m in enumerate(moveList):
            arrow = [a for a in curArrows if a.move == m]
            if arrow:
                opacity = 1.0 - i / length
                arrow[0].setOpacity(opacity)
            else:
                hero = self.heroColor == (i+self.board.turn) % 2
                opacity = 1.0 - i / length
                self.addEffectItem(ArrowGraphicsItem, m,
                                   hero, length - i, opacity)
        assert len(self.effectItems) <= length

    def flipBoard(self):
        # TODO: fix twitching on hover after flipping
        self.heroColor = not self.heroColor
        curArrows = [a for a in self.effectItems if a.type() ==
                     ArrowGraphicsItem.Type]
        for a in curArrows:
            a.changeHero()
        aniGroup = BoardAnimationGroup(self, curArrows + self.squareWidgets)
        aniDuration = 250
        for sq in self.squareWidgets:
            prop = QByteArray(b'pos')
            ani = QPropertyAnimation(sq, prop, self)
            ani.setDuration(aniDuration)
            ani.setStartValue(sq.pos())
            width = self.squareWidth * 7
            ani.setEndValue(QPointF(width - sq.x(),
                                    width - sq.y()))
            aniGroup.addAnimation(ani)
        aniGroup.start()

    def toggleCoordinates(self):
        # TODO: implement
        pass

    def pieceClicked(self, square):
        # This is a two-click capture move.
        if (self.board.piece_at(square).color != self.board.turn):
            if self.selectedSquare != -1:
                self.sendMove(square)
            return
        lastSelection = self.selectedSquare
        # Clicking on a new or old piece deselects the previous squares
        self.deselectSquares()
        self.selectedSquare = square
        self.updateSelectionGraphics(lastSelection, square)

    def pieceDragStarting(self, square):
        self.dragPieceAhead = self.squareWidgets[square].pieceItem
        self.squareWidgets[square].removePiece()
        self.dragPieceAhead.setZValue(150)
        self.dragPieceAhead.setCursor(Qt.SizeAllCursor)
        pieceImg = QPixmap(self.squareWidth, self.squareWidth)
        pieceImg.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pieceImg)
        self.dragPieceAhead.renderer().render(painter)
        painter.end()
        self.dragPieceBehind = QGraphicsPixmapItem(pieceImg)
        pos = self.squareWidgets[square].pos()
        self.dragPieceBehind.setPos(pos)
        self.dragPieceBehind.setOpacity(0.5)
        self.addItem(self.dragPieceBehind)

    def pieceDragHappening(self, mousePos):
        squareWidget = self.squareWidgetAt(mousePos)
        if squareWidget is not None:
            if self.lastMouseSquare != squareWidget:
                squareWidget.hoverEnterEvent(None)
                if self.lastMouseSquare is not None:
                    self.lastMouseSquare.hoverLeaveEvent(None)
                self.lastMouseSquare = squareWidget

    def pieceDragStopping(self, square, mousePos):
        assert(self.dragPieceBehind is not None)
        self.removeItem(self.dragPieceBehind)
        self.dragPieceBehind = None
        assert(self.dragPieceAhead is not None)
        self.squareWidgets[square].addPiece(self.dragPieceAhead)

        # This is a drag and drop move
        toWidget = self.squareWidgetAt(mousePos)
        if toWidget is not None and toWidget.isValidMove:
            self.dragPieceAhead.setCursor(Qt.ArrowCursor)
            self.dragPieceAhead = None
            self.sendMove(toWidget.square, square)
        else:
            self.dragPieceAhead.setCursor(Qt.PointingHandCursor)
            self.dragPieceAhead = None
            self.deselectSquares()
            return

    def deselectSquares(self):
        for s in self.squareWidgets:
            if s.isValidMove:
                s.isValidMove = False
                s.removeEffectItem(SquareWidget.ValidMove)
        self.squareWidgets[self.selectedSquare].removeEffectItem(
            SquareWidget.Selected)
        self.selectedSquare = -1

    def reset(self, newNode):
        self.board = copy.deepcopy(newNode.board())
        self.dragPieceBehind = None
        self.dragPieceAhead = None
        self.selectedSquare = -1
        self.lastMouseSquare = None
        # For arrows
        self.longestPV = []
        self.clearEffectItems()
        self.refreshPosition()

    def editBoard(self):
        pieces = []
        for t in chess.PIECE_TYPES:
            for c in chess.COLORS:
                pieces.append(chess.Piece(t, c))
        # TODO: implement
        # dimen = self.moveTreeView.geometry()
        # pieceWidth = max(dimen.width() / 8, dimen.height() / 8)
        self.moveTreeView.setVisible(False)


class ArrowGraphicsItem(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, hero, move, fromSquare, toSquare, squareWidth):
        super(ArrowGraphicsItem, self).__init__()
        self.squareWidth = squareWidth
        self.move = move
        self.fromSquare = fromSquare
        self.toSquare = toSquare
        self.sourcePoint = self.fromSquare.pos() + \
            QPointF(self.squareWidth / 2, self.squareWidth / 2)
        self.destPoint = self.toSquare.pos() + \
            QPointF(self.squareWidth / 2, self.squareWidth / 2)
        self.arrowSize = float(userConfig.config['BOARD']['arrowSize'])
        self.hero = hero
        if self.hero:
            col = QColor(userConfig.config['BOARD']['heroArrowColor'])
        else:
            col = QColor(userConfig.config['BOARD']['enemyArrowColor'])
        self.createPallette(col)

    def type(self):
        return self.Type

    def createPallette(self, col):
        self.brush = QBrush(col)
        self.pen = QPen(self.brush,
                        float(userConfig.config['BOARD']['arrowWidth']),
                        Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)

    def changeHero(self):
        if self.hero:
            col = QColor(userConfig.config['BOARD']['enemyArrowColor'])
        else:
            col = QColor(userConfig.config['BOARD']['heroArrowColor'])
        self.createPallette(col)
        self.hero = not self.hero

    def adjust(self):
        self.prepareGeometryChange()
        self.sourcePoint = self.fromSquare.pos() + \
            QPointF(self.squareWidth / 2, self.squareWidth / 2)
        self.destPoint = self.toSquare.pos() + \
            QPointF(self.squareWidth / 2, self.squareWidth / 2)

    def boundingRect(self):
        extra = (self.pen.width() + self.arrowSize) / 2.0
        return QRectF(self.sourcePoint,
                      QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                             self.destPoint.y() - self.sourcePoint.y())) \
            .normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        assert self.fromSquare is not None
        assert self.toSquare is not None
        line = QLineF(self.sourcePoint, self.destPoint)

        assert(line.length() != 0.0)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi*2.0) - angle

        destArrowP1 = self.destPoint + QPointF(
                math.sin(angle - math.pi / 3) * self.arrowSize,
                math.cos(angle - math.pi / 3) * self.arrowSize
        )
        destArrowP2 = self.destPoint + QPointF(
                math.sin(angle - math.pi + math.pi / 3) * self.arrowSize,
                math.cos(angle - math.pi + math.pi / 3) * self.arrowSize
        )

        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        # arrowhead1 = QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2])
        arrowhead2 = QPolygonF([line.p2(), destArrowP1, destArrowP2])
        painter.drawPolygon(arrowhead2)

        painter.setPen(self.pen)
        painter.drawLine(line)


class BoardAnimationGroup(QParallelAnimationGroup):
    def __init__(self, parent, adjustAfterAnimationItems):
        super().__init__(parent)
        self.adjustAfterAnimationItems = adjustAfterAnimationItems

    def updateCurrentTime(self, currentTime):
        super().updateCurrentTime(currentTime)

    def updateState(self, newState, oldState):
        if (newState == QParallelAnimationGroup.Stopped):
            for i in self.adjustAfterAnimationItems:
                i.adjust()
