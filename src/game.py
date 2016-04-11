from PyQt5.QtCore import pyqtSignal, QObject, QDir
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from chess import pgn
import os
import constants
import strings


class OpenChessGame(QObject):
    moveDone = pyqtSignal(pgn.GameNode)
    positionChanged = pyqtSignal(pgn.GameNode)
    positionScrolled = pyqtSignal(pgn.GameNode)
    """
    OpenGame is a helper class that houses the game state and
    recieves/sends messages whenever it is updated.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.fileHandle = None
        self.game = pgn.Game()
        self.updateCurrent(self.game.root())

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        If the move overwrites the current main line, this widget
        will ask whether to demote the current line or not.
        :param move: A chess.Move without promotion
        :return: True if the move was able to be made, False
        otherwise
        """
        assert(move in self.board.legal_moves)
        if self.current.is_end():
            self.current.add_main_variation(move)
            print('appending %s (%s)' % (self.board.san(move), str(move)))
            self.updateCurrent(self.current.variation(move))
            self.moveDone.emit(self.current)
        elif move not in [v.move for v in self.current.variations]:
            varOption = VariationMessageBox(self.parent()).exec_()
            if varOption == 1:
                self.current.add_variation(move)
                print('adding variation %s (%s)' % (self.board.san(move),
                                                    str(move)))
                self.updateCurrent(self.current.variation(move))
                self.moveDone.emit(self.current)
            elif varOption == 0:
                if self.current.variations:
                    self.current.demote(self.current.variations[0])
                self.current.add_main_variation(move)
                print('overwriting %s (%s)' % (self.board.san(move),
                                               str(move)))
                self.updateCurrent(self.current.variation(move))
                self.positionChanged.emit(self.current)
            else:
                print('rejected %s (%s)' % (self.board.san(move),
                                            str(move)))
        else:
            self.updateCurrent(self.current.variation(move))
            self.positionScrolled.emit(self.current)

    def updateCurrent(self, newCur):
        self.current = newCur
        self.board = self.current.board()
        constants.CURRENT_GAME_BOARD = self.board

    def newGame(self, newGamePath=None):
        if newGamePath:
            with open(newGamePath) as pgnFile:
                self.game = pgn.read_game(pgnFile)
            print('opened', newGamePath)
        else:
            print('new game')
            self.fileHandle = None
            self.game = pgn.Game()
        self.updateCurrent(self.game.root())
        self.positionChanged.emit(self.current)

    def openGame(self):
        path = QFileDialog.getOpenFileName(self.parent(),
                                           'Open PGN',
                                           QDir.homePath(),
                                           filter='*.pgn')
        self.newGame(path[0])
        self.fileHandle = path

    def writeGame(self, filePath):
        print('saving', filePath)
        with open(filePath, 'w') as newPgn:
            exporter = pgn.FileExporter(newPgn)
            self.game.accept(exporter)

    def saveGame(self):
        if not (self.fileHandle and os.path.isfile(self.fileHandle)):
            self.saveGameAs()
            return
        self.writeGame(self.fileHandle)

    def saveGameAs(self):
        path = QFileDialog.getSaveFileName(self.parent(),
                                           'Save PGN',
                                           QDir.homePath(),
                                           filter='*.pgn\n*.*')
        if path[0]:
            self.writeGame(path[0])
            self.fileHandle = path[0]

    def scrollToNode(self, moveNode):
        if self.current == moveNode:
            return
        print('scrolling to', moveNode.board().fen())
        self.updateCurrent(moveNode)
        self.positionScrolled.emit(moveNode)

    def scrollInDirection(self, direction, mustBeMainVar=False,
                          mustBeVar=False):
        assert not (mustBeMainVar and mustBeVar)
        curNode = self.current
        while True:
            if direction < 0:
                if curNode.parent:
                    curNode = curNode.parent
                else:
                    self.scrollToNode(curNode)
                    break
            elif curNode.variations:
                curNode = curNode.variations[0]
            else:
                self.scrollToNode(curNode)
                break

            if mustBeMainVar:
                if curNode.is_main_variation():
                    self.scrollToNode(curNode)
                    break
            elif mustBeMainVar:
                if not curNode.is_main_variation():
                    self.scrollToNode(curNode)
                    break

    def editBoard(self):
        print('editing board')


class VariationMessageBox(QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(strings.GAME_VARIATION_ERROR)
        self.setText(strings.GAME_VARIATION)
        self.addButton(QMessageBox.Cancel)
        self.addButton('Overwrite', QMessageBox.NoRole)
        self.addButton('Add as variation', QMessageBox.YesRole)
