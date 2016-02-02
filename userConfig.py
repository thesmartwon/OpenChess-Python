import configparser


# TODO: rip the cool ches icons from lichess <
# TODO: generate default config if user doesn't have one
config = configparser.ConfigParser()
config.read('settings.ini')


def saveFile(filename):
    with open(filename, 'w') as configfile:
        config.write(configfile)
