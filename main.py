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
        self.projFireRate = 100  # How long the enemy['model'] must wait before firing again
        # This is a default and can differ between enemies
        self.lastFireTime = 0

        self.enemyStages = ['DEAD', COLOURS['RED'],
                            COLOURS['AQUA'], COLOURS['MAGENTA']]
        self.types = ['base', 'shooter']
        self.boss = {
            'health': 0
        }  # Initialise boss dictionary for use in createEnemies()
        self.bossesDefeated = 0
        self.bossJustCleared = 0

        self.enemyCounts = {}
        self.screenCleared = {}
        self.currentEnemies = []
        self.lastMovement = 0  # Time when the enemy['model'] last moved
        self.enemyUpdatePeriod = 50  # How long the enemy['model'] must wait before moving again

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
        # Spawn and end must have 0 enemy['model'] counts

    def createEnemies(self):
        self.vel = 4 + 0.33 * len(self.screenCleared)

        self.currentEnemies = []
        self.newEnemy = {}
        if s.currentScreen != 99:
            for count in range(0, self.enemyCounts[s.currentScreen]):
                self.newEnemy = {}
                self.newEnemy['model'] = pygame.Rect(s.createRandomCoordinates(WINDOW_WIDTH), s.createRandomCoordinates(
                    WINDOW_HEIGHT), self.modelWidth, self.modelHeight)
                if count % 3 == 0:  # Every third enemy['model'] is a 'shooter' type
                    self.type = 'shooter'
                else:
                    self.type = 'base'

                self.newEnemy['colour'] = self.colour
                self.newEnemy['type'] = self.type
                self.newEnemy['lastFireTime'] = self.lastFireTime
                self.newEnemy['canMove'] = True
                self.currentEnemies.append(self.newEnemy)

            if self.enemyCounts[s.currentScreen] == 0 and not s.currentScreen in self.screenCleared and s.currentScreen != 11:
                self.boss['health'] = random.randint(
                    25, 40) + (self.bossesDefeated + 1) * 0.5 + len(self.screenCleared)
                self.boss['healthMax'] = self.boss['health']
                self.boss['damage'] = len(self.screenCleared) * 4
                self.boss['size'] = random.randint(100, 200)
                self.boss['velocity'] = random.randint(
                    1, 4) + (len(self.screenCleared) / 10)
                self.boss['type'] = self.types[random.randint(
                    0, len(self.types) - 1)]
                self.boss['lastFireTime'] = 0

            if self.boss['health'] > 0:
                self.previousVel = self.vel
                self.vel = self.boss['velocity']
                self.type = self.boss['type']
                self.boss['model'] = pygame.Rect(
                    WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, self.boss['size'], self.boss['size'])
                self.boss['colour'] = COLOURS['RED']
                self.boss['canMove'] = True
                self.currentEnemies.append(self.boss)

    def updateEnemies(self):
        for enemy in self.currentEnemies:
            for projectile in p.projectiles:
                if projectile[0].colliderect(enemy['model']):
                    try:
                        if self.boss['health'] > 0:
                            self.boss['health'] -= 1
                            if self.boss['health'] <= 0:
                                self.vel = self.previousVel
                                p.health += 20
                                p.updateHealth()
                                self.currentEnemies.remove(enemy)
                                self.bossesDefeated += 1
                                self.bossJustCleared = True
                                p.score += 500
                        else:  # If not boss, goto updateHealth()
                            self.updateHealth(enemy)
                    except ValueError:
                        print(
                            '>>> Too many projectiles causing too many enemy kills! @ {}'.format(TIME))
                    p.projectiles.remove(projectile)

            if TIME - self.lastMovement > self.enemyUpdatePeriod:  # Move towards player
                for otherEnemy in self.currentEnemies:
                    if enemy['model'].colliderect(otherEnemy['model']) and enemy['model'] != otherEnemy['model']:
                        otherEnemy['canMove'] = False

                if enemy['canMove']:
                    if enemy['model'].centerx < p.model.centerx:
                        enemy['model'].centerx += self.vel
                    else:
                        enemy['model'].centerx -= self.vel
                    if enemy['model'].centery < p.model.centery:
                        enemy['model'].centery += self.vel
                    else:
                        enemy['model'].centery -= self.vel

            enemy['canMove'] = True

        if TIME - self.lastMovement > self.enemyUpdatePeriod:
            self.lastMovement = TIME

        if self.currentEnemies == []:
            self.enemyCounts[s.currentScreen] = 0
            self.screenCleared[s.currentScreen] = True

    def updateHealth(self, enemy):  # Called when an enemy is hit
        enemy['colour'] = self.enemyStages[self.enemyStages.index(
            enemy['colour']) - 1]  # Decrease enemy['model'] 'stage'
        if enemy['colour'] == 'DEAD':
            self.currentEnemies.remove(enemy)
            p.score += 50
        else:
            p.score += 5

    def checkEnemyCollisions(self):
        p.flashTime = TIME - p.invulnerabilityTime
        for enemy in self.currentEnemies:
            if TIME - p.invulnerabilityTime > 500:
                if enemy['model'].colliderect(p.model):
                    if self.boss['health'] > 0:
                        p.health -= self.boss['damage']
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

    def fire(self, enemy):
        enemy['lastFireTime'] = TIME
        if self.boss['health'] > 0:
            self.boss['lastFireTime'] = enemy['lastFireTime']
        dx = p.model.centerx - enemy['model'].centerx
        dy = p.model.centery - enemy['model'].centery

        self.newProjectile = pygame.Rect(enemy['model'].centerx, enemy['model'].centery, 3, 3)
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
            for item in self.items:
                if item['chance'] != 0 and s.currentScreen not in e.screenCleared or item['screen'] == s.currentScreen:
                    self.currentItems.append(item)
                    item['rolled'] = 200

    def checkItemCollisions(self):
        if e.currentEnemies == [] and s.currentScreen in e.screenCleared:
            for item in self.currentItems:
                if p.model.colliderect(item['model']) and (item['chance'] >= item['rolled'] or item['screen'] == s.currentScreen):
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
        return random.randint(limit / 10, limit - 8 * s.borderSize)


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
        return bool(e.boss['health'] > 0)

    def getBossAttributes(self):
        if e.boss['health'] > 0:
            return e.boss

    def getItemAttributes(self):
        self.returnString = ''
        for item in i.currentItems:
            if item['chance'] != 0 or item['screen'] == s.currentScreen:
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
pygame.display.set_caption('Yaka\'s Game!')

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

    if s.update:
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
    for enemy in e.currentEnemies:
        pygame.draw.rect(WINDOW, enemy['colour'], enemy['model'])
        if enemy['type'] == 'shooter' and TIME - enemy['lastFireTime'] > 500:
            e.fire(enemy)
        if e.boss['health'] > 0:
            e.healthBarBase = pygame.Rect(
                enemy['model'].left - 16, enemy['model'].bottom + 16, e.boss['size'] + 32, 4)
            e.healthBar = pygame.Rect(
                enemy['model'].left - 16, enemy['model'].bottom + 16, e.boss['health'] * ((e.boss['size'] + 32) / e.boss['healthMax']), 4)
            pygame.draw.rect(WINDOW, COLOURS['RED'], e.healthBarBase)
            pygame.draw.rect(WINDOW, COLOURS['GREEN'], e.healthBar)
            if TIME - e.boss['lastFireTime'] > 500:
                e.fire(enemy)

    for item in i.currentItems:
        if item['rolled'] == 200:
            item['rolled'] = random.randint(0, 100)
        if e.currentEnemies == []:
            if e.bossJustCleared:
                item['chance'] *= 2
            if item['chance'] >= item['rolled'] or item['screen'] == s.currentScreen:
                item['screen'] = s.currentScreen
                item['chance'] = 0
                pygame.draw.rect(
                    WINDOW, COLOURS[item['colour']], item['model'])
            if e.bossJustCleared:
                item['chance'] /= 2
    e.bossJustCleared = False

    for projectile in p.projectiles:
        pygame.draw.rect(WINDOW, p.projColour, projectile[0])
    for projectile in e.projectiles:
        pygame.draw.rect(WINDOW, e.projColour, projectile[0])

    s.drawBorders()
    pygame.draw.rect(WINDOW, p.colour, p.model)
    s.drawScreenNo()
    s.drawScore()
    pygame.draw.rect(WINDOW, COLOURS['RED'], p.healthBarBase)
    pygame.draw.rect(WINDOW, COLOURS['GREEN'], p.healthBar)
    p.checkHealth()
    pygame.display.update()

    FPSCLOCK.tick(FPS)
    TIME += FPSCLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
