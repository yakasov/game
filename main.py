import pygame
import random
import time
import numpy
from dictResolver import *
from mazeRandomiser import *
from pygame.locals import *
pygame.init()

COLOURS = loadDictionaries('colours')


class player():
    def __init__(self):
        self.modelWidth = 15
        self.modelHeight = 15
        self.model = pygame.Rect(25, 40, self.modelWidth, self.modelHeight)
        self.colour = COLOURS['WHITE']
        self.vel = 5

        self.score = 0

        self.projectiles = []
        self.projVel = 8
        self.projColour = COLOURS['WHITE']
        self.projFireRate = 100  # How long the player must wait before firing again
        self.lastFireTime = 0

        self.health = 100
        self.healthMax = 100
        self.healthBarBase = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, 50)
        self.healthBar = pygame.Rect(
            0, WINDOW_HEIGHT, self.health * (WINDOW_WIDTH / self.healthMax), 50)
        self.flashTime = 0
        self.invulnerabilityTime = 0
        # Temporary storage for when the next player invulnerability flash can occur

    def updateHealth(self):
        self.healthBar = pygame.Rect(
            0, WINDOW_HEIGHT, self.health * (WINDOW_WIDTH / self.healthMax), 50)

    def checkHealth(self):
        if self.health > self.healthMax:
            self.health = self.healthMax

        self.updateHealth()

        if self.health <= 0:
            for i in range(52):
                x = 0 + i * 5
                WINDOW.fill((x, x, x))
                pygame.display.update()
                time.sleep(0.0512)
            gameOverText = LARGE_FONT.render(
                'Game Over', True, COLOURS['BLACK'], COLOURS['WHITE'])
            textBox = gameOverText.get_rect()
            textBox.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
            WINDOW.blit(gameOverText, textBox)
            pygame.display.update()
            time.sleep(3)
            pygame.quit()

    def fire(self, direction, magnitude):
        self.lastFireTime = TIME
        if direction == 'x':
            xModifier = magnitude * 0.5 * self.modelWidth
            yModifier = 0
        if direction == 'y':
            yModifier = magnitude * 0.5 * self.modelHeight
            xModifier = 0

        self.newProjectile = pygame.Rect(
            self.model.centerx + xModifier, self.model.centery + yModifier, 3, 3)
        self.projectiles.append([self.newProjectile, direction, magnitude])

    def updateProjectiles(self):
        for projectile in self.projectiles:
            if projectile[1] == 'x':
                projectile[0].centerx += projectile[2] * self.projVel
            if projectile[1] == 'y':
                projectile[0].centery += projectile[2] * self.projVel

            if projectile[0].centerx > WINDOW_WIDTH or projectile[0].centerx < 0:
                self.projectiles.remove(projectile)
            if projectile[0].centery > WINDOW_HEIGHT or projectile[0].centery < 0:
                self.projectiles.remove(projectile)


