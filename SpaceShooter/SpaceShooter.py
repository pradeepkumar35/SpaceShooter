# PYGAME TEMPLATE - SKELETON FOR EVERY PYGAME PROJECT
import pygame
import time
import random
from pygame import mixer

pygame.font.init()

width = 800
height = 600
# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter")

# player Images

playerImg = pygame.transform.scale(pygame.image.load("SpaceShip.png"), (60,60))



# Images
enemy1Img = pygame.transform.scale(pygame.image.load("ENemy1.png"), (60,60))
enemy2Img = pygame.transform.scale(pygame.image.load("ENemy2.png"), (60,60))
enemy3Img = pygame.transform.scale(pygame.image.load("ENemy3.png"),(60,60))
laserBlue = pygame.image.load("laserGreen.png")
laserRed = pygame.image.load("laserRed.png")

# Bg
bg = pygame.image.load("BACKKGROUND.jpg")


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):

        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, HEIGHT ):
        return not (self.y <= HEIGHT and self.y >= -30)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    Cooldown = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = 100
        self.PlayerShip_img = None
        self.laser = None
        self.lasers = []
        self.cool_down_counter = 0
        self.height = -600

    def draw(self, window):
        window.blit(self.PlayerShip_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                obj.lives -= 1
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.Cooldown:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.PlayerShip_img.get_width()

    def get_height(self):
        return self.PlayerShip_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.PlayerShip_img = playerImg
        self.laser = laserBlue
        self.mask = pygame.mask.from_surface(self.PlayerShip_img)
        self.max_health = 100
        self.lives = 10
        self.font = pygame.font.SysFont("impact", 50)
        self.Font = pygame.font.SysFont("impact",30)
        self.lost = False
        self.lost_count = 0
        self.FPS = 30
        self.score_value = 0
    
    def score(self):
       self.score_value += 1
    
    def collsound(self):
       lcollisonsound = mixer.Sound("explosion.wav")
       lcollisonsound.play()

    def coll(self):
        self.lives -= 1
        self.health -= 10
        

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.score_value += 1
                        objs.remove(obj)
                        lcollisonsound = mixer.Sound("explosion.wav")
                        lcollisonsound.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(screen)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),[50,20,150,10])
        pygame.draw.rect(window,(0,255,100),(50,20,150*(self.health / self.max_health),10))
        self.lives_label = self.font.render("LIVES :" + str(self.lives), True, (255, 255, 200))
        self.score_label = self.Font.render("SCORE :" + str(self.score_value), 1, (255, 255, 200))
        screen.blit(self.score_label, (width - 130, 40))
        if self.lives <= 0:
            lost_label = self.font.render("GAME OVER !!", True, (255, 0, 0))
            screen.blit(lost_label, (width / 2 - lost_label.get_width() / 2, height / 2 - lost_label.get_height() / 2))
            self.lost = True
            self.lost_count += 1
            if self.lost:
                if self.lost_count >= self.FPS :
                    self.lives = 0
                    lcollisonsound = mixer.Sound("explosion.wav")
                    lcollisonsound.play()
                    main_menu()


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+24, self.y-15 , self.laser)
            self.lasers.append(laser)
            laserSound = mixer.Sound("laser.wav")
            laserSound.play()
            self.cool_down_counter = 1


class Enemy(Ship):
    Color_Map = {"red": (enemy1Img, laserRed),
                 "black": (enemy2Img, laserRed),
                 "yellow": (enemy3Img, laserRed)
                 }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.PlayerShip_img, self.laser = self.Color_Map[color]
        self.mask = pygame.mask.from_surface(self.PlayerShip_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0 and self.y >= 0:
            laser = Laser(self.x+24 , self.y+30, self.laser)
            laserSound = mixer.Sound("laser.wav")
            laserSound.play()
            self.lasers.append(laser)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Game loop
def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    lives = 5
    level = 0
    playerVel = 4
    laserVel = 4
    font = pygame.font.SysFont("impact", 30)
    lost_font = pygame.font.SysFont("impact", 50)
    player = Player(330, 480, font)
    enemies = []
    wave_length = 5
    enemyVel = 1

    def window():
        screen.blit(bg, (0, 0))
        lives_label = font.render("LIVES :" + str(lives), True, (255, 255, 200))
        level_label = font.render("LEVEL:" + str(level), True, (255, 255, 200))
        plaYerImg = pygame.transform.scale(pygame.image.load("SpaceShip.png"),(32,32))

        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
        screen.blit(plaYerImg, (10, 5))
        screen.blit(level_label, (width-100,5))


        if lost:
            lost_label = font.render("GAME OVER !!", True, (255, 0, 0))
            screen.blit(lost_label, (width / 2 - lost_label.get_width() / 2, height / 2 - lost_label.get_height() / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        window()
        if lives <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 200), random.randrange(-1500, -100),
                              random.choice(["red", "black", "yellow"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # returns all key in a dictionary
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - playerVel > 0:
            player.x -= playerVel
        if keys[pygame.K_d] and player.x + playerVel + player.get_width() < width:
            player.x += playerVel
        if keys[pygame.K_w] and player.y + 10 - playerVel > 0:
            player.y -= playerVel
        if keys[pygame.K_s] and player.y + playerVel + player.get_height() + 15 < height:
            player.y += playerVel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemyVel)
            enemy.move_lasers(laserVel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                Player.coll(player)
                Player.score(player)
                Player.collsound(player)
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > height:
                Player.coll(player)
                enemies.remove(enemy)

        player.move_lasers(-laserVel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("impact", 50)
    game_font = pygame.font.SysFont("impact",100)
    run = True
    while run:
        screen.blit(bg, (0, 0))
        game_label = title_font.render("SPACE SHOOTER", 1, (255, 255, 255))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        screen.blit(game_label, (width / 2 - game_label.get_width() / 2,250 ))
        screen.blit(title_label, (width / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mixer.music.load("GAMEMUSIC.mp3")
                mixer.music.play(-1)
                main()
    quit()



main_menu()

