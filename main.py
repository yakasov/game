import pygame, random, time
from dictResolver import *
pygame.init()

COLOURS = loadDictionaries('colours')

class player():
    def __init__(self):
        self.modelWidth = 15
        self.modelHeight = 15
        self.model = pygame.Rect(25, 40, self.modelWidth, self.modelHeight)
        self.colour = COLOURS['WHITE']
        self.vel = 5

        self.projectiles = []
        self.projVel = 8
        self.projColour = COLOURS['WHITE']
        self.projFireRate = 100
        self.lastFireTime = 0

        self.health = 100
        self.healthMax = 100
        self.healthBarBase = pygame.Rect(0, WINDOW_HEIGHT, WINDOW_WIDTH, 50)
        self.healthBar = pygame.Rect(0, WINDOW_HEIGHT, self.health * (WINDOW_WIDTH / self.healthMax), 50)
        self.invulnerabilityTime = 0
        self.flashTime = 0

    def updateHealth(self):
        self.healthBar = pygame.Rect(0, WINDOW_HEIGHT, self.health * (WINDOW_WIDTH / self.healthMax), 50)

    def checkHealth(self):
        if self.health > self.healthMax:
            self.health = self.healthMax

        if self.health <= 0:
            for i in range(52):
                x = 0 + i * 5
                WINDOW.fill((x, x, x))
                pygame.display.update()
                time.sleep(0.0512)
            gameOverText = LARGE_FONT.render('Game Over', True, COLOURS['BLACK'], COLOURS['WHITE'])
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

        self.newProjectile = pygame.Rect(self.model.centerx + xModifier, self.model.centery + yModifier, 3, 3)
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
        self.projFireRate = 100
        self.lastFireTime = 0

        self.enemyStages = ['DEAD', COLOURS['RED'], COLOURS['AQUA'], COLOURS['MAGENTA']]
        self.screenCleared = {}
        self.currentEnemies = []
        self.currentBosses = []
        self.lastMovement = 0
        self.enemyUpdatePeriod = 50

    def createEnemies(self):
        self.vel = 4 + 0.5 * len(self.screenCleared)

        self.currentEnemies = []
        try:
            for count in range(0, self.enemyCounts[s.currentScreen]):
                self.enemy = pygame.Rect(s.createRandomCoordinates(WINDOW_WIDTH), s.createRandomCoordinates(WINDOW_HEIGHT), self.modelWidth, self.modelHeight)
                if count % 3 == 0:
                    self.type = 'shooter'
                else:
                    self.type = 'base'
                self.currentEnemies.append([self.enemy, self.colour, self.type, self.lastFireTime])
        except KeyError:
            print('>>> No enemies available for screen {}! @ {}'.format(s.currentScreen, TIME))

        if s.currentScreen in self.bosses and self.bosses[s.currentScreen]['health'] > 0:
            self.previousVel = self.vel
            self.bossData = self.bosses[s.currentScreen]
            self.vel = self.bossData['velocity']
            self.boss = pygame.Rect(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, self.bossData['size'], self.bossData['size'])
            self.currentEnemies.append([self.boss, COLOURS['RED']])
            self.currentBosses.append([self.boss, COLOURS['RED']])

    def updateEnemies(self):
        for enemyData in self.currentEnemies:
            enemy = enemyData[0]
            for projectile in p.projectiles:
                if projectile[0].colliderect(enemy):
                    try:
                        if enemyData in self.currentBosses:
                            self.bossData['health'] -= 1
                            if self.bossData['health'] <= 0:
                                self.vel = self.previousVel
                                p.health += 20
                                p.updateHealth()
                                self.currentBosses.remove(enemyData)
                                self.currentEnemies.remove(enemyData)
                        else:
                            self.updateHealth(enemyData)
                    except ValueError:
                        print('>>> Too many projectiles causing too many enemy kills! @ {}'.format(TIME))
                    p.projectiles.remove(projectile)

            if TIME - self.lastMovement > self.enemyUpdatePeriod:
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

    def updateHealth(self, enemyData):
        enemyData[1] = self.enemyStages[self.enemyStages.index(enemyData[1]) - 1]
        if enemyData[1] == 'DEAD':
            self.currentEnemies.remove(enemyData)

    def checkEnemyCollisions(self):
        p.flashTime = TIME - p.invulnerabilityTime
        for enemyData in self.currentEnemies:
            enemy = enemyData[0]
            if TIME - p.invulnerabilityTime > 500:
                if enemy.colliderect(p.model):
                    if enemyData in self.currentBosses:
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

    def fire(self, enemyData): ### <--- every x seconds, fire projectile
        enemy = enemyData[0]
        self.lastFireTime = TIME
        dx = p.model.centerx - enemy.centerx
        dy = p.model.centery - enemy.centery
        grad = dy / dx

        self.newProjectile = pygame.Rect(enemy.centerx, enemy.centery, 3, 3)
        self.projectiles.append([self.newProjectile, grad])

    def updateProjectiles(self):
        for projectile in self.projectiles:
            projectile[0].centerx += (1 / projectile[1]) * self.projVel
            projectile[0].centery == projectile[1] * self.projVel

            if projectile[0].centerx > WINDOW_WIDTH or projectile[0].centerx < 0:
                self.projectiles.remove(projectile)
            if projectile[0].centery > WINDOW_HEIGHT or projectile[0].centery < 0:
                self.projectiles.remove(projectile)


