from resources.colours import *
import random
import pygame

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
borderSize = 10


def loadDictionaries(substring):
    indice = [i for i, s in enumerate(dataLocations) if substring in s]

    try:
        with open(dataLocations[indice[0]], 'r') as dictionary:
            result = eval(dictionary.read())
            dictionary.close()
            return result
    except IndexError:
        print('Nothing enumerable, skipping...\nPlease replace empty lines with a #!')


def loadTxt(location):
    with open(location, 'r') as file:
        result = file.read()
        file.close()
        return result


def cRC(limit):  # createRandomCoordinates
    return random.randint(limit / 10, limit - 4 * borderSize)


dataLocations = []
with open('resources/list.txt', 'r') as locationList:
    for line in locationList:
        if '#' not in line:
            dataLocations.append('resources/' + line.strip('\n'))
locationList.close()
