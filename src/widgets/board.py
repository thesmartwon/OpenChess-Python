from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView
from PyQt5.QtGui import QPixmap, QPainter, QColor, QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from widgets.square import SquareWidget, PieceItem
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

    def initSquares(self, squareWidth):
        """
        Initializes squares and pieces with dimensions
        given by squareWidth.
        """
        self.squareWidth = squareWidth
        for i in range(64):
            file = 7 - int(i / 8)
            rank = i % 8
            p = self.game.piece_at(i)
            newSquareWidget = SquareWidget(i, squareWidth)
            newSquareWidget.setPos(squareWidth * rank,
                                   squareWidth * file)
            newSquareWidget.pieceReleased.connect(self.pieceDropped)
            newSquareWidget.invalidDrop.connect(self.deselectSquaresEvent)
            if p is not None:
                newPieceItem = PieceItem(p)
                lesserDimension = min(squareWidth, squareWidth)
                scale = float(lesserDimension) / \
                    newPieceItem.boundingRect().width()
                newPieceItem.setScale(scale)
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                newPieceItem.pieceDragStarting.connect(
                    self.pieceDragStartingEvent)
                newPieceItem.pieceDragHappening.connect(
                    self.pieceDragHappeningEvent)
                newPieceItem.pieceDragStopping.connect(
                    self.pieceDragStoppingEvent)
                newSquareWidget.addPiece(newPieceItem)
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
            self.squareWidgets[move.to_square - 2].removePiece()
            self.squareWidgets[move.to_square + 1].addPiece(newPieceItem)
        elif castling == 2:
            newPieceItem = PieceItem(self.squareWidgets[move.to_square + 1].
                                     pieceItem.piece)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.
                                  boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
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

    def squareWidgetAt(self, pos):
        file = 7 - int(pos.y() / self.squareWidth)
        rank = int(pos.x() / self.squareWidth)
        if file in range(8) and rank in range(8):
            return self.squareWidgets[file * 8 + rank]
        else:
            return None

    # Events
    def pieceClickedEvent(self, square):
        # This is a two-click capture move.
        print('hi')
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
            self.pieceDropped(toWidget.square, square )
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