class enemies():
    def __init__(self):
        self.modelWidth = 14
        self.modelHeight = 20
        self.colour = COLOURS['RED']
        self.vel = 4

        self.projectiles = []
        self.projVel = 6
        self.projColour = COLOURS['RED']
        self.projFireRate = 100  # How long the enemy must wait before firing again
        # This is a default and can differ between enemies
        self.lastFireTime = 0

        self.enemyStages = ['DEAD', COLOURS['RED'],
                            COLOURS['AQUA'], COLOURS['MAGENTA']]
        self.types = ['base', 'shooter']
        self.bossData = {
            'health': 0
        }  # Initialise bossData dictionary for use in createEnemies()
        self.bossesDefeated = 0

        self.enemyCounts = {}
        self.screenCleared = {}
        self.currentEnemies = []
        self.lastMovement = 0  # Time when the enemy last moved
        self.enemyUpdatePeriod = 50  # How long the enemy must wait before moving again

    def createEnemyCounts(self):
        for y in range(0, 9):
            for x in range(0, 9):
                if s.lines[y][x] == 1:
                    if x * y < 9:
                        e.enemyCounts[(x + 1) * 10 + (y + 1)
                                      ] = random.randint(2, 6)
                    elif x * y < 17:
                        e.enemyCounts[(x + 1) * 10 + (y + 1)
                                      ] = random.randint(4, 8)
                    elif x * y < 40:
                        e.enemyCounts[(x + 1) * 10 + (y + 1)
                                      ] = random.randint(5, 11)
                    else:
                        e.enemyCounts[(x + 1) * 10 + (y + 1)
                                      ] = random.randint(4, 14)
                elif s.lines[y][x] == 2:
                    e.enemyCounts[(x + 1) * 10 + (y + 1)] = 0

        e.enemyCounts[11] = 0
        e.enemyCounts[99] = 0
        # Spawn and end must have 0 enemy counts

    def createEnemies(self):
        self.vel = 4 + 0.33 * len(self.screenCleared)

        self.currentEnemies = []
        if s.currentScreen != 99:
            for count in range(0, self.enemyCounts[s.currentScreen]):
                self.enemy = pygame.Rect(s.createRandomCoordinates(WINDOW_WIDTH), s.createRandomCoordinates(
                    WINDOW_HEIGHT), self.modelWidth, self.modelHeight)
                if count % 3 == 0:  # Every third enemy is a 'shooter' type
                    self.type = 'shooter'
                else:
                    self.type = 'base'
                self.currentEnemies.append(
                    [self.enemy, self.colour, self.type, self.lastFireTime])

            if self.enemyCounts[s.currentScreen] == 0 and not s.currentScreen in self.screenCleared and s.currentScreen != 11:
                self.bossData['health'] = random.randint(
                    25, 40) + (self.bossesDefeated + 1) * 0.5 + len(self.screenCleared)
                self.bossData['healthMax'] = self.bossData['health']
                self.bossData['damage'] = len(self.screenCleared) * 4
                self.bossData['size'] = random.randint(100, 200)
                self.bossData['velocity'] = random.randint(
                    1, 4) + (len(self.screenCleared) / 10)
                self.bossData['type'] = self.types[random.randint(
                    0, len(self.types) - 1)]
                self.bossData['lastFireTime'] = 0

            if self.bossData['health'] > 0:
                self.previousVel = self.vel
                self.vel = self.bossData['velocity']
                self.type = self.bossData['type']
                self.boss = pygame.Rect(
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, self.bossData['size'], self.bossData['size'])
                self.currentEnemies.append(
                    [self.boss, COLOURS['RED'], self.type, self.lastFireTime])

    def updateEnemies(self):
        for enemyData in self.currentEnemies:
            enemy = enemyData[0]
            for projectile in p.projectiles:
                if projectile[0].colliderect(enemy):
                    try:
                        if self.bossData['health'] > 0:
                            self.bossData['health'] -= 1
                            if self.bossData['health'] <= 0:
                                self.vel = self.previousVel
                                p.health += 20
                                p.updateHealth()
                                self.currentEnemies.remove(enemyData)
                                self.bossesDefeated += 1
                                p.score += 500
                        else:  # If not boss, goto updateHealth()
                            self.updateHealth(enemyData)
                    except ValueError:
                        print(
                            '>>> Too many projectiles causing too many enemy kills! @ {}'.format(TIME))
                    p.projectiles.remove(projectile)

            if TIME - self.lastMovement > self.enemyUpdatePeriod:  # Move towards player
                if enemy.centerx < p.model.centerx:
                    enemy.centerx += self.vel
                else:
                    enemy.centerx -= self.vel
                if enemy.centery < p.model.centery:
                    enemy.centery += self.vel
                else:
                    enemy.centery -= self.vel

        if TIME - self.lastMovement > self.enemyUpdatePeriod:
            self.lastMovement = TIME

        if self.currentEnemies == []:
            self.enemyCounts[s.currentScreen] = 0
            self.screenCleared[s.currentScreen] = True

    def updateHealth(self, enemyData):  # Called when an enemy is hit
        enemyData[1] = self.enemyStages[self.enemyStages.index(
            enemyData[1]) - 1]  # Decrease enemy 'stage'
        if enemyData[1] == 'DEAD':
            self.currentEnemies.remove(enemyData)
            p.score += 50
        else:
            p.score += 5

    def checkEnemyCollisions(self):
        p.flashTime = TIME - p.invulnerabilityTime
        for enemyData in self.currentEnemies:
            enemy = enemyData[0]
            if TIME - p.invulnerabilityTime > 500:
                if enemy.colliderect(p.model):
                    if self.bossData['health'] > 0:
                        p.health -= self.bossData['damage']
                        p.invulnerabilityTime = TIME + 500
                    else:
                        p.health -= 20
                        p.invulnerabilityTime = TIME
                p.updateHealth()

        if TIME - p.invulnerabilityTime < 500:
            if round(p.flashTime / 50) % 2 == 0:
                p.colour = COLOURS['BLACK']
            else:
                p.colour = COLOURS['WHITE']
        else:
            p.colour = COLOURS['WHITE']

    def fire(self, enemyData):
        enemy = enemyData[0]
        enemyData[3] = TIME
        if self.bossData['health'] > 0:
            self.bossData['lastFireTime'] = enemyData[3]
        dx = p.model.centerx - enemy.centerx
        dy = p.model.centery - enemy.centery

        self.newProjectile = pygame.Rect(enemy.centerx, enemy.centery, 3, 3)
        self.projectiles.append([self.newProjectile, dx, dy])

    def updateProjectiles(self):
        for projectile in self.projectiles:
            self.dirvect = pygame.math.Vector2(projectile[1], projectile[2])
            self.dirvect.normalize()
            self.dirvect.scale_to_length(self.projVel)
            projectile[0].move_ip(self.dirvect)

            try:
                if projectile[0].centerx > WINDOW_WIDTH or projectile[0].centerx < 0:
                    self.projectiles.remove(projectile)
                if projectile[0].centery > WINDOW_HEIGHT or projectile[0].centery < 0:
                    self.projectiles.remove(projectile)

                if projectile[0].colliderect(p.model):
                    p.health -= 10
                    self.projectiles.remove(projectile)
            except ValueError:
                print('Error removing enemy projectile! @ {}'.format(TIME))


