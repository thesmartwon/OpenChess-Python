from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QDialog
import chess
from chess import pgn
import constants


class OpenChessGame(QObject):
    moveDone = pyqtSignal(pgn.GameNode)
    positionChanged = pyqtSignal(pgn.GameNode)
    newGameOpened = pyqtSignal(pgn.GameNode)
    """
    OpenGame is a helper class that houses the game state and
    recieves/sends messages whenever it is updated.
    Must call setWeakRefs before doMove.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.game = pgn.Game()
        self.updateCurrent(self.game.root())

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        If the move is a promotion, this widget will send a message
        to the board to ask for it.
        If the move overwrites the current main line, this widget
        will ask whether to demote the current line or not.
        :param move: A chess.Move without promotion
        :return: True if the move was able to be made, False
        otherwise
        """
        if (self.board.piece_at(move.from_square).piece_type == chess.PAWN and
                chess.rank_index(move.to_square) in [0, 7]):
            # TODO: ask for a real promotion piece
            print('promoting to queen')
            move.promotion = chess.QUEEN
        assert(move in self.board.legal_moves)
        if self.current.is_end():
            self.current.add_main_variation(move)
        elif move not in [v.move for v in self.current.variations]:
            response = True  # VariationDialog(self.parent())
            if response:
                self.current.add_variation(move)
            else:
                mainVar = [m for m in self.current.variations if
                           m.is_main_variation()]
                if mainVar:
                    self.current.demote(mainVar[0])
                self.current.add_main_variation(move)
        self.updateCurrent(self.current.variation(move))
        self.moveDone.emit(self.current)

    def updateCurrent(self, newCur):
        self.current = newCur
        self.board = self.current.board()
        constants.CURRENT_GAME_BOARD = self.board

    def newGame(self, newGamePath=None):
        if newGamePath:
            try:
                pgnFile = open(newGamePath)
                self.game = pgn.read_game(pgnFile)
                print('opened', newGamePath)
            except Exception:
                print('failed to open', newGamePath)
                print('new game')
                self.game = pgn.Game()
                raise Exception
        else:
            print('new game')
            self.game = pgn.Game()
        self.game.setup(chess.Board())
        self.current = self.game.root()
        self.board = self.current.board()
        constants.CURRENT_GAME_BOARD = self.board
        self.newGameOpened.emit(self.current)

    def openGame(self):
        # TODO: fetch path
        path = 'C:/Users/thesm/Documents/Chess/game1.pgn'
        self.newGame(path)

    def scrollToMove(self, moveNode):
        if self.current == moveNode:
            return
        self.updateCurrent(moveNode)
        # movetree stays the same
        self.positionChanged.emit(self.current)

    def editBoard(self):
        print('editing board')
        self.board.reset()
        self.board.clear_board()


class VariationDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText('')
