from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsPixmapItem,
                             QGraphicsView, QMenu, QGraphicsWidget,
                             QGraphicsItem)
from PyQt5.QtGui import (QPixmap, QPainter, QColor, QCursor, QTransform,
                         QBrush, QPen, QPolygonF)
from PyQt5.QtCore import (Qt, QRectF, QLineF, QPointF, QSizeF,
                          QPropertyAnimation, QByteArray, QVariant,
                          QParallelAnimationGroup)
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from widgets.square import SquareWidget, PieceItem, DummySquareItem
import math
import userConfig
import chess
import constants
# THIS CLASS IS VERY IMPORTANT TO ME, LET'S KEEP IT PRETTY


class BoardScene(QGraphicsScene):
    """
    Contains and manages SquareWidgets interacting
    with each other.
    Sends moves up to the gameCopy given, which must
    be a chess.Board
    """
    # Can go up to +20

    def __init__(self, parent):
        super().__init__(parent)
        self.game = constants.GAME_STATE
        self.squareWidgets = []
        self.squareWidth = 0
        curs = QPixmap(constants.RESOURCES_PATH + '/cursor.png')
        self.pieceDraggingCursor = QCursor(curs, curs.width() / 2,
                                           curs.height() / 2)
        self.dragPieceBehind = None
        self.dragPieceAhead = None
        self.selectedSquare = -1
        self.lastMouseSquare = None
        # For arrows
        self.longestPV = []

    def initSquares(self, squareWidth):
        """
        Initializes squares and pieces with dimensions
        given by squareWidth.
        """
        self.squareWidth = squareWidth
        constants.PIECE_PADDING_RIGHT = constants.PIECE_PADDING_RIGHT * \
            squareWidth
        constants.PIECE_PADDING_BOT = constants.PIECE_PADDING_BOT * squareWidth
        for i in range(64):
            newSquareWidget = SquareWidget(i, squareWidth)
            newSquareWidget.pieceReleased.connect(self.makeMoveTo)
            newSquareWidget.invalidDrop.connect(self.deselectSquares)
            if self.game.piece_at(i) is not None:
                piece = self.createPiece(self.game.piece_at(i))
                newSquareWidget.addPiece(piece)
            self.addItem(newSquareWidget)
            self.squareWidgets.append(newSquareWidget)

    # Helper methods
    def makeMoveTo(self, toSquare, fromSquare=None):
        """
        Passes the move to the parent. Then updates the board graphics.
        Does not validate move, although it should be valid.
        """
        if fromSquare is None:
            fromSquare = self.selectedSquare
        m = chess.Move(fromSquare, toSquare)
        self.parent().doMove(m)

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
        for m in self.game.legal_moves:
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

    def updateGraphicsAfterMove(self, move):
        for s in self.squareWidgets:
            p = self.game.piece_at(s.square)
            if s.square == move.from_square or s.square == move.to_square:
                s.clearEffectItems()
                s.addEffectItem(SquareWidget.LastMove)
            elif (self.game.is_check() and p is not None and
                    p.piece_type == chess.KING and
                    p.color == self.game.turn):
                s.addEffectItem(SquareWidget.CheckSquare)
            else:
                s.clearEffectItems()
            s.isValidMove = False
        self.selectedSquare = -1
        # Remove the first move and its arrow if it follows the engine line
        if len(self.longestPV) > 0 and self.longestPV[0] == move:
            item = self.findEffectItem(ArrowGraphicsItem, move)
            if item is not None:
                self.removeEffectItem(item)
                self.longestPV = self.longestPV[1:]
        else:
            # Otherwise remove them all, and throw away the current variation
            self.longestPV = []
        self.updateEngineItems(self.longestPV)

    def updatePositionAfterMove(self, move, castling, isEnPassant):
        """
        Updates the board graphics one valid move forward.
        This is faster than calling refreshPosition.
        :param move: the move that happened on the board
        :param isEnPassant: whether the move that just occured was an ep
        :return: void
        """
        if move.promotion is None:
            newPieceItem = self.squareWidgets[move.from_square].pieceItem
            self.squareWidgets[move.from_square].removePiece()
        else:
            newPieceItem = self.createPiece(chess.Piece(move.promotion,
                                            not self.game.turn))
            self.squareWidgets[move.from_square].removePiece(True)

        self.squareWidgets[move.to_square].removePiece()
        self.squareWidgets[move.to_square].addPiece(newPieceItem)
        # TODO: support king takes rook castling
        # I'm going to stay consistent with python.chess's
        # implementation of castling.
        # Oddly enough, it 'e1g1' or 'e1c1'.

        if castling == 1:
            fromWid = self.squareWidgets[move.to_square - 2]
            newPieceItem = fromWid.pieceItem
            fromWid.removePiece()
            self.squareWidgets[move.to_square + 1].addPiece(newPieceItem)
        elif castling == 2:
            fromWidg = self.squareWidgets[move.to_square + 1]
            newPieceItem = fromWidg.pieceItem
            fromWidg.removePiece()
            self.squareWidgets[move.to_square - 1].addPiece(newPieceItem)
        elif isEnPassant:
            # remember we are updating after the move has occurred
            if self.game.turn == chess.BLACK:
                self.squareWidgets[move.to_square - 8].removePiece()
            else:
                self.squareWidgets[move.to_square + 8].removePiece()

        self.updateGraphicsAfterMove(move)

    def findEffectItem(self, itemClass, move=None):
        assert hasattr(itemClass, 'Type')
        for i in self.effectItems(itemClass):
            if i.type() == itemClass.Type:
                if move is not None:
                    if i.move == move:
                        return i
                else:
                    return i
        return None

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
            effectItem.setZValue(149 + zValue)
            self.addItem(effectItem)
        else:
            print('tried to add an invalid effect item', itemClass)

    def clearEffectItems(self, itemClass=None):
        for i in self.items():
            if itemClass is not None and i.type() == itemClass.Type:
                self.removeEffectItem(i)
            elif itemClass is None:
                self.removeEffectItem(i)

    def effectItems(self, itemClass):
        for i in self.items():
            if i.type() == itemClass.Type:
                yield i

    def removeEffectItem(self, effectItem):
        assert effectItem is not None
        effectItem.setParentItem(None)
        self.removeItem(effectItem)

    # Called from elsewhere
    def refreshPosition(self):
        """
        Clears all pieces and creates new pieces according to
        self.game.
        Also clears the selected square and adds check effects if in check.
        :return: Void
        """
        for s in self.squareWidgets:
            s.removePiece()
            p = self.game.piece_at(s.square)
            if p is not None:
                newPieceItem = PieceItem(p, s.square)
                newPieceItem.setScale(float(self.squareWidth) /
                                      newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClicked)
                s.addPiece(newPieceItem)
                if self.game.is_check() and p is not None \
                   and p.piece_type == chess.KING \
                   and p.color == self.game.turn:
                    s.addEffectItem(SquareWidget.CheckSquare)
        self.selectedSquare = -1

    def updateEngineItems(self, longestPV):
        if len(longestPV) < 1:
            self.clearEffectItems(ArrowGraphicsItem)
            return
        self.longestPV = longestPV
        length = min(len(longestPV),
                     int(userConfig.config['BOARD']['numArrows']))

        # Arrows
        moveList = longestPV[:length]
        # Remove all non-repeated arrow
        for i in self.effectItems(ArrowGraphicsItem):
            if i.move not in moveList:
                self.removeEffectItem(i)
        # Add new arrows, or modify existing ones
        for i in range(len(moveList)):
            arrow = self.findEffectItem(ArrowGraphicsItem, move=moveList[i])
            if arrow is not None:
                opacity = 1.0 - i / length
                arrow.setOpacity(opacity)
            else:
                hero = not bool(i % 2 + self.game.turn - 1)
                opacity = 1.0 * float(i) / length
                self.addEffectItem(ArrowGraphicsItem, moveList[i],
                                   hero, length - i, opacity)

    def flipBoard(self):
        aniGroup = BoardAnimationGroup(self,
                                       self.effectItems(ArrowGraphicsItem))
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
        pass

    # Events
    def pieceClicked(self, square):
        # This is a two-click capture move.
        if (self.game.piece_at(square).color != self.game.turn):
            if self.selectedSquare != -1:
                self.makeMoveTo(square)
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
        self.dragPieceAhead.setCursor(self.pieceDraggingCursor)
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
            print("attempt", chess.Move(square, toWidget.square))
            self.dragPieceAhead.setCursor(Qt.ArrowCursor)
            self.dragPieceAhead = None
            self.makeMoveTo(toWidget.square, square)
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


