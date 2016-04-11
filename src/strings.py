import chess


COLOR_FIRST = 'White'
COLOR_SECOND = 'Black'
FILE_NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
RANK_NAMES = ['1', '2', '3', '4', '5', '6', '7', '8']
PIECE_SYMBOLS = ['R', 'N', 'B', 'Q', 'K']

MENU_FILE = '&File'
MENU_BOARD = '&Board'
MENU_NEW = '&New Game'
MENU_NEW_TIP = 'Start a new game'
MENU_OPEN = '&Open Game'
MENU_OPEN_TIP = 'Open a new game'
MENU_SAVE = '&Save Game'
MENU_SAVE_TIP = 'Save the current game'
MENU_SAVEAS = '&Save Game As'
MENU_SAVEAS_TIP = 'Save the current game to a new file'
MENU_QUIT = '&Quit'
MENU_QUIT_TIP = 'Exit application'
MENU_EDITBOARD = '&Setup a position'
MENU_EDITBOARD_TIP = 'Add or remove pieces from the current position'
MENU_FLIP = '&Flip'
MENU_FLIP_TIP = 'Flip the current board'

GAME_VARIATION_ERROR = 'Move already exists'
GAME_VARIATION = 'That move already exists. Would you like to add this move as a variation, or would you like to overwrite the mainline?'
BOARD_ERROR_DICT = {chess.STATUS_NO_WHITE_KING: 'There is no white king',
                    chess.STATUS_NO_BLACK_KING: 'There is no black king',
                    chess.STATUS_TOO_MANY_KINGS: 'There are too many kings',
                    chess.STATUS_TOO_MANY_WHITE_PAWNS: 'There are more than 8 white pawns',
                    chess.STATUS_TOO_MANY_BLACK_PAWNS: 'There are more than 8 black pawns',
                    chess.STATUS_PAWNS_ON_BACKRANK: 'There are unpromoted pawns on the backrank.',
                    chess.STATUS_TOO_MANY_WHITE_PIECES: 'There are too many white rooks, bishops, knights, or queens.',
                    chess.STATUS_TOO_MANY_BLACK_PIECES: 'There are too many black rooks, bishops, knights, or queens.',
                    chess.STATUS_BAD_CASTLING_RIGHTS: 'The given castling rights are not possible given the position.',
                    chess.STATUS_INVALID_EP_SQUARE: 'The en passant square set is not possible given the position',
                    chess.STATUS_OPPOSITE_CHECK: 'Both kings are in check'}
BOARD_ERROR = 'This position is invalid. It has the following errors:'
BOARD_ERROR_CONTINUE = 'Would you like to continue anyway?'
BOARD_ERROR_TITLE = 'Invalid Position'
