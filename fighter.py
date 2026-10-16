import pygame, random , sys 
from pygame.locals import *

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Global constants
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
LIGHTBLUE = (  0,   0, 155)
FPS = 60
NORMAL_SHOT_INTERVAL = 250
POWERUP_SHOT_INTERVAL = int(NORMAL_SHOT_INTERVAL / 1.5)
POWERUP_DURATION = 8000
POWERUP_SPAWN_INTERVAL = 12000

class Player(pygame.sprite.Sprite):

    # set speed vector of the player
    change_x = 0
    change_y = 0
    moverate = 5
    # Constructor. Pass in x and y position
    def __init__(self, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        # Create player image
        self.image = pygame.image.load('player.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image.set_colorkey(WHITE)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y

    def changespeed(self, x, y):
        """ Change the speed of the player"""
        self.change_x += x
        self.change_y += y

    def update(self):
        """ Move the player. """
        self.rect.move_ip(self.change_x, 0)
        self.rect.move_ip(0, self.change_y)

    def stop(self):
        """ Called when the user lets off the keyboard."""
        self.change_x = - self.change_x
        self.change_y = - self.change_y

class Enemy(pygame.sprite.Sprite):
    """ This class represents the enemy sprites. """
    minmoverate = 1
    maxmoverate = 8

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('enemyShip.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()

    def reset_pos(self):
        """ Reset position to the top of the screen, at a random x location. """
        self.rect.y = - ( SCREEN_HEIGHT / 4)
        self.rect.x = random.randrange(SCREEN_WIDTH)

    def update(self):
        """ Move the enemies. """
        self.rect.y += 2
        self.rect.x += 0
        if self.rect.y > SCREEN_HEIGHT:
            self.reset_pos()

class FireRatePowerUp(pygame.sprite.Sprite):
    """A collectible that temporarily increases the player's firing rate."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([24, 24])
        self.image.fill((255, 220, 0))
        # Blue center makes this collectible visually distinct.
        pygame.draw.rect(self.image, LIGHTBLUE, [8, 4, 8, 16])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

    def update(self):
        self.rect.y += 3
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([8, 20])
        self.image.fill(LIGHTBLUE)
        self.rect = self.image.get_rect()

    def update(self):
        """ Move the bullet. """
        self.rect.y -= 10
        if self.rect.y < - self.rect.height:
            self.kill()

class Game(object):
    """ This class represents an instance of the game. """

    enemy_list = None
    bullet_list = None
    all_sprites_list = None

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    screen_rect = screen.get_rect()

    def __init__(self):
        self.score = 0
        self.game_over = False
        self.moverate = 5
        self.shot = pygame.mixer.Sound("fire.ogg")
        self.next_shot_time = 0
        self.powerup_expires_at = 0
        self.next_powerup_time = pygame.time.get_ticks() + POWERUP_SPAWN_INTERVAL
        self.powerup_list = pygame.sprite.Group()

        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()

        for i in range(15):
            enemy = Enemy()
            enemy.rect.x = random.randrange(SCREEN_WIDTH)
            enemy.rect.y = random.randrange(-300, 20)
            self.enemy_list.add(enemy)
            self.all_sprites_list.add(enemy)

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT - (SCREEN_HEIGHT / 6))
        self.all_sprites_list.add(self.player)

    def fire_bullet(self):
        bullet = Bullet()
        bullet.rect.centerx = self.player.rect.centerx
        bullet.rect.y = self.player.rect.y
        self.all_sprites_list.add(bullet)
        self.bullet_list.add(bullet)
        self.shot.play()

    def process_events(self):
        """ Process all of the events. Return True if we need to close the window. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return True
                elif event.key == K_RETURN:
                    if self.game_over:
                        self.__init__()
                elif event.key in (K_RIGHT ,K_d):
                    self.player.changespeed(self.moverate, 0)
                elif event.key in (K_LEFT ,K_a):
                    self.player.changespeed(-self.moverate, 0)
                elif event.key in (K_UP , K_w):
                    self.player.changespeed(0, -self.moverate)
                elif event.key in (K_DOWN , K_s):
                    self.player.changespeed(0, self.moverate)

            elif event.type == KEYUP:
                if event.key in (K_RIGHT ,K_d):
                    self.player.changespeed(-self.moverate, 0)
                elif event.key in (K_LEFT ,K_a):
                    self.player.changespeed(self.moverate, 0)
                elif event.key in (K_UP , K_w):
                    self.player.changespeed(0, self.moverate)
                elif event.key in (K_DOWN , K_s):
                    self.player.changespeed(0, -self.moverate)
        return False

    def run_logic(self):
        """Update sprites, power-ups, firing and collisions."""
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        self.all_sprites_list.update()

        # Holding Space fires continuously; cooldown controls the rate.
        if pygame.key.get_pressed()[K_SPACE] and now >= self.next_shot_time:
            interval = NORMAL_SHOT_INTERVAL
            if now < self.powerup_expires_at:
                interval = POWERUP_SHOT_INTERVAL
            self.fire_bullet()
            self.next_shot_time = now + interval

        if now >= self.next_powerup_time:
            powerup = FireRatePowerUp()
            self.powerup_list.add(powerup)
            self.all_sprites_list.add(powerup)
            self.next_powerup_time = now + POWERUP_SPAWN_INTERVAL

        # Collecting a pickup grants the temporary 1.5x fire-rate boost.
        collected = pygame.sprite.spritecollide(self.player, self.powerup_list, True)
        if collected:
            self.powerup_expires_at = now + POWERUP_DURATION

        if len(self.all_sprites_list) < 17:
            enemy = Enemy()
            self.enemy_list.add(enemy)
            self.all_sprites_list.add(enemy)
            enemy.rect.x = random.randrange(SCREEN_WIDTH)
            enemy.rect.y = random.randrange(-100, -50)

        for bullet in self.bullet_list:
            hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, True)
            if hit_list:
                bullet.kill()
                self.score += len(hit_list)

        player_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_list, True)
        if player_hit_list:
            self.game_over = True

    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
        screen.fill(BLACK)

        if self.game_over:
            font = pygame.font.SysFont("serif", 25)
            text = font.render("Game Over! You scored " + str(self.score) +
                               " points, press Enter to restart", True, WHITE)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])

        if not self.game_over:
            self.player.rect.clamp_ip(self.screen_rect)
            self.all_sprites_list.draw(screen)
            if pygame.time.get_ticks() < self.powerup_expires_at:
                font = pygame.font.SysFont("serif", 18)
                status = font.render("Rapid fire!", True, (255, 220, 0))
                screen.blit(status, [10, 10])

        pygame.display.flip()

def main():
    """ Main program function. """
    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    screen_rect = screen.get_rect()
    pygame.display.set_caption("Fighter!")
    pygame.mouse.set_visible(False)

    done = False
    clock = pygame.time.Clock()
    game = Game()

    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