class items():
    def checkCurrentScreenItems(self):
        self.currentItems = []
        if s.currentScreen != 11:
            try:
                for item in self.items[0]:
                    if item['chance'] != 0:
                        self.currentItems.append(item)
                        item['rolled'] = 200
            except KeyError:
                print('>>> No items found with all screen spawns! @ {}'.format(TIME))
                pass
            try:
                for item in self.items[s.currentScreen]:
                    if item['chance'] != 0:
                        self.currentItems.append(item)
                        item['rolled'] = 200
            except KeyError:
                print('>>> No items found for screen {}! @ {}'.format(
                    s.currentScreen, TIME))

    def checkItemCollisions(self):
        if e.currentEnemies == []:
            for item in self.currentItems:
                if p.model.colliderect(item['model']):
                    if 'PLAYER_VELOCITY' in item['attributes']:  # Default 5
                        p.vel += item['magnitude']
                    if 'PLAYER_HEALTH' in item['attributes']:  # Default 100
                        p.healthMax += item['magnitude']
                        p.health += item['magnitude']
                    if 'PROJECTILE_VELOCITY' in item['attributes']:  # Default 8
                        p.projVel += item['magnitude'] * 2
                    if 'PROJECTILE_RATE' in item['attributes']:  # Default 100
                        p.projFireRate -= item['magnitude'] * 5
                    print('Player picked up {} @ {}'.format(item, TIME))
                    self.currentItems.remove(item)
                    item['chance'] = 0


