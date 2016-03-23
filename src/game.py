from PyQt5.QtWidgets import QDialog
import chess
from chess import pgn
import constants


class OpenGame():
    """
    OpenGame is a helper class that houses the game state and
    recieves/sends messages whenever it is updated.
    Must call setWeakRefs before doMove.
    """
    def __init__(self):
        self.game = pgn.Game()
        self.current = self.game.root()
        self.board = self.game.root().board()
        constants.GAME_STATE = self.board
        constants.HERO = chess.WHITE

    def setWeakRefs(self, centralFrame, boardScene, moveTreeModel, engine):
        self.centralFrame = centralFrame
        self.moveTreeModel = moveTreeModel
        self.boardScene = boardScene
        self.engine = engine

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        If the move is a promotion, this widget will send a message
        to the board to ask for it.
        If the move overwrites the current main line, this widget
        will ask for the default option.
        :param move: A chess.Move without promotion
        :return: True if the move was able to be made, False
        otherwise
        """
        myPossibleMoves = [m for m in self.board.legal_moves
                           if m.from_square == move.from_square and
                           m.to_square == move.to_square]
        move = myPossibleMoves[0]
        assert move
        if move.promotion is not None:
            # TODO: ask for a real promotion piece
            print('promoting to queen')
            move.promotion = chess.QUEEN
        assert(move in self.board.legal_moves)
        if move in self.board.legal_moves:
            if self.current.is_end():
                self.current.add_main_variation(move)
            elif move not in [v.move for v in self.current.variations]:
                response = True # VariationDialog(self.centralFrame)
                if response:
                    self.current.add_variation(move)
                else:
                    mainVar = [m for m in self.current.variations if
                               m.is_main_variation()]
                    if mainVar:
                        self.current.demote(mainVar[0])
                    self.current.add_main_variation(move)
            self.current = self.current.variation(move)
            self.board = self.current.board()
            constants.GAME_STATE = self.board
            self.moveTreeModel.updateAfterMove(self.current)
            self.boardScene.updatePositionAfterMove(self.board)
            self.engine.updateAfterMove(self.board)
            return True
        return False

    def newGame(self):
        print('new game')
        self.board.reset()
        self.game.setup(self.board)
        self.engine.reset(self.board, True)
        self.moveTreeModel.reset(self.game)
        self.boardScene.reset(self.board)

    def scrollToPly(self, plyNumber):
        curPly = self.board.fullmove_number * 2 + int(not self.board.turn) - 2
        assert curPly >= plyNumber
        if curPly == plyNumber:
            return
        print('scrolling to', plyNumber)
        for i in range(curPly - plyNumber - 1):
            self.current = self.current.parent
        self.board = self.current.board()
        self.engine.reset(self.board)
        # self.moveTreeModel.eraseAfterPly(plyNumber)
        self.boardScene.reset(self.board)

    def editBoard(self):
        print('editing board')
        self.board.reset()
        self.board.clear_board()


class VariationDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText('')
