from PyQt5.QtWidgets import QGraphicsScene
from widgets.square import SquareWidget, PieceItem
import chess
import userConfig
# TODO: remove all .config['BOARD']['squareWidth'] so as to allow different widths
# this class is very important to me, let's keep it pretty


class BoardScene(QGraphicsScene):
    """
    Contains and manages SquareItems interacting with each other.
    Sends moves up to the parent, which must have a self.game = chess.Board().
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.squareWidgets = []
        self.squareWidth = int(userConfig.config['BOARD']['squareWidth'])
        self.selectedSquare = -1
        for i in range(64):
            row = 8 - int(i / 8)
            col = i % 8
            p = self.parent().game.piece_at(i)
            newSquareItem = SquareWidget(i)
            newSquareItem.setPos(self.squareWidth * col, self.squareWidth * row)
            newSquareItem.pieceReleased.connect(self.pieceDroppedEvent)
            newSquareItem.invalidDrop.connect(self.deselectSquaresEvent)
            if p is not None:
                newPieceItem = PieceItem(p, i)
                newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                newSquareItem.addPiece(newPieceItem)
            self.addItem(newSquareItem)
            self.squareWidgets.append(newSquareItem)

    def pieceClickedEvent(self, square):
        # This is a two-click capture move.
        if self.parent().game.piece_at(square).color != self.parent().game.turn:
            if self.selectedSquare != -1:
                self.pieceDroppedEvent(square)
            return
        lastSelection = self.selectedSquare
        self.selectedSquare = square
        # Clicking on an new or old piece deselects it, and adds effects.
        for s in self.squareWidgets:
            if s.isValidMove:
                s.isValidMove = False
                s.removeEffectItem(SquareWidget.ValidMove)
        self.squareWidgets[lastSelection].removeEffectItem(SquareWidget.Selected)
        # Clicking on a new piece selects it.
        if lastSelection != square:
            self.squareWidgets[square].isSelected = True
            self.squareWidgets[square].addEffectItem(SquareWidget.Selected)
        else:
            self.selectedSquare = -1
        # Add the valid move squares
        for m in self.parent().game.generate_legal_moves():
            if m.from_square == self.selectedSquare:
                self.squareWidgets[m.to_square].addEffectItem(SquareWidget.ValidMove)
                self.squareWidgets[m.to_square].isValidMove = True

    def pieceDroppedEvent(self, toSquare):
        """
        Passes the move to the parent. Then updates the board graphics.
        :param toSquare: Received from the Square
        :return: None
        """
        m = chess.Move(self.selectedSquare, toSquare)
        self.parent().doMove(m)

    def updatePositionAfterMove(self, move, en_passant_square):
        """
        Updates the board graphics one valid move forward. This is faster than calling refreshPosition.
        :param move: the move that happened on the board
        :return: void
        """
        if move.promotion is None:
            newPieceItem = PieceItem(self.squareWidgets[move.from_square].pieceItem.piece, move.to_square)
        else:
            newPieceItem = PieceItem(chess.Piece(move.promotion, not self.parent().game.turn), move.to_square)
        newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
        newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
        self.squareWidgets[move.from_square].removePiece()
        self.squareWidgets[move.to_square].removePiece()
        self.squareWidgets[move.to_square].addPiece(newPieceItem)
        # TODO: support king takes rook castling
        # I'm going to stay consistent with python.chess's implementation of castling.
        # Oddly enough, it 'e1g1' or 'e1c1'.
        castling = -1
        if self.parent().game.is_kingside_castling(move):
            castling = 0
        elif self.parent().game.is_queenside_castling(move):
            castling = 1

        if castling == 1:
            newPieceItem = PieceItem(self.squareWidgets[move.to_square - 2].pieceItem.piece, move.to_square + 1)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[move.to_square - 2].removePiece()
            self.squareWidgets[move.to_square + 1].addPiece(newPieceItem)
        elif castling == 0:
            newPieceItem = PieceItem(self.squareWidgets[move.to_square + 1].pieceItem.piece, move.to_square - 1)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[move.to_square + 1].removePiece()
            self.squareWidgets[move.to_square - 1].addPiece(newPieceItem)
        elif en_passant_square != -1:
            self.squareWidgets[en_passant_square].removePiece()

        for s in self.squareWidgets:
            p = self.parent().game.piece_at(s.square)
            if s.square == move.from_square or s.square == move.to_square:
                s.clearEffectItems()
                s.addEffectItem(SquareWidget.LastMove)
            elif self.parent().game.is_check() and p is not None and p.piece_type == chess.KING \
                    and p.color == self.parent().game.turn:
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
        self.squareWidgets[self.selectedSquare].removeEffectItem(SquareWidget.Selected)
        self.selectedSquare = -1

    def refreshPosition(self):
        """
        Clears all pieces and creates new pieces according to self.parent().game
        Also clears the selected square and adds check effects if in check.
        :return: Void
        """
        for s in self.squareWidgets:
            s.removePiece()
            p = self.parent().game.piece_at(s.square)
            if p is not None:
                newPieceItem = PieceItem(p, s.square)
                newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                s.addPiece(newPieceItem)
                if self.parent().game.is_check() and p is not None and p.piece_type == chess.KING \
                        and p.color == self.parent().game.turn:
                    s.addEffectItem(SquareWidget.CheckSquare)
        self.selectedSquare = -1
