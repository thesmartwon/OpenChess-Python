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
        if self.parent().game.piece_at(square).color != self.parent().game.turn and self.selectedSquare != -1:
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
        assert m in self.parent().game.generate_legal_moves()
        # TODO: support king takes rook castling
        # I'm going to stay consistent with python.chess's implementation of castling.
        # Oddly enough, it 'e1g1' or 'e1c1'.
        castling = 0
        if self.parent().game.is_kingside_castling(m):
            castling = 1
        elif self.parent().game.is_queenside_castling(m):
            castling = 2

        if self.parent().doMove(m):
            self.updatePositionAfterMove(toSquare, castling)

    def updatePositionAfterMove(self, toSquare, castling):
        """
        Updates the board graphics one valid move forward. This is faster than calling refreshPosition.
        :param toSquare: square move is to. fromSquare is already stored
        :param castling: 0 for none, 1 for kingside, 2 for queenside
        :return:
        """
        newPieceItem = PieceItem(self.squareWidgets[self.selectedSquare].pieceItem.piece, toSquare)
        newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
        newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
        self.squareWidgets[self.selectedSquare].removePiece()
        self.squareWidgets[toSquare].removePiece()
        self.squareWidgets[toSquare].addPiece(newPieceItem)
        if castling == 2:
            newPieceItem = PieceItem(self.squareWidgets[toSquare - 2].pieceItem.piece, toSquare + 1)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[toSquare - 2].removePiece()
            self.squareWidgets[toSquare + 1].addPiece(newPieceItem)
        elif castling == 1:
            newPieceItem = PieceItem(self.squareWidgets[toSquare + 1].pieceItem.piece, toSquare - 1)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[toSquare + 1].removePiece()
            self.squareWidgets[toSquare - 1].addPiece(newPieceItem)

        for s in self.squareWidgets:
            p = self.parent().game.piece_at(s.square)
            if s.square == self.selectedSquare or s.square == toSquare:
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
