from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QColor, QCursor
from PyQt5.QtCore import QPointF
from widgets.square import SquareWidget, PieceItem, DummySquareItem
import chess
import userConfig
import constants
# TODO: remove all .config['BOARD']['squareWidth'] so
# as to allow different widths
# THIS CLASS IS VERY IMPORTANT TO ME, LET'S KEEP IT PRETTY


class BoardScene(QGraphicsScene):
    """
    Contains and manages SquareWidgets interacting with each other.
    Sends moves up to the parent, which must have a self.game = chess.Board().
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.squareWidgets = []
        self.squareWidth = int(userConfig.config['BOARD']['squareWidth'])
        self.selectedSquare = -1
        curs = QPixmap(constants.RESOURCES_PATH + '\\cursor.png')
        self.pieceDraggingCursor = QCursor(curs, curs.width() / 2,
                                           curs.height() / 2)
        self.dragPieceBehind = None
        self.dragPieceCursor = None
        # initialize squares and pieces
        for i in range(64):
            file = 7 - int(i / 8)
            rank = i % 8
            p = self.parent().game.piece_at(i)
            newSquareWidget = SquareWidget(i, self.squareWidth,
                                           self.squareWidth)
            newSquareWidget.setPos(self.squareWidth * rank,
                                   self.squareWidth * file)
            newSquareWidget.pieceReleased.connect(self.pieceDroppedEvent)
            newSquareWidget.invalidDrop.connect(self.deselectSquaresEvent)
            if p is not None:
                newPieceItem = PieceItem(p)
                newPieceItem.setScale(float(self.squareWidth) /
                                      newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                newPieceItem.pieceDragStarting.connect(
                    self.pieceDragStartingEvent)
                newPieceItem.pieceDragStopping.connect(
                    self.pieceDragStoppingEvent)
                newSquareWidget.addPiece(newPieceItem)
            self.addItem(newSquareWidget)
            self.squareWidgets.append(newSquareWidget)

    def pieceClickedGraphicsEvent(self, lastSelection, square):
        # Clicking on a new piece selects it.
        if lastSelection != square:
            self.squareWidgets[square].isSelected = True
            self.squareWidgets[square].addEffectItem(SquareWidget.Selected)
        else:
            self.selectedSquare = -1
            return
        # Add the valid move squares
        for m in self.parent().game.legal_moves:
            if m.from_square == self.selectedSquare:
                self.squareWidgets[m.to_square].addEffectItem(
                    SquareWidget.ValidMove)
                self.squareWidgets[m.to_square].isValidMove = True

    def pieceClickedEvent(self, square):
        # This is a two-click capture move.
        if (self.parent().game.piece_at(square).color !=
                self.parent().game.turn):
            if self.selectedSquare != -1:
                self.pieceDroppedEvent(square)
            return
        lastSelection = self.selectedSquare
        # Clicking on a new or old piece deselects the previous squares
        self.deselectSquaresEvent()
        self.selectedSquare = square
        self.pieceClickedGraphicsEvent(lastSelection, square)

    def pieceDragStartingEvent(self, square):
        self.dragPieceCursor = self.squareWidgets[square].pieceItem
        self.squareWidgets[square].removePiece()
        self.dragPieceCursor.setZValue(150)
        pieceImg = QPixmap(self.squareWidth, self.squareWidth)
        pieceImg.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pieceImg)
        self.dragPieceCursor.renderer().render(painter)
        painter.end()
        self.dragPieceBehind = QGraphicsPixmapItem(pieceImg)
        self.dragPieceBehind.setCursor(self.pieceDraggingCursor)
        pos = self.squareWidgets[square].pos()
        self.dragPieceBehind.setPos(pos)
        self.dragPieceBehind.setOpacity(0.5)
        self.addItem(self.dragPieceBehind)

    def squareWidgetAt(self, pos):
        file = 7 - int(pos.y() / self.squareWidth)
        rank = int(pos.x() / self.squareWidth)
        if file in range(7) and rank in range(7):
            return self.squareWidgets[file * 8 + rank]
        else:
            return None

    def pieceDragStoppingEvent(self, square, mousePos):
        assert(self.dragPieceBehind is not None)
        self.removeItem(self.dragPieceBehind)
        self.dragPieceBehind = None
        assert(self.dragPieceCursor is not None)
        self.squareWidgets[square].addPiece(self.dragPieceCursor)
        self.dragPieceCursor = None

        toWidget = self.squareWidgetAt(mousePos)
        if toWidget is not None and toWidget.isValidMove:
            print("attempt", chess.Move(square, toWidget.square))
            self.pieceDroppedEvent(square, toWidget.square)
        else:
            self.deselectSquaresEvent()
            return

    def pieceDroppedEvent(self, fromSquare, toSquare):
        """
        Passes the move to the parent. Then updates the board graphics.
        :param fromSquare: Square move is from
        :param toSquare: Square move is to
        :return: None
        """
        m = chess.Move(fromSquare, toSquare)
        self.parent().doMove(m)
        self.pieceIsDragging = False

    def updatePositionAfterMove(self, move, isEnPassant):
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
                                     not self.parent().game.turn))
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

        if self.parent().game.is_queenside_castling(move):
            newPieceItem = PieceItem(self.squareWidgets[move.to_square - 2].
                                     pieceItem.piece, move.to_square + 1)
            newPieceItem.setScale(float(self.squareWidth) /
                                  newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[move.to_square - 2].removePiece()
            self.squareWidgets[move.to_square + 1].addPiece(newPieceItem)
        elif self.parent().game.is_kingside_castling(move):
            newPieceItem = PieceItem(self.squareWidgets[move.to_square + 1].
                                     pieceItem.piece, move.to_square - 1)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.
                                  boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[move.to_square + 1].removePiece()
            self.squareWidgets[move.to_square - 1].addPiece(newPieceItem)
        elif isEnPassant:
            # remember we are updating after the move has occurred
            if self.parent().game.turn == chess.BLACK:
                self.squareWidgets[move.to_square - 8].removePiece()
            else:
                self.squareWidgets[move.to_square + 8].removePiece()

        for s in self.squareWidgets:
            p = self.parent().game.piece_at(s.square)
            if s.square == move.from_square or s.square == move.to_square:
                s.clearEffectItems()
                s.addEffectItem(SquareWidget.LastMove)
            elif (self.parent().game.is_check() and p is not None and
                    p.piece_type == chess.KING and
                    p.color == self.parent().game.turn):
                s.addEffectItem(SquareWidget.CheckSquare)
            else:
                s.clearEffectItems()
            s.isValidMove = False
        self.selectedSquare = -1

    def deselectSquaresEvent(self):
        for s in self.squareWidgets:
            if s.isValidMove:
                s.isValidMove = False
                s.removeEffectItem(SquareWidget.ValidMove)
        self.squareWidgets[self.selectedSquare].removeEffectItem(
            SquareWidget.Selected)
        self.selectedSquare = -1

    def refreshPosition(self):
        """
        Clears all pieces and creates new pieces according to
        self.parent().game.
        Also clears the selected square and adds check effects if in check.
        :return: Void
        """
        for s in self.squareWidgets:
            s.removePiece()
            p = self.parent().game.piece_at(s.square)
            if p is not None:
                newPieceItem = PieceItem(p, s.square)
                newPieceItem.setScale(float(self.squareWidth) /
                                      newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                s.addPiece(newPieceItem)
                if self.parent().game.is_check() and p is not None \
                   and p.piece_type == chess.KING \
                   and p.color == self.parent().game.turn:
                    s.addEffectItem(SquareWidget.CheckSquare)
        self.selectedSquare = -1