class items():
    def checkCurrentScreenItems(self):
        self.currentItems = []
        try:
            for item in self.items[0]:
                self.currentItems.append(item)
                item['rolled'] = 200
        except KeyError:
            print('>>> No items found with all screen spawns! @ {}'.format(TIME))
            pass
        try:
            for item in self.items[s.currentScreen]:
                self.currentItems.append(item)
                item['rolled'] = 200
        except KeyError:
            print('>>> No items found for screen {}! @ {}'.format(s.currentScreen, TIME))

    def checkItemCollisions(self):
        for item in self.currentItems:
            if p.model.colliderect(item['model']):
                if 'PLAYER_VELOCITY' in item['attributes']: ## Default 5
                    p.vel += item['magnitude']
                if 'PLAYER_HEALTH' in item['attributes']: ## Default 100
                    p.healthMax += item['magnitude']
                    p.health += item['magnitude']
                if 'PROJECTILE_VELOCITY' in item['attributes']: ## Default 8
                    p.projVel += item['magnitude'] * 2
                if 'PROJECTILE_RATE' in item['attributes']: ## Default 100
                    p.projFireRate -= item['magnitude'] * 5
                self.currentItems.remove(item)
                item['chance'] = 0


class screens():
    def __init__(self):
        self.currentScreen = 11
        self.update = True

        self.borderColour = (51, 51, 51)
        self.borderSize = 10
        self.topBar = pygame.Rect(0, 0, WINDOW_WIDTH, self.borderSize)
        self.bottomBar = pygame.Rect(0, WINDOW_HEIGHT - self.borderSize, WINDOW_WIDTH, self.borderSize)
        self.rightBar = pygame.Rect(WINDOW_WIDTH - self.borderSize, 0, self.borderSize, WINDOW_HEIGHT)
        self.leftBar = pygame.Rect(0, 0, self.borderSize, WINDOW_HEIGHT)
        self.lettersToBorders = {'T': self.topBar,
                                 'B': self.bottomBar,
                                 'L': self.leftBar,
                                 'R': self.rightBar
                                 }

    def screenUpdate(self):
        if s.currentScreen % 10 > 3:
            e.colour = COLOURS['AQUA']

        i.checkCurrentScreenItems()
        e.createEnemies()
        d.printInfo()

    def drawBorders(self):
        self.bordersToDraw = []
        if e.currentEnemies == []:
            if self.currentScreen in self.borderOverrides and self.bordersToDraw == []:
                for letter in self.borderOverrides[self.currentScreen]:
                    try:
                        self.bordersToDraw.append(self.lettersToBorders[letter])
                    except KeyError:
                        print('>>> Incorrect borders found for screen border override! @ {}'.format(TIME))
                        pass
            else:
                if self.currentScreen + 10 in e.enemyCounts:
                    self.bordersToDraw.append(self.rightBar)
                if self.currentScreen - 10 in e.enemyCounts:
                    self.bordersToDraw.append(self.leftBar)
                if self.currentScreen + 1 in e.enemyCounts:
                    self.bordersToDraw.append(self.topBar)
                if self.currentScreen -1 in e.enemyCounts:
                    self.bordersToDraw.append(self.bottomBar)
            for bar in self.bordersToDraw:
                pygame.draw.rect(WINDOW, self.borderColour, bar)
                self.checkBorderCollisions(bar)

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
        if s.currentScreen in e.bosses:
            return True
        else:
            return False

    def getBossAttributes(self):
        if s.currentScreen in e.bosses:
            return e.bosses[s.currentScreen]
        else:
            return 'None'

    def getItemAttributes(self):
        self.returnString = ''
        for item in i.currentItems:
            if item['chance'] != 0 or item['screen'] == s.currentScreen:
                self.returnString += '\n  {}'.format(item)
        return self.returnString


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

## Load dictionaries from the 'resources' folder.
e.bosses = loadDictionaries('bosses')
e.enemyCounts = loadDictionaries('enemyCounts')
i.items = loadDictionaries('items')
s.borderOverrides = loadDictionaries('borderOverrides')

while True:
    pygame.time.delay(round(1000 / FPS))

    if s.update == True:
        s.screenUpdate()
        s.update = False

    keys = pygame.key.get_pressed()

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
    e.checkEnemyCollisions()
    i.checkItemCollisions()

    WINDOW.fill(COLOURS['BLACK'])
    for enemyData in e.currentEnemies:
        pygame.draw.rect(WINDOW, enemyData[1], enemyData[0])
        print(enemyData)
        if enemyData[2] == 'shooter' and TIME - enemyData[3] > 200:
            e.fire(enemyData)
    for item in i.currentItems:
        if item['rolled'] == 200:
            item['rolled'] = random.randint(0, 100)
        if e.currentEnemies == []:
            if (item['chance'] >= item['rolled'] and item['screen'] == 0) or item['screen'] == s.currentScreen:
                item['screen'] = s.currentScreen
                pygame.draw.rect(WINDOW, COLOURS[item['colour']], item['model'])

    for projectile in p.projectiles:
        pygame.draw.rect(WINDOW, p.projColour, projectile[0])
    for projectile in e.projectiles:
        pygame.draw.rect(WINDOW, e.projColour, projectile[0])
    s.drawBorders()
    pygame.draw.rect(WINDOW, p.colour, p.model)
    pygame.draw.rect(WINDOW, COLOURS['RED'], p.healthBarBase)
    pygame.draw.rect(WINDOW, (57, 255, 14), p.healthBar)
    p.checkHealth()
    pygame.display.update()

    FPSCLOCK.tick(FPS)
    TIME += FPSCLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
