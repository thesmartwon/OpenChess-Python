import os


CURRENT_WORKING_DIRECTORY = os.getcwd()
ROOT_DIRECTORY = CURRENT_WORKING_DIRECTORY[:CURRENT_WORKING_DIRECTORY.
                                           index('OpenChess')+len('OpenChess')]
CONFIG_PATH = ROOT_DIRECTORY + '\\settings.ini'
RESOURCES_PATH = ROOT_DIRECTORY + '\\resources'
# TODO: fix cburnett to be pure white
PIECE_TYPE_FILE_DICT = {'P': 'wp.svg', 'p': 'bp.svg',
                        'R': 'wr.svg', 'r': 'br.svg',
                        'N': 'wn.svg', 'n': 'bn.svg',
                        'B': 'wb.svg', 'b': 'bb.svg',
                        'Q': 'wq.svg', 'q': 'bq.svg',
                        'K': 'wk.svg', 'k': 'bk.svg'}
GAME_STATE = None
PIECE_PADDING_RIGHT = 9
PIECE_PADDING_BOT = 15
HAS_FOCUS = True
