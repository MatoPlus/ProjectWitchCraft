"""Author: Rixin Yang
   Date: May 1, 2018
   Description: Creates a module used for the game "PROJECT: Witchcraft" using 
   many sprite classes.
"""

#Import needed module
import pygame, math, random

class Player(pygame.sprite.Sprite):
    '''The player class sprite. This class sprite is the player model being 
    controlled by the user.'''
 
    def __init__(self, screen):
        '''This method initializes the sprite using the screen parameter to 
        set boundaries in update.'''
 
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        #Set up and load images for animation frames while idle
        self.__frames = []
        for index in range(5):
            self.__frames.append(pygame.image.load("images/station"
                                        +str(index)+".png").convert_alpha())
            
        #Set other instances needed for this class.
        self.image = self.__frames[0] 
        self.rect = self.image.get_rect()
        self.rect.center = ((screen.get_width()-200)/2, 
                            screen.get_height()- 2*self.rect.height)
        self.__index = 0 #For animation image
        self.__frame_refresh = 2 #For animation refresh
        self.__temp_frame_refresh = self.__frame_refresh   
        self.__screen = screen
        self.__dx = 0
        self.__dy = 0
        self.__diagonal = 1
        self.__focus = 1
        self.__invincible = 0
        self.__shoot = 0
        self.__cool_rate = 4
        self.__focus_cool_rate = 6
        self.__temp_cool_rate = 4
      
    def change_direction(self, xy_change):
        '''This method takes a xy tuple to change the direction.'''
        
        #Multiply appropriate vectors by a magnitude of 10
        if xy_change[0] != 0:
            self.__dx = xy_change[0]*8
        elif xy_change[1] != 0:
            self.__dy = xy_change[1]*8
        #No vectors if idle
        else:
            self.__dx = 0
            self.__dy = 0
        
        #Toggle/untoggle diagonal mode when depending on if both value = 1.
        if self.__dx != 0 and self.__dy != 0:
            self.diagonal_mode(1)
        else:
            self.diagonal_mode(0)
        
    def diagonal_mode(self, mode):
        '''This method toggle/untoggles the diagonal mode depending on the 
        mode parameter (boolean). This is used to ensure consistency
        amongst movement.'''
        
        #change factor used in update to approximately 0.7071.
        if mode:
            self.__diagonal = ((2.0**0.5)/2.0)
        else:
            self.__diagonal = 1
            
    def focus_mode(self, mode):
        '''This method toggles/untoggles the focused mode depending on the mode
        parameter (boolean). This is used to toggle between different speeds and
        fire types.'''
        
        #Change focus factor to the correct value depending on mode. 
        if mode:
            self.__focus = 1.75
        else:
            self.__focus = 1
    
    def shoot_mode(self, mode):
        '''This method toggles/untoggles the shoot mode depending on the mode
        parameter (boolean). This is used to toggle constant firing and non-
        firing.'''        
        
        #Change boolean value
        self.__shoot = mode

    def spawn_bullet(self):
        '''This method spawns bullets, used in main. This spawns different 
        bullets with different pattern depending on focus type.'''
        
        #If focused, shoot stream of bullet, and reset the cool down with 
        #appropriate cool rate.
        if not self.__focus == 1:
            self.__temp_cool_rate = self.__cool_rate
            return Bullet(self.__screen, self, 0)
        #Unfocused shoots muti-bullets. Resetting with appropriate cool rate.
        else:
            self.__temp_cool_rate = self.__focus_cool_rate
            return [Bullet(self.__screen, self, 1, 60),
                    Bullet(self.__screen, self, 1, 80),
                    Bullet(self.__screen, self, 1, 100),
                    Bullet(self.__screen, self, 1, 120)]
        
    def reset(self):
        '''This method resets the player to original spawn point.'''
        
        self.rect.center = ((self.__screen.get_width()-200)/2,
                            self.__screen.get_height()- 2*self.rect.height)    
        
    def get_cool_rate(self):
        '''This method returns the self instance, cool rate. Used in main to 
        see if player can fire.'''
        
        #Return instance value.
        return self.__temp_cool_rate
        
    def get_shoot(self):
        '''This method returns the self instance, shoot mode. Used in main to 
        see if player can fire.'''        
        
        #Return instance.
        return self.__shoot
    
    def get_center(self):
        '''This method returns the self instance, center. Used in respawn and 
        positioning.'''           
        
        #Return instance.
        return self.rect.center
        
    def update(self):
        '''Update method used to update animation frames, cooldowns, and 
        movement.'''
        
        #Update sprite animation frames
        if self.__temp_frame_refresh > 0:
            self.__temp_frame_refresh -= 1
        else:
            self.__temp_frame_refresh = self.__frame_refresh
            self.__index += 1
            self.image = self.__frames[self.__index % len(self.__frames)]
            
        #Update sprite position using boundaries.
        #Horizontal position.
        if ((self.rect.left > 0) and (self.__dx < 0)) or\
           ((self.rect.right < self.__screen.get_width()-200) and\
            (self.__dx > 0)):
            self.rect.centerx += self.__dx/self.__focus*self.__diagonal
        #Vertical position
        if ((self.rect.top > 0) and (self.__dy < 0)) or\
                  ((self.rect.bottom < self.__screen.get_height()) and\
                   (self.__dy > 0)):
            self.rect.centery += self.__dy/self.__focus*self.__diagonal
            
        #Cool down control.
        if self.__temp_cool_rate > 0 :
            self.__temp_cool_rate -= 1
        