class screens():
    def __init__(self):
        self.lines = []
        self.currentScreen = 11
        self.update = True

        self.borderColour = (51, 51, 51)
        self.borderSize = 10
        self.topBar = pygame.Rect(0, 0, WINDOW_WIDTH, self.borderSize)
        self.bottomBar = pygame.Rect(
            0, WINDOW_HEIGHT - self.borderSize, WINDOW_WIDTH, self.borderSize)
        self.rightBar = pygame.Rect(
            WINDOW_WIDTH - self.borderSize, 0, self.borderSize, WINDOW_HEIGHT)
        self.leftBar = pygame.Rect(0, 0, self.borderSize, WINDOW_HEIGHT)
        self.lettersToBorders = {'T': self.topBar,
                                 'B': self.bottomBar,
                                 'L': self.leftBar,
                                 'R': self.rightBar
                                 }

    def screenUpdate(self):
        s.currentScreen = str(s.currentScreen)
        if int(s.currentScreen[0]) > 6 or int(s.currentScreen[1]) > 6:
            e.colour = COLOURS['MAGENTA']
        elif int(s.currentScreen[0]) > 3 or int(s.currentScreen[1]) > 3:
            e.colour = COLOURS['AQUA']
        else:
            e.colour = COLOURS['RED']
        s.currentScreen = int(s.currentScreen)

        i.checkCurrentScreenItems()
        e.createEnemies()
        d.printInfo()

    def drawBorders(self):
        self.bordersToDraw = []
        if e.currentEnemies == []:
            if self.currentScreen + 10 in e.enemyCounts:
                self.bordersToDraw.append(self.rightBar)
            if self.currentScreen - 10 in e.enemyCounts:
                self.bordersToDraw.append(self.leftBar)
            if self.currentScreen + 1 in e.enemyCounts:
                self.bordersToDraw.append(self.topBar)
            if self.currentScreen - 1 in e.enemyCounts:
                self.bordersToDraw.append(self.bottomBar)
            for bar in self.bordersToDraw:
                pygame.draw.rect(WINDOW, self.borderColour, bar)
                self.checkBorderCollisions(bar)

    def drawScreenNo(self):
        screenText = NORMAL_FONT.render(
            str(s.currentScreen), True, COLOURS['RED'])
        textBox = screenText.get_rect()
        textBox.left = 2 * s.borderSize
        textBox.top = 2 * s.borderSize
        WINDOW.blit(screenText, textBox)

    def drawScore(self):
        scoreText = NORMAL_FONT.render(
            str(p.score), True, COLOURS['RED'])
        textBox = scoreText.get_rect()
        textBox.right = WINDOW_WIDTH - 2 * s.borderSize
        textBox.top = 2 * s.borderSize
        WINDOW.blit(scoreText, textBox)

    def checkBorderCollisions(self, bar):
        if p.model.colliderect(bar):
            self.screenMoveDirection(bar)
            p.projectiles = []

    def screenMoveDirection(self, bar):
        if bar == self.topBar:
            self.currentScreen += 1
            p.model.centery += WINDOW_HEIGHT - 4 * p.model.height
        if bar == self.bottomBar:
            self.currentScreen -= 1
            p.model.centery -= WINDOW_HEIGHT - 4 * p.model.height
        if bar == self.rightBar:
            self.currentScreen += 10
            p.model.centerx -= WINDOW_WIDTH - 4 * p.model.width
        if bar == self.leftBar:
            self.currentScreen -= 10
            p.model.centerx += WINDOW_WIDTH - 4 * p.model.width

        i.currentItems = []
        self.update = True

    def createRandomCoordinates(self, limit):
        return random.randint(limit / 10, limit - 4 * s.borderSize)


class debug():
    def printInfo(self):
        print('====================' +
              '\nCurrent Screen: {}'.format(s.currentScreen) +
              '\nEntering at X: {}, Y: {}'.format(p.model.centerx, p.model.centery) +
              '\n\nEnemies: {}, Velocity: {}'.format(e.enemyCounts[s.currentScreen], e.vel) +
              '\nBoss: {}, Attributes: {}'.format(self.checkBosses(), self.getBossAttributes()) +
              '\n\nItems: {}'.format(self.getItemAttributes()) +
              '\n\nPlayer Health: {}, Velocity: {}\n\n'.format(p.health, p.vel))

    def checkBosses(self):
        if e.bossData['health'] > 0:
            return True
        else:
            return False

    def getBossAttributes(self):
        if e.bossData['health'] > 0:
            return e.bossData
        else:
            return 'None'

    def getItemAttributes(self):
        self.returnString = ''
        for item in i.currentItems:
            if item['chance'] != 0:
                self.returnString += '\n  {}'.format(item)
        return self.returnString

    def commandInput(self):
        command = input().lower()
        command = command.split(' ')
        if 'map' in command:
            for line in numpy.flip(s.lines, 0):
                print(line)
        if 'god' in command:
            p.healthMax = 10**10
            p.health = p.healthMax
        if 'goto' in command:
            s.currentScreen = int(command[command.index('goto') + 1])
            s.update = True