class BoardSceneView(QGraphicsView):
    def __init__(self, parent, scene):
        super().__init__(parent)
        self.setScene(scene)
        self.setParent(parent)
        if QGLFormat.hasOpenGL():
            self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.initialSceneWidth = 0

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quitAction = menu.addAction("Flip board")
        quitAction.triggered.connect(self.scene().flipBoard)
        action = menu.popup(self.mapToGlobal(event.pos()))

    def resizeEvent(self, event):
        sceneWidth = min(event.size().width(), event.size().height())
        trans = QTransform()
        trans.scale(sceneWidth / self.initialSceneWidth,
                    sceneWidth / self.initialSceneWidth)
        self.setTransform(trans)


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
        if hero:
            col = QColor(userConfig.config['BOARD']['heroArrowColor'])
        else:
            col = QColor(userConfig.config['BOARD']['enemyArrowColor'])
        self.brush = QBrush(col)
        self.pen = QPen(self.brush,
                        float(userConfig.config['BOARD']['arrowWidth']),
                        Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)

    def type(self):
        return self.Type

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
    def __init__(self, parent, adjustItems):
        super().__init__(parent)
        self.adjustItems = adjustItems

    def updateCurrentTime(self, currentTime):
        super().updateCurrentTime(currentTime)

    def updateState(self, newState, oldState):
        if (newState == QParallelAnimationGroup.Stopped):
            for i in self.adjustItems:
                i.adjust()