class Hitbox(pygame.sprite.Sprite):
    '''The sprite for the player hit box sprite. Used in bullet detection.'''
    
    def __init__(self, player):
        '''This method initializes the sprite using the player sprite.'''
            
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        #Image loading
        self.__hitbox = pygame.image.load("images/hitbox.png")\
            .convert_alpha()
        self.__temp = pygame.image.load("images/temp.png").convert_alpha()
        
        #Instance value setting.
        self.image = self.__hitbox
        self.rect = self.image.get_rect()
        self.__player = player
    
    def position(self, player):
        '''This method uses the player sprite instance to reposition itself.'''
        
        self.rect.center = player.rect.center
        
    def set_visible(self, visible):
        '''This method uses the visible parameter (boolean), to set image from
        visible to invisible.'''
        
        if visible:
            self.image = self.__hitbox
        else:
            self.image = self.__temp

    def update(self):
        '''This sprite updates the position of the hitbox sprite. using a
        method.'''

        self.position(self.__player)
        
class Bomb(pygame.sprite.Sprite):
    '''This class creates a player bomb sprite. Used to detect and kill bullets
    upon detection.'''
    
    def __init__(self, xy_position):
        '''This method initializes the class using the xy parameter 
        (tuple position) to start bomb at a point.'''
        
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)        
        
        #Set instance values.
        self.__side = 20
        self.image = pygame.Surface((self.__side,self.__side))
        self.rect = self.image.get_rect()
        self.__start = xy_position
        self.rect.center = xy_position
        self.__finish_raidus = 700
        self.__expand = 30
        self.__width = 3
        
    def get_side(self):
        '''This method returns the instance side. Used in accurate rect 
        detection in main.'''
        
        #Return instance.
        return self.__side

    def update(self):
        ''''This method updates the bomb by increasing the size, the width of 
        the circle drawn and to seemingly animate the bomb to expand off the 
        screen.'''
        
        #If not finished expanding, continue.
        if self.__side/2 < self.__finish_raidus:
            self.__side += self.__expand
            self.__width += 1
            
            #Create new surface with the new size
            self.image = pygame.Surface((self.__side,self.__side))
            
            #Make background invisible
            self.image.set_colorkey((0,0,0))
            
            #Draw circle in surface.
            pygame.draw.circle(self.image, (255,255,255), (self.__side/2
                                , self.__side/2), self.__side/2, self.__width)
            
            #Reset rect for proper collision.
            self.rect = self.image.get_rect()
            self.rect.center = self.__start
            
        #If done, kill bomb.
        else:
            self.kill()
              
