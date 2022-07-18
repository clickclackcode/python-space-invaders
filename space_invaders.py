import pygame
from pygame.locals import *
import random

pygame.init()

# create the game screen
game_width = 500
game_height = 500
size = (game_width, game_height)
padding = 20
game_screen = pygame.display.set_mode(size)
pygame.display.set_caption('Space Invaders')

# colors
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# alien movement variables
alien_direction_x = 1
alien_direction_y = 0
count_direction_x_changes = 0

# player variables
player_speed = 8
player_lives = 5
missile_cooldown = 500

# frames per second
fps = 30
clock = pygame.time.Clock()

# helper function for displaying text on the screen
def write_text(str, color, x, y):
    text = font.render(str, True, color)
    text_rect = text.get_rect()
    text_rect.center = (x, y)
    game_screen.blit(text, text_rect)
    
# create the sprite groups
spaceship_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()
alien_missile_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()

class Spaceship(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # max and remaining lives
        self.lives = player_lives
        self.lives_left = player_lives
        
        # time the last missile was fired
        self.last_missile = pygame.time.get_ticks() - missile_cooldown
        
    def update(self):
        
        # draw health bar
        for life in range(self.lives):
            
            health_x = int(game_width / self.lives * life)
            health_y = game_height - padding
            
            if life < self.lives_left:
                pygame.draw.rect(game_screen, green, (health_x, health_y, int(game_width / self.lives), padding))
            else:
                pygame.draw.rect(game_screen, red, (health_x, health_y, int(game_width / self.lives), padding))
                
        write_text('Life', black, game_width / 2, game_height - padding / 2)
        
        key = pygame.key.get_pressed()
        
        # move left/right
        if key[K_LEFT] and self.rect.left > padding / 2:
            self.rect.x -= player_speed
        elif key[K_RIGHT] and self.rect.right < game_width - padding / 2:
            self.rect.x += player_speed
            
        # shoot missile
        if key[K_SPACE]:
            
            # wait some time before firing another missile
            current_time = pygame.time.get_ticks()
            if current_time - self.last_missile > missile_cooldown:
                
                missile = Missile(self.rect.centerx, self.rect.y)
                missile_group.add(missile)
                
                self.last_missile = current_time
                
class Alien(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image_filename):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
    def update(self):
        
        # move the alien
        self.rect.x += alien_direction_x
        self.rect.y += alien_direction_y
        
        # 1% chance that this alien will fire a missile
        alien_fire_probability = 1
        
        # don't fire another alien missile if there are already 3 on the screen
        max_alien_missiles = 3
        
        fire_chance = random.randint(0, 100)
        if fire_chance < alien_fire_probability and len(alien_missile_group.sprites()) < max_alien_missiles:
            alien_missile = AlienMissile(self.rect.centerx, self.rect.y)
            alien_missile_group.add(alien_missile)
            
class Missile(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x - 2, y, 4, 8)
        
    def update(self):
        
        # missile shoots up the screen
        self.rect.y -= 5
        
        # display the missile or remove it when it goes off screen
        if self.rect.bottom > 0:
            for w in range(self.rect.width):
                for h in range(self.rect.height):
                    game_screen.set_at((self.rect.x + w, self.rect.y - h), yellow)
        else:
            self.kill()
            
        # check for collision with alien
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            
class AlienMissile(Missile):
    
    def __init__(self, x, y):
        super().__init__(x, y)
        
    def update(self):
        
        # alien missile shoots down the screen
        self.rect.y += 5
        
        # display the missile or remove it when it goes off screen
        if self.rect.top <= game_height:
            for w in range(self.rect.width):
                for h in range(self.rect.height):
                    game_screen.set_at((self.rect.x + w, self.rect.y - h), red)
        else:
            self.kill()
            
        # check for collision with spaceship
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            self.kill()
            spaceship.lives_left -= 1
            
class Star(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x, y, 2, 2)
        
    def update(self):
        game_screen.set_at((self.rect.x, self.rect.y), white)
        
# create the stars for the background
for i in range(500):
    x = random.randint(0, game_width - 1)
    y = random.randint(0, game_height - 1)
    star = Star(x, y)
    star_group.add(star)
    
# create the spaceship
spaceship = Spaceship(int(game_width / 2), int(game_height - 2 * padding))
spaceship_group.add(spaceship)

# create the aliens
def create_aliens(alien_group):
    
    # alien images
    image_filenames = [
        'alien_red.png',
        'alien_purple.png',
        'alien_orange.png',
        'alien_green.png'
    ]
    
    alien_group.empty()
    
    # number of rows and columns of aliens
    rows_aliens = 4
    cols_aliens = 7
    
    for row in range(rows_aliens):
        for col in range(cols_aliens // 2 * -1, cols_aliens - cols_aliens // 2):
            x = game_width / 2 - 50 * col
            y = padding + row * 40
            alien = Alien(x, y, image_filenames[row])
            alien_group.add(alien)
create_aliens(alien_group)

# define the boundaries of the leftmost and rightmost aliens
aliens_left_bound = alien_group.sprites()[-1].rect.left
aliens_right_bound = alien_group.sprites()[0].rect.right

# game variables
game_status = 'new game'
ready_countdown = 0

font = pygame.font.Font(pygame.font.get_default_font(), 16)

# game loop
running = True
while running:
    
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
    # draw the background
    game_screen.fill(black)
    star_group.update()
    
    # draw the spaceship
    spaceship_group.draw(game_screen)
    
    # draw the aliens
    alien_group.draw(game_screen)
    
    # check if aliens need to change direction
    aliens_left_bound += alien_direction_x
    aliens_right_bound += alien_direction_x
    if aliens_left_bound <= padding or aliens_right_bound >= game_width - padding:
        alien_direction_x *= -1
        count_direction_x_changes += 1
        
    # after three x direction changes, move the aliens down
    if count_direction_x_changes < 3:
        alien_direction_y = 0
    else:
        alien_direction_y = 50
        count_direction_x_changes = 0
        
    # check if the left/right bounds need to be updated
    if len(alien_group.sprites()) > 0:
        aliens_left_bound = alien_group.sprites()[0].rect.left
        aliens_right_bound = alien_group.sprites()[-1].rect.right
    for alien in alien_group.sprites():
        if alien.rect.left < aliens_left_bound:
            aliens_left_bound = alien.rect.left
        if alien.rect.right > aliens_right_bound:
            aliens_right_bound = alien.rect.right
    
    if game_status == 'new game':
        
        # display start screen
        write_text('Space Invaders', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to Start', white, game_width / 2, game_height / 2 + 50)
        
        # change to 'playing' status when player presses SPACE
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'playing'
            ready_countdown = 3
            
    elif game_status == 'playing':
        
        # display the countdown
        if ready_countdown >= 0:
            
            write_text(str(ready_countdown), white, game_width / 2, game_height / 2)
            
            countdown_timer = pygame.time.get_ticks()
            pygame.time.delay(1000)
            ready_countdown -= 1
            pygame.display.update()
            
        else:
            
            # update the sprites
            spaceship_group.update()
            alien_group.update()
            missile_group.update()
            alien_missile_group.update()
            
        # check for game cleared or game over
        if len(alien_group.sprites()) == 0:
            game_status = 'cleared'
        elif spaceship.lives_left == 0:
            game_status = 'game over'
        for alien in alien_group.sprites():
            if alien.rect.bottom > spaceship.rect.top:
                game_status = 'game over'
                
    elif game_status == 'cleared':
        
        # display game cleared text
        write_text('Game Cleared', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to play again', white, game_width / 2, game_height / 2 + 50)
        
        # change to 'restart' status when player presses SPACE
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'restart'
            
    elif game_status == 'game over':
        
        # display game over text
        write_text('Game Over', white, game_width / 2, game_height / 2)
        write_text('Press SPACE to play again', white, game_width / 2, game_height / 2 + 50)
        
        # change to 'restart' status when player presses SPACE
        key = pygame.key.get_pressed()
        if key[K_SPACE]:
            game_status = 'restart'
            
    elif game_status == 'restart':
        
        # reset the aliens
        create_aliens(alien_group)
        alien_direction_x = 1
        alien_direction_y = 0
        count_direction_x_changes = 0
        aliens_left_bound = alien_group.sprites()[0].rect.left
        aliens_right_bound = alien_group.sprites()[-1].rect.right
        
        # reset the spaceship
        spaceship.rect.centerx = int(game_width / 2)
        spaceship.lives_left = spaceship.lives
        
        # reset the missiles
        missile_group.empty()
        alien_missile_group.empty()
        
        # reset the countdown timer for the next game
        ready_countdown = 3
        
        game_status = 'playing'
    
    pygame.display.update()
    
pygame.quit()