TIME = 0
FPS = 60
FPSCLOCK = pygame.time.Clock()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + 40))

LARGE_FONT = pygame.font.SysFont('consolas', 64)
NORMAL_FONT = pygame.font.SysFont('consolas', 32)
SMALL_FONT = pygame.font.SysFont('consolas', 16)

p = player()
e = enemies()
i = items()
s = screens()
d = debug()

s.lines = mazeMaker()
e.createEnemyCounts()

i.items = loadDictionaries('items')

while True:
    pygame.time.delay(round(1000 / FPS))

    if s.update == True:
        s.screenUpdate()
        s.update = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_c]:
        d.commandInput()

    if keys[pygame.K_LEFT] and p.model.left > p.vel:
        p.model.left -= p.vel
    if keys[pygame.K_RIGHT] and p.model.right < WINDOW_WIDTH - p.vel:
        p.model.right += p.vel
    if keys[pygame.K_UP] and p.model.top > p.vel:
        p.model.top -= p.vel
    if keys[pygame.K_DOWN] and p.model.bottom < WINDOW_HEIGHT - p.vel:
        p.model.bottom += p.vel

    if TIME - p.lastFireTime >= p.projFireRate:
        if keys[pygame.K_w]:
            p.fire('y', -1)
        elif keys[pygame.K_s]:
            p.fire('y', 1)
        elif keys[pygame.K_a]:
            p.fire('x', -1)
        elif keys[pygame.K_d]:
            p.fire('x', 1)

    p.updateProjectiles()
    e.updateEnemies()
    e.updateProjectiles()
    e.checkEnemyCollisions()
    i.checkItemCollisions()

    WINDOW.fill(COLOURS['BLACK'])
    for enemyData in e.currentEnemies:
        enemy = enemyData[0]
        pygame.draw.rect(WINDOW, enemyData[1], enemy)
        if enemyData[2] == 'shooter' and TIME - enemyData[3] > 500:
            e.fire(enemyData)
        if e.bossData['health'] > 0:
            e.healthBarBase = pygame.Rect(
                enemy.left - 16, enemy.bottom + 16, e.bossData['size'] + 32, 4)
            e.healthBar = pygame.Rect(
                enemy.left - 16, enemy.bottom + 16, e.bossData['health'] * ((e.bossData['size'] + 32) / e.bossData['healthMax']), 4)
            pygame.draw.rect(WINDOW, COLOURS['RED'], e.healthBarBase)
            pygame.draw.rect(WINDOW, COLOURS['GREEN'], e.healthBar)
            if TIME - e.bossData['lastFireTime'] > 500:
                e.fire(enemyData)

    for item in i.currentItems:
        if item['rolled'] == 200:
            item['rolled'] = random.randint(0, 100)
        if e.currentEnemies == []:
            if item['chance'] >= item['rolled'] or item['screen'] == s.currentScreen:
                item['screen'] = s.currentScreen
                pygame.draw.rect(
                    WINDOW, COLOURS[item['colour']], item['model'])

    for projectile in p.projectiles:
        pygame.draw.rect(WINDOW, p.projColour, projectile[0])
    for projectile in e.projectiles:
        pygame.draw.rect(WINDOW, e.projColour, projectile[0])

    s.drawBorders()
    s.drawScreenNo()
    s.drawScore()
    pygame.draw.rect(WINDOW, p.colour, p.model)
    pygame.draw.rect(WINDOW, COLOURS['RED'], p.healthBarBase)
    pygame.draw.rect(WINDOW, COLOURS['GREEN'], p.healthBar)
    p.checkHealth()
    pygame.display.update()

    FPSCLOCK.tick(FPS)
    TIME += FPSCLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