class Enemy(pygame.sprite.Sprite):
    '''The Enemy sprite class that shoots bullets at player with different 
    patterns depending on the enemy type.'''
    
    def __init__(self, screen, enemy_type = 1):
        '''This method initializes the enemy sprite with correct properties 
        according to enemy type parameter. The screen parameter is used in for
        boundaries in update.'''
    
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        #Set up and load animation frames.
        self.__frames = []
        for index in range(4):
            self.__frames.append(pygame.image.load("images/fairy"
                        +str(enemy_type)+"_"+str(index)+".png").convert_alpha())
        self.image = self.__frames[0]
        
        #Setting default properites
        self.__down_frames = 0
        self.__active_frames = 0
        self.__cool_rate = 0
        self.__dx = 0
        self.__dy = 0
        self.__hp = 0
        self.__degs_change = 0     
        self.rect = self.image.get_rect()
        self.rect.center = (400-50*enemy_type, 340-50*enemy_type)
        self.__screen = screen        
        self.__target_degs = None
        self.__enemy_type = enemy_type
        self.__index = 0
        self.__frame_refresh = 2
        self.__images = 4        
        
        #Setting special enemy instance values depending on enemy type.
        if enemy_type == 1:
            self.__down_frames = 60
            self.__active_frames = 120
            self.__cool_rate = 15
            self.__hp = 20
        elif enemy_type == 2:
            self.__down_frames = 30
            self.__active_frames = 60
            self.__cool_rate = 10
            self.__hp = 25  
        elif enemy_type == 3:
            self.__down_frames = 0
            self.__active_frames = 12
            self.__cool_rate = 4
            self.__hp = 40
            self.__degs_change = 6
        elif enemy_type == 4:
            self.__down_frames = 60
            self.__active_frames = 25
            self.__cool_rate = 5
            self.__hp = 5   
        
        #Set temps used in countdowns.
        self.__temp_down_frames = self.__down_frames
        self.__temp_frame_refresh = self.__frame_refresh
        self.__temp_active_frames = self.__active_frames
        self.__temp_cool_rate = self.__cool_rate
        
    def spawn_bullet(self, target):
        '''This method accepts a target parameter (a sprite) and use it to 
        spawn/return bullets. The pattern will vary depending on the enemy 
        types.'''
        
        #Get the temp slopes values.
        temp_dx = float(target.rect.centerx - self.rect.centerx)
        temp_dy = float(target.rect.centery - self.rect.centery)
        #Get radians from slope values.
        rads = math.atan2(-temp_dy, temp_dx)
        rads %= math.pi*2
        #Convert radians to degrees for easy pattern mannipulation.
        degs = math.degrees(rads)  
        
        #Type 1, fire 1 bullet that tracks in the direction of the target 
        #with little variation.
        if self.__enemy_type == 1:
            self.__target_degs = degs
            vary = random.randrange(-2, 12, 2)
            self.__target_degs += vary
            self.__temp_cool_rate = self.__cool_rate
            return Bullet(self.__screen, self, self.__enemy_type+1,
                          self.__target_degs) 
        
        #Type 2, fire three bullets in a triple spread pattern towards target 
        #with little variation.
        elif self.__enemy_type == 2:
            if self.__target_degs == None:
                self.__target_degs = degs
                vary = random.randrange(-2, 12, 2)
                self.__target_degs += vary                 
            self.__temp_cool_rate = self.__cool_rate              
            return [Bullet(self.__screen, self, self.__enemy_type+1, 
                           self.__target_degs), 
                    Bullet(self.__screen, self, 
                           self.__enemy_type+1, self.__target_degs-25),
                    Bullet(self.__screen, self, self.__enemy_type+1,
                           self.__target_degs+25)]
        
        #Type 3, Fire four bullets in a 90 degree gap each. The degree of 
        #direction will change and rotate as frames pass by.
        elif self.__enemy_type == 3:
            if self.__target_degs == None:
                self.__target_degs = 0
            factor = random.randrange(1,4)
            if self.__target_degs < 0 and self.__degs_change < 0:
                self.__degs_change = 9 * factor
            elif self.__target_degs > 180 and self.__degs_change > 0:
                self.__degs_change = -9 * factor
            self.__target_degs += self.__degs_change
            self.__temp_cool_rate = self.__cool_rate              
            return [Bullet(self.__screen, self, self.__enemy_type+1,
                           self.__target_degs),
                   Bullet(self.__screen, self, self.__enemy_type+1,
                          self.__target_degs+90),
                   Bullet(self.__screen, self, self.__enemy_type+1,
                          self.__target_degs+180),
                   Bullet(self.__screen, self, self.__enemy_type+1,
                          self.__target_degs+270)]
        
        #Last type, fire at target will a lot of variation in direction.
        else:
            self.__target_degs = degs
            vary = random.randrange(-16, 30, 2)
            self.__target_degs += vary                 
            self.__temp_cool_rate = self.__cool_rate              
            return Bullet(self.__screen, self, self.__enemy_type+1, 
                           self.__target_degs)     
        
    def damaged(self, damage):
        '''This method takes a damage paramter (integer). The damage paramter
        is used to decrease enemy/class health.'''
        
        #Mutate hp instance.
        self.__hp -= damage        
            
    def get_cool_rate(self):
        '''This method returns the cool rate of the enemy. Used in main to see 
        when enemy can fire.'''
        
        #Return instance.
        return self.__temp_cool_rate
    
    def get_down_frames(self):
        '''This method returns the down frames of the enemy. Used to see when 
        the enemy can fire in main.'''
        
        #Return instance
        return self.__temp_down_frames
        
    def get_hp(self):
        '''This method returns the hp of the enemy. Used to see when 
        the enemy can be deleted in main.'''        
        
        #Return instance.
        return self.__hp
    
    def get_center(self):
        '''This method returns the down frames of the enemy. Used to position 
        sprites.'''        
        
        #Return instance.
        return self.rect.center
    
    def update(self):
        '''This method updates what happens to the enemy class as frames passes 
        by. This method kills, moves, animates, and controls cool down of 
        enemy class.'''
        
        #Decide to kill if enemy dies.
        if self.__hp <= 0 or self.rect.top > self.__screen.get_height():
            self.kill()
        
        #Animate frames, refresh counter
        if self.__temp_frame_refresh > 0:
            self.__temp_frame_refresh -= 1
        else:
            self.__temp_frame_refresh = self.__frame_refresh
            self.__index += 1
        self.image = self.__frames[self.__index % self.__images]
        
        #Tick cool rate if appropriate.
        if self.__temp_cool_rate > 0:
            self.__temp_cool_rate -= 1
        
        #Reset down frames and active frames to original.
        if self.__temp_active_frames == 0 == self.__temp_down_frames:
            self.__temp_down_frames = self.__down_frames
            self.__temp_active_frames = self.__active_frames
            #Set target degrees to none as appropriate to type 2 pattern
            if self.__enemy_type == 2:
                self.__target_degs = None
        
        #Tick down frames and active frames if appropriate.
        if self.__temp_down_frames > 0:
            self.__temp_down_frames -= 1
        if self.__temp_active_frames > 0 and self.__temp_down_frames == 0:
            self.__temp_active_frames -= 1
    
        #Change x vector when colliding with boundary for opposite direction.
        if self.rect.left <= 0 and self.__dx < 0:
            self.__dx = abs(self.__dx)
        elif self.rect.right >= self.__screen.get_width()-200 and self.__dx > 0:
            self.__dx = -self.__dx
            
        #move class/sprite according to vectors.
        self.rect.centerx += self.__dx
        self.rect.centery += self.__dy
            
