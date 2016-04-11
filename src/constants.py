import os
import chess


# TODO: put this all in userConfig
CURRENT_WORKING_DIRECTORY = os.getcwd().replace('\\', '/')
ROOT_DIRECTORY = CURRENT_WORKING_DIRECTORY[:CURRENT_WORKING_DIRECTORY.
                                           index('OpenChess')+len('OpenChess')]
CONFIG_PATH = ROOT_DIRECTORY + '/settings.ini'
RESOURCES_PATH = ROOT_DIRECTORY + '/resources'
ENGINES_PATH = ROOT_DIRECTORY + '/engines'
# TODO: fix cburnett to be pure white
PIECE_TYPE_FILE_DICT = {'P': 'wp.svg', 'p': 'bp.svg',
                        'R': 'wr.svg', 'r': 'br.svg',
                        'N': 'wn.svg', 'n': 'bn.svg',
                        'B': 'wb.svg', 'b': 'bb.svg',
                        'Q': 'wq.svg', 'q': 'bq.svg',
                        'K': 'wk.svg', 'k': 'bk.svg'}
CHESS_ERRORS = [chess.STATUS_NO_WHITE_KING, chess.STATUS_TOO_MANY_BLACK_PIECES,
                chess.STATUS_TOO_MANY_KINGS, chess.STATUS_TOO_MANY_BLACK_PAWNS,
                chess.STATUS_TOO_MANY_WHITE_PAWNS, chess.STATUS_OPPOSITE_CHECK,
                chess.STATUS_PAWNS_ON_BACKRANK, chess.STATUS_INVALID_EP_SQUARE,
                chess.STATUS_BAD_CASTLING_RIGHTS, chess.STATUS_NO_BLACK_KING,
                chess.STATUS_TOO_MANY_WHITE_PIECES]
CURRENT_GAME_BOARD = None
PIECE_PADDING_RIGHT = .162
PIECE_PADDING_BOT = .3
MOVE_ITEM_PADDING = 8
HAS_FOCUS = True
IDEAL_RESOLUTION = {'width': 1049, 'height': 910}
