import os


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
GAME_STATE = None
# True is white. False is black.
HERO = True
PIECE_PADDING_RIGHT = .162
PIECE_PADDING_BOT = .3
HAS_FOCUS = True
IDEAL_RESOLUTION = {'width': 1049, 'height': 928}
