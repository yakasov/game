import random
import numpy


def generator(lines):
    for line in lines:
        for i, cell in enumerate(line):
            requirement = random.randint(0, 100)
            result = random.randint(0, 80)

            if result > requirement:
                line[i] = 1
            if result >= 72:
                line[i] = 2

    lines[7][0] = 1
    lines[7][1] = 1
    lines[8][0] = 1
    lines[8][1] = 1
    lines[0][8] = 3

    return lines


def patcher(lines):
    for line in lines:
        for i, cell in enumerate(line):
            try:
                if line[i] == 0:
                    if (line[i - 1] + line[i + 1] + lines[lines.index(line) - 1][i] + lines[lines.index(line) + 1][i]) > 2:
                        line[i] = 1
            except IndexError:
                pass

    return lines


def invert(lines):
    invertedLines = []
    for line in lines:
        newLine = []
        for cell in line:
            if cell == 0:
                cell = 1
            else:
                cell = 0
            newLine.append(cell)
        invertedLines.append(newLine)

    return invertedLines


def solver(invertedLines):
    x = 0
    y = 0

    for i in range(5000):
        prevX = x
        prevY = y
        move = random.randint(0, 3)

        if move == 0 and x != 0:
            x -= 1
        if move == 1 and x != 8:
            x += 1
        if move == 2 and y != 0:
            y -= 1
        if move == 3 and y != 8:
            y += 1

        if x == 8 and y == 8:
            return True
        elif invertedLines[y][x] == 1:
            x = prevX
            y = prevY


def mazeMaker(state):
    while True:
        lines = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for i, cell in enumerate(lines):
            lines[i] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        lines = generator(lines)
        lines = patcher(lines)
        lines = numpy.flip(lines, 0)

        invertedLines = invert(lines)
        passes = solver(invertedLines)

        if passes:
            lines = numpy.asarray(lines)
            if state == 'print':
                print('\n')
                for line in lines:
                    print(line)
            return lines
