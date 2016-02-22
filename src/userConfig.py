import configparser
import constants


# TODO: rip the cool chess icons from lichess <
# TODO: generate default config if user doesn't have one
config = configparser.ConfigParser()
config.read(constants.CONFIG_PATH)


def saveFile(filename):
    with open(filename, 'w') as configfile:
        config.write(configfile)