class Explosion(pygame.sprite.Sprite):
    '''This class creates a Explosion animation depending on type.'''
    
    def __init__(self, xy_position, explosion_type):
        '''This method initializes the class by using paramters starting 
        position and type. The starting position is used as spawn point and
        explosion type is used to load appropriate image.
        '''
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)    
        
        #Set up and load frames depending on type
        self.__frames = []
        if explosion_type == 0:
            for num in range(4):
                self.__frames.append(pygame.image.load("images/death"
                                            +str(num)+".png").convert_alpha())
        elif explosion_type == 1:
            for num in range(3):
                self.__frames.append(pygame.image.load("images/burst"
                                            +str(num)+".png").convert_alpha())
                
        #Set up instances.
        self.image = self.__frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = xy_position
        self.__frame_refresh = 1 
        self.__temp_refresh = self.__frame_refresh
        self.__index = 0
    
    def update(self):
        '''Update class as frames passes by. Control frame refresh, new frame
        and kill.'''
        
        #Frame tick
        if self.__temp_refresh > 0:
            self.__temp_refresh -= 1
            
        #Kill after animation
        else:
            if self.__index >= len(self.__frames)-1:
                self.kill()
            #Next frame if appropriate
            else:
                self.__index += 1
                self.image = self.__frames[self.__index]
            self.__temp_refresh = self.__frame_refresh
            
class Bullet(pygame.sprite.Sprite):
    '''This is the Bullet class sprite that creates a bullet that is used to 
    hit the player or the enemies. The direction will vary on degrees passed in.
    '''
    
    def __init__(self, screen, shooter, shoot_type, degs = None):
        '''This method initializes the bullet sprite using parameters such 
        as screen, shooter of bullet, shoot type, and degrees.'''
   
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        #Load appropriate image for bullet depending on shoot type.
        self.image = pygame.image.load("images/bullet"
                                       +str(shoot_type)+".png").convert_alpha()
        
        #Set up default values.
        self.rect = self.image.get_rect()
        self.rect.center = shooter.rect.center
        self.__screen = screen
        self.__dx = 0
        self.__dy = 0
        
        #Set unique bullet speed and direction depending on shoot type.
        if shoot_type == 0:
            self.__dy = -20
        elif shoot_type ==1:
            self.__dx = math.cos(math.radians(degs)) * 20
            self.__dy = -(math.sin(math.radians(degs)) * 20)            
        elif shoot_type == 2:
            self.__dx = math.cos(math.radians(degs)) * 6
            self.__dy = -(math.sin(math.radians(degs)) * 6)
        elif shoot_type ==3:         
            self.__dx = math.cos(math.radians(degs)) * 4
            self.__dy = -(math.sin(math.radians(degs)) * 4)    
        elif shoot_type ==4:
            self.__dx = math.cos(math.radians(degs)) * 6
            self.__dy = -(math.sin(math.radians(degs)) * 6)  
        else:
            self.__dx = math.cos(math.radians(degs)) * 5
            self.__dy = -(math.sin(math.radians(degs)) * 5)              
            
    def get_center(self):
        '''This method returns the center instance. Used in main for sprite
        positioning.'''
        
        #Return instance.
        return self.rect.center
        
    def update(self):
        '''This method will be called automatically to reposition the
        bullet sprite on the screen.'''
            
        #Reposition
        self.rect.centery += self.__dy  
        self.rect.centerx += self.__dx
        
        #Kill bullet if out of screen for effciency.
        if not (-100 <= self.rect.centerx <= self.__screen.get_width()-100)\
           and not \
           (-100 <= self.rect.centery <= self.__screen.get_height()+100):
            self.kill()
        
