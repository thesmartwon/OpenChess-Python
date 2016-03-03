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
    Arrow, Blank = range(QGraphicsItem.UserType + 1,
                         QGraphicsItem.UserType + 3)

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
        self.graphicEffectItems = []

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
            # TODO: figure out why this rect is always at 0,0 and fix in
            # self.squareWidgetAt
            p = self.game.piece_at(i)
            newSquareWidget.pieceReleased.connect(self.pieceDropped)
            newSquareWidget.invalidDrop.connect(self.deselectSquaresEvent)
            if p is not None:
                piece = PieceItem(p)
                lesserDimension = min(squareWidth, squareWidth)
                scale = float(lesserDimension) / piece.boundingRect().width()
                piece.setScale(scale)
                piece.pieceClicked.connect(self.pieceClickedEvent)
                piece.pieceDragStarting.connect(self.pieceDragStartingEvent)
                piece.pieceDragHappening.connect(self.pieceDragHappeningEvent)
                piece.pieceDragStopping.connect(self.pieceDragStoppingEvent)
                newSquareWidget.addPiece(piece)
            self.addItem(newSquareWidget)
            self.squareWidgets.append(newSquareWidget)

    # Helper methods
    def pieceDropped(self, toSquare, fromSquare=None):
        """
        Passes the move to the parent. Then updates the board graphics.
        Does not validate move, although it should be valid.
        :param fromSquare: Square move is from
        :param toSquare: Square move is to
        :return: None
        """
        if fromSquare is None:
            fromSquare = self.selectedSquare
        m = chess.Move(fromSquare, toSquare)
        self.parent().doMove(m)

    def deselectSquaresEvent(self):
        for s in self.squareWidgets:
            if s.isValidMove:
                s.isValidMove = False
                s.removeEffectItem(SquareWidget.ValidMove)
        self.squareWidgets[self.selectedSquare].removeEffectItem(
            SquareWidget.Selected)
        self.selectedSquare = -1

    def pieceClickedGraphicsEvent(self, lastSelection, square):
        # Clicking on a new piece selects it.
        if lastSelection != square:
            self.squareWidgets[square].isSelected = True
            self.squareWidgets[square].addEffectItem(SquareWidget.Selected)
        else:
            self.selectedSquare = -1
            return
        # Add the valid move squares
        for m in self.game.legal_moves:
            if m.from_square == self.selectedSquare:
                self.squareWidgets[m.to_square].addEffectItem(
                    SquareWidget.ValidMove)
                self.squareWidgets[m.to_square].isValidMove = True

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
            newPieceItem = PieceItem(chess.Piece(move.promotion,
                                     not self.game.turn))
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            newPieceItem.pieceDragStarting.connect(self.pieceDragStartingEvent)
            newPieceItem.pieceDragHappening.connect(self.pieceDragHappeningEvent)
            newPieceItem.pieceDragStopping.connect(self.pieceDragStoppingEvent)
            newPieceItem.setScale(float(self.squareWidth) /
                                  newPieceItem.boundingRect().width())
            self.squareWidgets[move.from_square].removePiece(True)

        self.squareWidgets[move.to_square].removePiece()
        self.squareWidgets[move.to_square].addPiece(newPieceItem)
        # TODO: support king takes rook castling
        # I'm going to stay consistent with python.chess's
        # implementation of castling.
        # Oddly enough, it 'e1g1' or 'e1c1'.

        if castling == 1:
            newPieceItem = PieceItem(self.squareWidgets[move.to_square - 2].
                                     pieceItem.piece)
            newPieceItem.setScale(float(self.squareWidth) /
                                  newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            newPieceItem.pieceDragStarting.connect(self.pieceDragStartingEvent)
            newPieceItem.pieceDragHappening.connect(self.pieceDragHappeningEvent)
            newPieceItem.pieceDragStopping.connect(self.pieceDragStoppingEvent)
            self.squareWidgets[move.to_square - 2].removePiece()
            self.squareWidgets[move.to_square + 1].addPiece(newPieceItem)
        elif castling == 2:
            newPieceItem = PieceItem(self.squareWidgets[move.to_square + 1].
                                     pieceItem.piece)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.
                                  boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            newPieceItem.pieceDragStarting.connect(self.pieceDragStartingEvent)
            newPieceItem.pieceDragHappening.connect(self.pieceDragHappeningEvent)
            newPieceItem.pieceDragStopping.connect(self.pieceDragStoppingEvent)
            self.squareWidgets[move.to_square + 1].removePiece()
            self.squareWidgets[move.to_square - 1].addPiece(newPieceItem)
        elif isEnPassant:
            # remember we are updating after the move has occurred
            if self.game.turn == chess.BLACK:
                self.squareWidgets[move.to_square - 8].removePiece()
            else:
                self.squareWidgets[move.to_square + 8].removePiece()

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

    def squareWidgetAt(self, pos):
        for i in self.items(pos):
            if type(i) == DummySquareItem:
                return i.parentItem()
        return None

    def countItem(self, itemType):
        count = 0
        for e in self.graphicEffectItems:
            if e.data(0) == itemType:
                count += 1
        return count

    def existsItem(self, itemType, move=None):
        if itemType == self.Arrow:
            assert move is not None
            for i in self.graphicEffectItems:
                if i.data(0) == itemType:
                    if i.move == move:
                        return True
        return False

    def createEffectItem(self, itemType, move=None, hero=True, opacity=1.0):
        if itemType == BoardScene.Arrow:
            assert move is not None
            fromSquare = self.squareWidgets[move.from_square]
            toSquare = self.squareWidgets[move.to_square]
            item = ArrowGraphicsItem(hero, move, fromSquare, toSquare,
                                     self.squareWidth)
            item.setOpacity(opacity)
            return item
        return None

    def addEffectItem(self, itemType, move=None, hero=True, opacity=1.0):
        effectItem = self.createEffectItem(itemType, move, hero, opacity)
        if effectItem is not None:
            effectItem.setData(0, QVariant(itemType))
            effectItem.setZValue(149)
            print('adding', effectItem)
            self.addItem(effectItem)
            self.graphicEffectItems.append(effectItem)
        else:
            print('tried to add an invalid effect item', itemType)

    def clearEffectItems(self, itemType=None):
        for i in self.items():
            if (itemType is not None and i.data(0) is not None and
                    i.data(0) == itemType):
                self.removeEffectItem(i)
            elif itemType is None:
                self.removeEffectItem(i)

    def effectItems(self, itemType):
        for i in self.items():
            if i.data(0) is not None and i.data(0) == itemType:
                yield i

    def removeEffectItem(self, effectItem):
        assert effectItem is not None
        effectItem.setParentItem(None)
        print('removing1', effectItem)
        self.graphicEffectItems.remove(effectItem)
        print('removing2')
        self.removeItem(effectItem)
        print('removing3')

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
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                s.addPiece(newPieceItem)
                if self.game.is_check() and p is not None \
                   and p.piece_type == chess.KING \
                   and p.color == self.game.turn:
                    s.addEffectItem(SquareWidget.CheckSquare)
        self.selectedSquare = -1

    def updateEngineItems(self, longestPV):
        if len(longestPV) < int(userConfig.config['BOARD']['numArrows']):
            length = len(longestPV)
        else:
            length = int(userConfig.config['BOARD']['numArrows'])

        # Arrows
        moveList = longestPV[:length]
        for i in self.effectItems(self.Arrow):
            if i.move in moveList:
                opacity = 1.0 - moveList.index(i.move) / length
                if opacity == 0:
                    opacity = 0.1
                i.setOpacity(opacity)
            else:
                self.removeEffectItem(i)

        for i in range(len(moveList)):
            if not self.existsItem(self.Arrow, move=moveList[i]):
                hero = not bool(i % 2 + self.game.turn - 1)
                opacity = 1.0 - float(i) / length
                if opacity == 0:
                    opacity = 0.1
                self.addEffectItem(BoardScene.Arrow, moveList[i],
                                   hero, opacity)

    def flipBoard(self):
        aniGroup = BoardAnimationGroup(self, self.graphicEffectItems)
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
    def pieceClickedEvent(self, square):
        # This is a two-click capture move.
        if (self.game.piece_at(square).color !=
                self.game.turn):
            if self.selectedSquare != -1:
                self.pieceDropped(square)
            return
        lastSelection = self.selectedSquare
        # Clicking on a new or old piece deselects the previous squares
        self.deselectSquaresEvent()
        self.selectedSquare = square
        self.pieceClickedGraphicsEvent(lastSelection, square)

    def pieceDragStartingEvent(self, square):
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

    def pieceDragHappeningEvent(self, mousePos):
        squareWidget = self.squareWidgetAt(mousePos)
        if squareWidget is not None:
            if self.lastMouseSquare != squareWidget:
                squareWidget.hoverEnterEvent(None)
                if self.lastMouseSquare is not None:
                    self.lastMouseSquare.hoverLeaveEvent(None)
                self.lastMouseSquare = squareWidget

    def pieceDragStoppingEvent(self, square, mousePos):
        assert(self.dragPieceBehind is not None)
        self.removeItem(self.dragPieceBehind)
        self.dragPieceBehind = None
        assert(self.dragPieceAhead is not None)
        self.squareWidgets[square].addPiece(self.dragPieceAhead)

        toWidget = self.squareWidgetAt(mousePos)
        if toWidget is not None and toWidget.isValidMove:
            print("attempt", chess.Move(square, toWidget.square))
            self.dragPieceAhead.setCursor(Qt.ArrowCursor)
            self.dragPieceAhead = None
            self.pieceDropped(toWidget.square, square)
        else:
            self.dragPieceAhead.setCursor(Qt.PointingHandCursor)
            self.dragPieceAhead = None
            self.deselectSquaresEvent()
            return


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

    def updateCurrentTime(self, time):
        super().updateCurrentTime(time)
        for i in self.adjustItems:
            i.adjust()


# class EffectsWidget(QGraphicsWidget):
#     def __init__(self, squareWidth):
#         super().__init__()
#         self.squareWidth = squareWidth
#         self.setGeometry(0, 0, squareWidth * 8, squareWidth * 8)
