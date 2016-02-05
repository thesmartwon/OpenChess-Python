from PyQt5.QtWidgets import QGraphicsScene, QTreeView
from widgets.square import SquareWidget, PieceItem
import chess
import userConfig

# TODO: remove all .config['BOARD']['squareWidth'] so as to allow different widths


class BoardScene(QGraphicsScene):
    """
    Contains SquareItems. To do moves it requires that the parent have a self.game = chess.Board().
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.squareWidgets = []
        self.squareWidth = int(userConfig.config['BOARD']['squareWidth'])
        for i in range(64):
            row = 8 - int(i / 8)
            col = i % 8
            p = self.parent().game.piece_at(i)

            newSquareItem = SquareWidget(i, bool(p))
            newSquareItem.setPos(self.squareWidth * col, self.squareWidth * row)
            newSquareItem.pieceReleased.connect(self.doMove)
            newSquareItem.invalidDrop.connect(self.resetSquares)

            if p is not None:
                newPieceItem = PieceItem(p, i)
                newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
                newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
                newSquareItem.addPiece(newPieceItem)
            self.addItem(newSquareItem)
            self.squareWidgets.append(newSquareItem)

        self.selectedSquare = -1

    def pieceClickedEvent(self, square):
        for s in self.squareWidgets:
            if s.state != SquareWidget.Normal and s.state != SquareWidget.LastMove:
                s.setState(SquareWidget.Normal)
        if self.parent().game.piece_at(square).color != self.parent().game.turn:
            return
        lastSelection = self.selectedSquare
        self.selectedSquare = square
        if lastSelection != square:
            self.squareWidgets[square].setState(SquareWidget.Selected)
        else:
            self.selectedSquare = -1
        for m in self.parent().game.generate_legal_moves():
            if m.from_square == self.selectedSquare:
                self.squareWidgets[m.to_square].setState(SquareWidget.PossibleMove)

    def doMove(self, toSquare):
        m = chess.Move(self.selectedSquare, toSquare)
        if self.parent().makeMove(m):
            newPieceItem = PieceItem(self.squareWidgets[self.selectedSquare].pieceItem.piece, toSquare)
            newPieceItem.setScale(float(self.squareWidth) / newPieceItem.boundingRect().width())
            newPieceItem.pieceClicked.connect(self.pieceClickedEvent)
            self.squareWidgets[self.selectedSquare].removePiece()
            self.squareWidgets[toSquare].removePiece()
            self.squareWidgets[toSquare].addPiece(newPieceItem)
            for s in self.squareWidgets:
                if s.square == self.selectedSquare or s.square == toSquare:
                    s.setState(SquareWidget.LastMove)
                else:
                    s.setState(SquareWidget.Normal)
        self.selectedSquare = -1

    def resetSquares(self):
        for s in self.squareWidgets:
            s.setState(SquareWidget.Normal)
            self.selectedSquare = -1

