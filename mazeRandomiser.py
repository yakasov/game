import random, numpy
lines = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for i in range(len(lines)):
    lines[i] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

def generator():
    for line in lines:
        for i in range(len(line)):
            requirement = random.randint(0, 100)
            result = random.randint(0, 100)

            if result > requirement:
                line[i] = 1
            if result >= 90:
                line[i] = 2

    lines[7][0] = 1
    lines[7][1] = 1
    lines[8][0] = 1
    lines[8][1] = 1
    lines[0][8] = 3

def checker():
    for line in lines:
        for i in range(len(line)):
            try:
                if (line[i - 1] + line[i + 1] + lines[lines.index(line) - 1][i] + lines[lines.index(line) + 1][i]) == 0:
                    line[i] = 0
            except:
                pass

def patcher():
    for line in lines:
        for i in range(len(line)):
            try:
                if line[i] == 0:
                    if (line[i - 1] + line[i + 1] + lines[lines.index(line) - 1][i] + lines[lines.index(line) + 1][i]) > 2:
                        line[i] = 1
            except:
                pass

generator()
checker()
patcher()
lines = numpy.flip(lines, 0)

for line in lines:
    print(line)