class Score_tab(pygame.sprite.Sprite):
    '''The score tab class used to keep track of score, highscore, lives, and
    bombs.'''
    
    def __init__(self, screen):
        '''This method initializes the class with appropriate parameters.'''
        
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
 
        #Load image as main surface.
        self.image = pygame.image.load("images/score_tab.png").convert()
        
        #Set default instances.
        self.rect = self.image.get_rect()
        self.rect.center = (screen.get_width()-self.rect.width/2,\
                            screen.get_height()/2)
        self.__screen = screen
        
    def update(self):
        '''This method is called once per frame to update the score tab.'''
        pass
    
class Cloud(pygame.sprite.Sprite):
    '''This is a cloud class that is used to make background more lively.'''
    
    def __init__(self, screen):
        '''This method initializes the cloud class using the screen parameter 
        as bounaries.'''
         
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        #Set instances, randomize properties upon creation.
        self.__screen = screen
        self.__type = 0
        self.__dx = 0
        self.__dy = 0        
        self.random_type()
        self.random_speed()
        
        #Image loading 
        self.image = pygame.image.load("images/cloud"
            +str(self.__type)+".png").convert_alpha()
        self.rect = self.image.get_rect()
        
        #Set position.
        self.random_reset()
        
    def random_type(self):
        '''This method randomizes the type of the cloud for different images.'''
        
        #Randomize type value between 0-2
        self.__type = random.randrange(3)
        
    def random_speed(self):
        '''This method randomizes the speed of the cloud.'''
        
        #Randomize direction of x vector between -1 or 1.
        self.__dx = random.randrange(-1, 2, 2) 
        
        #Randomize values of y vector between 2-4
        self.__dy = random.randrange(2, 5)
        
    def random_reset(self):
        '''This method randomizes the position of the cloud near the top of the
        screen.'''
        
        #x pos is static
        x_pos = (self.__screen.get_width()-200)/2
        #y pos is randomized for varied cloud appearance
        y_pos = random.randrange(-200, -39, 2)
        
        #Position cloud.
        self.rect.center = (x_pos, y_pos)
        
    def update(self):
        '''This method automatically runs once per frame to update the cloud. 
        Reset cloud if appropriate.'''
        
        #Update position using vectors.
        self.rect.centerx += self.__dx
        self.rect.centery += self.__dy
        
        #Reset cloud if out of bottom.
        if self.rect.top > self.__screen.get_height():
            self.random_type()
            self.random_speed()
            self.random_reset()
   
class Background(pygame.sprite.Sprite):
    '''This class defines a surface sprite to blit the scrolling background on.
    This background will reset at a specific position while scrolling to give 
    illusion of infinite height.'''
        
    def __init__(self):
        '''This initializer creates surface, loads background and initializes
        other instances needed for scrolling in update'''
        
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
 
        # Create surface initialize rect, position.
        self.image = pygame.Surface((440, 480))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0,0)
        
        #Load image and initialize other instances.
        self.__background = pygame.image.load("images/background.png").convert()
        self.__background_y = -440
        self.__dy = 1
        
    def get_surface(self):
        '''This method returns the surface of the background which is needed for
        the clear method in main.'''
        
        #Return instance.
        return self.image
        
    def update(self):
        '''This method will be called automatically to reposition the
        background image on the surface, seemingly scrolling.'''
        
        #Update image.
        self.__background_y += self.__dy
        
        #Blit image on to surface.
        self.image.blit(self.__background, (0, self.__background_y))
        
        #Reset image to origin when appropriate
        if self.__background_y >= 0:
            self.__background_y = -440