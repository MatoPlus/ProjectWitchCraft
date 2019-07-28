"""Author: Rixin Yang
   Date: May 1, 2018
   Description: Summative Bullet Hell - Alpha Build
"""

# I - IMPORT AND INITIALIZE
import pygame, sprites

#pre_init reduces sound delay
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()

def main():
    '''This function defines the 'mainline logic' for PROJECT: Witchcraft.'''
      
    # DISPLAY - set display resolution and caption.
    screen_size = (640, 480)
    screen = pygame.display.set_mode(screen_size)    
    pygame.display.set_icon(pygame.image.load("images/icon.png").convert_alpha())
    pygame.display.set_caption("PROJECT: Witchcraft - Test Room")
    
    game_loop(screen)
    
    # Unhide the mouse pointer - before closing window
    pygame.mouse.set_visible(True)    
    #Quit the game with delay to hear music fade
    pygame.mixer.music.fadeout(1000)
    pygame.time.delay(1000)
    pygame.quit()      
    

def game_loop(screen):
    '''This function defines the main game logic for the game PROJECT:
    Witchcraft.'''
    
    # ENTITIES - create background and gameover label.
    background = sprites.Background()
    
    # Create a list of Joystick objects.
    joysticks = []
    for joystick_no in range(pygame.joystick.get_count()):
        stick = pygame.joystick.Joystick(joystick_no)
        stick.init()
        joysticks.append(stick)  
        
    #Sound - loading and setting volume
    pygame.mixer.music.load("sounds/background.ogg")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
        
    #Player sprite creation, append them in a list.
    player = sprites.Player(screen)
    hitbox = sprites.Hitbox(player)
    
    # Sprites for: ScoreKeeper label
    score_tab = sprites.Score_tab(screen)
    
    #Enemy sprite test
    enemies = []
    #enemies.append(sprites.Enemy(screen))
    #enemies.append(sprites.Enemy(screen, 2))
    enemies.append(sprites.Enemy(screen, 3))
    #enemies.append(sprites.Enemy(screen, 4))
    
    #Cloud sprite
    clouds = []
    
    for cloud in range(4):
        clouds.append(sprites.Cloud(screen))
    
    #Sprite groups for better layering
    low_sprites = pygame.sprite.OrderedUpdates(background, clouds, player, hitbox)
    enemy_sprites = pygame.sprite.OrderedUpdates(enemies)
    player_bullet_sprites = pygame.sprite.OrderedUpdates()
    enemy_bullet_sprites = pygame.sprite.OrderedUpdates()
    bomb_sprites = pygame.sprite.OrderedUpdates()
    animation_sprites = pygame.sprite.OrderedUpdates()
    top_sprites = pygame.sprite.OrderedUpdates(score_tab)
    
    #All sprites groups up, layering with order
    all_sprites = pygame.sprite.OrderedUpdates(low_sprites, enemy_sprites, \
    player_bullet_sprites, enemy_bullet_sprites, animation_sprites, top_sprites)

    # ASSIGN - assign important variables to start game.
    clock = pygame.time.Clock()
    keepGoing = True
    half_mode = False
    FPS = 30
     
    # Hide the mouse pointer
    pygame.mouse.set_visible(False)
 
    # LOOP
    while keepGoing:
     
        # TIME
        clock.tick(FPS)
     
        # EVENT HANDLING: p1 use arrow keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

            #Get a list containing boolean values of pressed keys to their
            #position.
            keys_pressed = pygame.key.get_pressed()
            #Exit program on escape
            if keys_pressed[pygame.K_ESCAPE]:
                keepGoing = False
            #Movement.
            player.change_direction((0,0))
            if keys_pressed[pygame.K_LEFT]:
                player.change_direction((-1,0))
            if keys_pressed[pygame.K_RIGHT]:
                player.change_direction((1,0))
            if keys_pressed[pygame.K_UP]:
                player.change_direction((0,-1))
            if keys_pressed[pygame.K_DOWN]:
                player.change_direction((0,1))
            #Toggle shoot mode
            if keys_pressed[pygame.K_z]:
                player.shoot_mode(1)
            elif not keys_pressed[pygame.K_z]:
                player.shoot_mode(0)
            #Add bomb to sprite.
            if keys_pressed[pygame.K_x]:
                bomb_sprites.add(sprites.Bomb(player.get_center()))
            #Toggle focus mode.
            if keys_pressed[pygame.K_LSHIFT]:
                player.focus_mode(1)
                hitbox.set_visible(1)
            elif not keys_pressed[pygame.K_LSHIFT]:
                player.focus_mode(0)
                hitbox.set_visible(0)
        
        #Enemy bullet event. Hit detection
        for hit in pygame.sprite.spritecollide(
            hitbox, enemy_bullet_sprites.sprites(), False):
            #Shrink the hitbox rect to detect actual size of hitbox
            if hitbox.rect.inflate(-13,-13).colliderect(hit):
                #Player death
                animation_sprites.add(sprites.Explosion(
                    player.get_center(), 0))
                player.reset()
         
        #Enemy rect and shoot events.
        for enemy in enemy_sprites.sprites():  
            #See if enemy is hit by bullet. Return list of bullet that hit.
            for bullet in pygame.sprite.spritecollide(
                enemy, player_bullet_sprites.sprites(), False):
                #Bullet hits enemy. Animate, damage and kill bullet.
                animation_sprites.add(
                    sprites.Explosion(bullet.get_center(), 1))
                enemy.damaged(1)
                bullet.kill()
                #Kill enemy if appropriate.
                if enemy.get_hp() <= 0:
                    animation_sprites.add(sprites.Explosion(
                        enemy.get_center(), 0))
            #Let enemy shoot if appropriate.
            if not enemy.get_cool_rate() and not enemy.get_down_frames():
                enemy_bullet_sprites.add(enemy.spawn_bullet(player)) 
                
        #Enemy - player collision event      
        for enemy in pygame.sprite.spritecollide(
                        hitbox, enemy_sprites.sprites(), False):   
            #Shrink the hitbox rect to detect actual size of hitbox
            if hitbox.rect.inflate(-14,-14).colliderect(enemy):
                #Player death
                animation_sprites.add(sprites.Explosion(
                    player.get_center(), 0))
                player.reset()

        #Player bullet event. Let player shoot.
        if player.get_shoot() and not player.get_cool_rate():
            player_bullet_sprites.add(player.spawn_bullet())
        
        #Bomb detection event. See if it hits bullets. Reutnr list of bullets
        for bomb in bomb_sprites.sprites():
            for bullet in pygame.sprite.spritecollide(
                bomb, enemy_bullet_sprites.sprites(), False):
                #See if bomb is too small to detect collision with rim, 
                #use entire area to detect area of bomb.
                #If not to small, use approximate bomb rim area to detect hit 
                #by seeing if it doesn't collide with outside.
                if bomb.get_side() <= 140 or not bomb.rect.inflate(
                    -bomb.get_side()/4,-bomb.get_side()/4).colliderect(bullet):
                    #Animate and kill bullet.
                    animation_sprites.add(
                        sprites.Explosion(bullet.get_center(), 0))
                    bullet.kill()
                
        #Update what is in the all_sprites group.
        all_sprites = pygame.sprite.OrderedUpdates(low_sprites, enemy_sprites,
            player_bullet_sprites, enemy_bullet_sprites,
            animation_sprites, bomb_sprites, top_sprites)
                         
        # REFRESH SCREEN - clear previous sprites, update positions and display
        all_sprites.clear(screen, background.get_surface())
        all_sprites.update()
        all_sprites.draw(screen)       
        pygame.display.flip()   
     
# Call the main function
main()    