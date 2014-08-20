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

        # Move left/right
        #if self.rect.x > 0 and (self.rect.x + 50) < SCREEN_WIDTH:
        self.rect.move_ip(self.change_x, 0)
       
        # Move up/down
        #if self.rect.y > 0 and (self.rect.y + 50) < SCREEN_HEIGHT:
        self.rect.move_ip(0, self.change_y)

        

    def stop(self):
        """ Called when the user lets off the keyboard."""
        self.change_x = - self.change_x
        self.change_y = - self.change_y
                
class Enemy(pygame.sprite.Sprite):
    """ This class represents the enemy sprites."""
    minmoverate = 1
    maxmoverate = 8

    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('enemyShip.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()

    def reset_pos(self):
        """ Reset position to the top of the screen, at a random x location.
        Called by update() or the main program loop if there is a collision."""

        self.rect.y = - ( SCREEN_HEIGHT / 4)
        self.rect.x = random.randrange(SCREEN_WIDTH)
        

    def update(self):
        """ Move the enemies. """
        # Move down, at some speed
        self.rect.y += 2
        # Move left and right, at some speed
        self.rect.x += 0

        # If enemy is too far down, reset to top of screen
        if self.rect.y > SCREEN_HEIGHT:
            self.reset_pos()
            


class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet. """
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([8, 20])
        self.image.fill(LIGHTBLUE)

        self.rect = self.image.get_rect()
        
    def update(self):
        """ Move the bullet. """
        self.rect.y -= 10
        # Remove the bullet if it flies up off the screen
        if self.rect.y < - self.rect.height:
            self.kill()
            

class Game(object):
    """ This class represents an instance of the game. If we need to
        rest the game we'd just need to create a new instance of this class."""

    # --- Class attributes.

    # Sprite lists
    enemy_list = None
    bullet_list = None
    all_sprites_list = None
    

    # Other data
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    screen_rect = screen.get_rect()
    
    # --- Class methods
    # Set up the game
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.moverate = 5

        # Create sprite lists
        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        
        # Create the starting enemy ships
        for i in range(15):
            enemy = Enemy()

            enemy.rect.x = random.randrange(SCREEN_WIDTH)
            enemy.rect.y = random.randrange(-300, 20)

            self.enemy_list.add(enemy)
            self.all_sprites_list.add(enemy)

        # Create the player
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT - (SCREEN_HEIGHT / 6))
        self.all_sprites_list.add(self.player)

        


    def process_events(self):
        """ Process all of the events. Return "True" if we need to close the window."""
        shot = pygame.mixer.Sound("fire.ogg")
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
                    self.player.changespeed( self.moverate ,0)
                elif event.key in (K_LEFT ,K_a):
                    self.player.changespeed( -self.moverate ,0)
                elif event.key in (K_UP , K_w):
                    self.player.changespeed(0, -self.moverate)
                elif event.key in (K_DOWN , K_s):
                    self.player.changespeed(0, self.moverate)
                elif event.key == K_SPACE: # Fire bullet
                    bullet = Bullet()
                    shot.play()
                    # Set bullet so it is where the player is
                    bullet.rect.centerx = self.player.rect.centerx 
                    bullet.rect.y = self.player.rect.y
                    
                    # Add bullet to lists
                    self.all_sprites_list.add(bullet)
                    self.bullet_list.add(bullet)

            elif event.type == KEYUP:
                if event.key in (K_RIGHT ,K_d):
                    self.player.changespeed( -self.moverate ,0)
                elif event.key in (K_LEFT ,K_a):
                    self.player.changespeed( self.moverate ,0)
                elif event.key in (K_UP , K_w):
                    self.player.changespeed(0, self.moverate)
                elif event.key in (K_DOWN , K_s):
                    self.player.changespeed(0, -self.moverate)
           
    def run_logic(self):
        """ This method is run each time through the frame.
            It updates positions and checks for collisions."""
        enemy = Enemy()
        if not self.game_over:
            # Move all the sprites
            self.all_sprites_list.update()

            if len(self.all_sprites_list) < 17:
                self.enemy_list.add(enemy)
                self.all_sprites_list.add(enemy)
                enemy.rect.x = random.randrange(SCREEN_WIDTH)
                enemy.rect.y = random.randrange(-100, -50)

            # Bullet Mechanics
            for bullet in self.bullet_list:
                # See if the bullets has collided with anything.
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, True)

                # For each enemy hit, remove bullet and enemy and add to score
                for enemy in self.enemy_hit_list:
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                    self.score += 1

            # Player Mechanics
            for enemy in self.enemy_list:
                # See if player has collided with anything.
                self.player_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_list, True)

                if len(self.player_hit_list) == 1:
                    # If player is hit, show game over.
                    self.game_over = True

    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
        screen.fill(BLACK)

        if self.game_over:
            # font = pygame.font.Font("Serif:, 25)
            font = pygame.font.SysFont("serif", 25)
            text = font.render("Game Over! You scored " + str(self.score) +" points, press Enter to restart", True, WHITE)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])

        if not self.game_over:
            self.player.rect.clamp_ip(self.screen_rect)
            self.all_sprites_list.draw(screen)
 
        pygame.display.flip()

def main():
    """ Main program function. """
    # Initialize Pygame and set up the window
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    screen_rect = screen.get_rect()
    pygame.display.set_caption("Fighter!")
    pygame.mouse.set_visible(False)
 
    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()
 
    # Create an instance of the Game class
    game = Game()
 
    # Main game loop
    while not done:
 
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
 
        # Update object positions, check for collisions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame(screen)
 
        # Pause for the next frame
        clock.tick(FPS)
 
    # Close window and exit
    pygame.quit()
 
# Call the main function, start up the game
if __name__ == "__main__":
    main()
