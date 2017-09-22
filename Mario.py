import pygame, random, math, time
from pygame.locals import *
from spritesheet_functions import SpriteSheet

class Player(pygame.sprite.Sprite):

    def __init__(self, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)

        self.jump_sound = pygame.mixer.Sound('./sound/small_jump.ogg')
        self.brick_hit_sound = pygame.mixer.Sound('./sound/brick_smash.ogg')
        self.coin_sound = pygame.mixer.Sound('./sound/coin.ogg')
        self.shroom_sound = pygame.mixer.Sound('./sound/powerup.ogg')
        self.stomp_sound = pygame.mixer.Sound('./sound/stomp.ogg')
        self.hit_sound = pygame.mixer.Sound('./sound/bump.ogg')
        self.flagpole_sound = pygame.mixer.Sound('./sound/flagpole.wav')
        self.big_jump_sound = pygame.mixer.Sound('./sound/big_jump.ogg')

        self.other_font = pygame.font.Font('other_font.ttf',14)
        
        self.character = 'datboi'

        self.walking_frames_l = []
        self.walking_frames_r = []

        self.big_walking_frames_l = []
        self.big_walking_frames_r = []

        if self.character == 'datboi':

            sprite_sheet = SpriteSheet('datboi_spritesheet.png')

            self.walking_frames_l.append(sprite_sheet.get_image(0,0,47,75))
            self.walking_frames_l.append(sprite_sheet.get_image(47,0,47,75))
            self.walking_frames_l.append(sprite_sheet.get_image(95,0,47,75))
            self.walking_frames_l.append(sprite_sheet.get_image(142,0,47,75))
            self.walking_frames_l.append(sprite_sheet.get_image(191,0,47,75))


            for image in self.walking_frames_l:
                self.walking_frames_r.append(pygame.transform.flip(image,True,False))

            sprite_sheet2 = SpriteSheet('datboi_spritesheet2.png')

            self.big_walking_frames_l.append(sprite_sheet2.get_image(0,0,64,102))
            self.big_walking_frames_l.append(sprite_sheet2.get_image(64,0,64,102))
            self.big_walking_frames_l.append(sprite_sheet2.get_image(128,0,64,102))
            self.big_walking_frames_l.append(sprite_sheet2.get_image(64*3,0,64,102))
            self.big_walking_frames_l.append(sprite_sheet2.get_image(64*4,0,64,102))

            for image in self.big_walking_frames_l:
                self.big_walking_frames_r.append(pygame.transform.flip(image,True,False))




        
        self.x_pos = x_pos
        self.y_pos = y_pos
##        self.image = pygame.Surface([15, 15])
##        self.image.fill(Color('white'))
        self.image = pygame.image.load('datboi5.png')

        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.change_x = 0
        self.change_y = 0

        self.walls = None
        level1 = Level1
        self.shrooms = None
        self.mysteries = None
        self.blocks = None
        self.enemy_sprites = None
        self.health = 1
        self.big = False
        self.goomba_sides = None
        self.goomba_top = None
        self.coin_list = None
        self.flag = None
        self.coolmode = False
        self.coins = 0
        self.score = 0
        

        self.jump_power = -11

        self.grav_power = .4

        self.direction = 'right'

        self.animation_timer = 0
        self.frame = 0

        self.pipetouch = False
        self.gmreset = False

        self.death = False
        self.flagpole = False



    def update(self):

        self.calc_grav() # Take care of gravity
        self.animation_timer += 1

        self.rect.x += self.change_x

        if self.rect.y > 700:
            self.death = True

        if self.health == 0:
            self.death = True

        # Walls Collisions

        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False) # Make "True" in order to create an item that could be picked up that disappears after collision
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right
                
        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)

        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0

        # Colliding with the bottom of Mystery Blocks
        block_hit_list = pygame.sprite.spritecollide(self, self.mysteries, False)
        for block in block_hit_list:
            if block.dead == True:
                pass
            else:
                block.dead = True
                self.score += 100
                

        # Colliding with bottom of bricks
        if self.health == 2:
            block_hit_list = pygame.sprite.spritecollide(self, self.blocks, False)
            for block in block_hit_list:
                self.change_y = 0
                block.dead = True
                self.brick_hit_sound.play()
                self.score += 100

        # FlagPole Collision
        block_hit_list = pygame.sprite.spritecollide(self, self.flag, False)
        for block in block_hit_list:
            self.flagpole = True
            self.flagpole_sound.play()
                
                


        # Picking up shrooms

        block_hit_list = pygame.sprite.spritecollide(self, self.shrooms, True)

        for block in block_hit_list:
            xx = block.rect.centerx
            yy = block.rect.centery
            self.upgrade(xx,yy)
            self.shroom_sound.play()
            self.score += 200
            

        # Goin down pipes

        block_hit_list = pygame.sprite.spritecollide(self, self.pipe_hitboxes, False)

        for block in block_hit_list:
            self.pipetouch = True

        # Killin Goom-Bitches
        block_hit_list = pygame.sprite.spritecollide(self,self.goomba_top, True)

        for block in block_hit_list:
            self.change_y = -7
            block.dead = True
            self.stomp_sound.play()
            self.score += 300
            

        # Getting Killed
        block_hit_list = pygame.sprite.spritecollide(self, self.goomba_sides, True)

        for block in block_hit_list:
            xx = self.rect.centerx
            yy = self.rect.centery
            self.degrade(xx,yy)
            self.change_y = -7
            self.hit_sound.play()

            
        # Picking up Coins
        block_hit_list = pygame.sprite.spritecollide(self, self.coin_list, True)

        for block in block_hit_list:
            self.coins += 1
            self.coin_sound.play()
            self.score += 25
        


        # Animation

        if self.health == 2:
            if self.direction == 'right' and self.animation_timer % 6 == 0:
                if self.change_x == 0:
                    self.frame = 0
                else:
                    self.frame = (self.frame+1) % len(self.big_walking_frames_r)

                self.image = self.big_walking_frames_r[self.frame]
            if self.direction == 'left' and self.animation_timer % 6 == 0:
                if self.change_x == 0:
                    self.frame = 0
                else:
                    self.frame = (self.frame+1) % len(self.big_walking_frames_l)

                self.image = self.big_walking_frames_l[self.frame]


        elif self.health == 1:
            if self.direction == 'right' and self.animation_timer % 6 == 0:
                if self.change_x == 0:
                    self.frame = 0
                else:
                    self.frame = (self.frame+1) % len(self.walking_frames_r)

                self.image = self.walking_frames_r[self.frame]
            if self.direction == 'left' and self.animation_timer % 6 == 0:
                if self.change_x == 0:
                    self.frame = 0
                else:
                    self.frame = (self.frame+1) % len(self.walking_frames_l)

                self.image = self.walking_frames_l[self.frame]

        self.image.set_colorkey(Color('white'))


    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += self.grav_power

    def jump(self):
        self.rect.y += 2 # Move the character down a little
        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
        self.rect.y -= 2 # Move the character back
        

        if block_hit_list:
            self.change_y = self.jump_power
            if self.health == 1:
                self.jump_sound.play()
            if self.health == 2:
                self.big_jump_sound.play()


    def upgrade(self, x_pos, y_pos):
        
        
        self.health = 2
        self.image = self.big_walking_frames_r[self.frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = x_pos
        self.rect.centery = y_pos
        self.big = True

    def degrade(self,x_pos,y_pos):
        self.health -= 1
        self.image = self.walking_frames_r[self.frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = x_pos
        self.rect.centery = y_pos
        


            

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, num):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.num = num


        if self.num == 1:
            self.image = pygame.image.load('./Images/Floors/floor1.png')
        if self.num == 2:
            self.image = pygame.image.load('./Images/Floors/floor2.png')
        if self.num == 3:
            self.image = pygame.image.load('./Images/Floors/floor3.png')
        if self.num == 4:
            self.image = pygame.image.load('./Images/Floors/floor4.png')

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Mystery(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x-10
        self.y = y-10

        self.image = pygame.image.load('./Images/mystery_block.png')

        self.rect = self.image.get_rect()
        self.rect.x = x-10
        self.rect.y = y-10

        self.hit_block = HitBox(self.rect.left + 8,
                                    self.rect.bottom+2)

    def update(self):
        if self.hit_block.dead == True:
            self.image = pygame.image.load('./Images/mystery_hit.png')

class HitBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 14, 1)
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        self.image.fill(Color('black'))
        self.dead = False

class GoombaBox(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 3, 14)
        self.image = pygame.Surface([self.rect.width, self.rect.height])
        self.image.fill(Color('black'))
        self.dead = False


class Brick(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x-10
        self.y = y-10

        self.image = pygame.image.load('./Images/rsz_brick_block.png')

        self.rect = Rect(self.x,self.y,30,33)
        self.rect.x = x-10
        self.rect.y = y-10

        self.hit_block = HitBox(self.rect.left + 6,
                                    self.rect.bottom + 6)

        self.coin = Coin(self.rect.left + 4, self.rect.top - 30)

    def update(self):
        if self.hit_block.dead == True:
            self.kill()
            self.hit_block.kill()
            
          
class Step(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x-10
        self.y = y-10

        self.image = pygame.image.load('./Images/steps.png')

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,height,hitbox):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = 590 - height
        self.hitbox = hitbox

        if height == 65:
            self.image = pygame.image.load('./Images/Pipes/pipe65.png')
        elif height == 95:
            self.image = pygame.image.load('./Images/Pipes/pipe95.png')
        elif height == 125:
            self.image = pygame.image.load('./Images/Pipes/pipe125.png')
        else:
            self.image = pygame.Surface([60,height])
            self.image.fill(Color('green'))

        self.rect = self.image.get_rect()
        self.rect.x = x-30
        self.rect.y = self.y

        if self.hitbox:
            self.hit_block = HitBox(self.rect.left + 10,
                                    self.rect.top - 50)


class Shroom(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load('./Images/mushroom.png')

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def eaten(self):
        self.player.shrooms = True

class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y + 90
        self.size = size
        if self.size == 's':
            self.image = pygame.image.load('./Images/singlecloud.png')
        elif self.size == 't':
            self.image = pygame.image.load('./Images/triplecloud.png')
        elif self.size == 'b1':
            self.image = pygame.image.load('./Images/singlebush.gif')
        elif self.size == 'b3':
            self.image = pygame.image.load('./Images/triplebush.png')
        elif self.size == 'h1':
            self.image = pygame.image.load('./Images/hill1.png')
        elif self.size == 'h3':
            self.image = pygame.image.load('./Images/hill3.png')
        elif self.size == 'sn':
            self.image = pygame.image.load('./Images/send_nudes.png')
        elif self.size == 'castle':
            self.image = pygame.image.load('./Images/castle.png')

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Flag(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load('./Images/flagpole.png')
##        self.image.set_colorkey(Color('white'))
        self.rect = Rect(self.x+40,self.y,10,1000)
        

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load('./Images/coin11.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Goomba(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.image = pygame.image.load('./Images/goomba_transparent.png')
        self.image.set_colorkey(Color('black'))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_pos = self.x
        self.direction = 'left'
        self.animation_timer = 0

        self.l_hitbox = GoombaBox(self.rect.left - 1, self.rect.bottom-16)
        self.r_hitbox = GoombaBox(self.rect.right + 1, self.rect.bottom-16)
        self.t_hitbox = HitBox(self.rect.left + 8, self.rect.top)

    def update(self):
        self.animation_timer += 1
        if self.x_pos < self.original_x - 160:
            self.direction = 'right'
        if self.x_pos > self.original_x:
            self.direction = 'left'
        if self.animation_timer % 3 == 0:
            if self.direction == 'left':
                self.rect.x -= 1
                self.l_hitbox.rect.x -= 1
                self.r_hitbox.rect.x -= 1
                self.t_hitbox.rect.x -= 1
                self.x_pos -= 1
            elif self.direction == 'right':
                self.rect.x += 1
                self.l_hitbox.rect.x += 1
                self.r_hitbox.rect.x += 1
                self.t_hitbox.rect.x += 1
                self.x_pos += 1
        if self.t_hitbox.dead == True:
            self.l_hitbox.kill()
            self.r_hitbox.kill()
            self.kill()
        self.image.set_colorkey(Color('black'))
            

        


        

class Level:

    def __init__(self, width, height):
        # For all walls that you can touch and jump on
        self.wall_list = pygame.sprite.Group()
        # For mushrooms
        self.shroom_list= pygame.sprite.Group()
        # For all images that you cannot collide with
        self.cloud_list = pygame.sprite.Group()
        # For the SN picture
        self.sn_list = pygame.sprite.Group()
        # For the hitboxes on the mystery boxes
        self.mystery_list = pygame.sprite.Group()
        # For the actual mystery blocks
        self.mysteryblock_list = pygame.sprite.Group()
        # For the normal bricks' hitboxes
        self.brickhitbox_list = pygame.sprite.Group()
        # For the bricks
        self.bricks_list = pygame.sprite.Group()
        # For Pipe hitboxes
        self.pipe_hitbox_list = pygame.sprite.Group()
        # Goombas and Enemies
        self.enemy_sprites = pygame.sprite.Group()
        # Goomba Side-Hitboxes
        self.goomba_sides = pygame.sprite.Group()
        # Goomba Top-Hitboxes
        self.goomba_top = pygame.sprite.Group()
        # Coin List
        self.coin_list = pygame.sprite.Group()
        # Flagpole
        self.flagpole = pygame.sprite.Group()

        self.width = width
        self.height = height

        self.world_shift = 0

        self.level_limit = 9000 # how far does your character go to win?

    def shift_world(self, shift_x):
        self.world_shift -= shift_x

        for wall in self.wall_list:
            wall.rect.x += shift_x

        for shroom in self.shroom_list:
            shroom.rect.x += shift_x

        for mystery in self.mystery_list:
            mystery.rect.x += shift_x

        for brick in self.brickhitbox_list:
            brick.rect.x += shift_x

        for cloud in self.cloud_list:
            cloud.rect.x += shift_x

        for s in self.sn_list:
            s.rect.x += shift_x

        for enemy in self.enemy_sprites:
            enemy.rect.x += shift_x

        for box in self.goomba_sides:
            box.rect.x += shift_x

        for box in self.goomba_top:
            box.rect.x += shift_x

        for coin in self.coin_list:
            coin.rect.x += shift_x

        for flag in self.flagpole:
            flag.rect.x += shift_x



class Level1(Level):

    def __init__(self, width, height):
        Level.__init__(self, width, height)
        walls =  [Wall(0,590,2210,10,'black',1),
                  Wall(2270,590,480,10,'black',2),
                  Wall(2850,590,2055,10,'black',3),
                  Wall(4975,590,1025,10,'black',4),
                  Wall(6000,590,2210,10, 'black', 1),
                  Wall(8202,590,480,10,'black',2)] # left bottom third

        #These coordinates are only accurate for the middle of the blocks
        #in order to fix that I have to subtract 15 from each direction for all
        #I need to learn how to make a for loop do that.

##        lb =343
##        hb = 473
        lb = 300
        hb = 450

        mysteries = [Mystery(530,hb),Mystery(690,hb),
                     Mystery(750,hb),Mystery(720,lb),
                     Mystery(2510,hb),Mystery(3020,lb),
                     Mystery(3410,lb),Mystery(3500,hb),
                     Mystery(3590,hb),Mystery(3505,lb),
                     Mystery(4145,lb),Mystery(4175,lb),
                     Mystery(5455,hb)]

        for mystery in mysteries:
            self.mystery_list.add(mystery.hit_block)


        bricks = [Brick(660,hb),Brick(720,hb),
                  Brick(780,hb),Brick(2480,hb),
                  Brick(2540,hb),Brick(2570,lb),
                  Brick(2600,lb),Brick(2630,lb),
                  Brick(2660,lb),Brick(2690,lb),
                  Brick(2720,lb),Brick(2750,lb),
                  Brick(2780,lb),Brick(2930,lb),
                  Brick(2960,lb),Brick(2990,lb),
                  Brick(3020,hb),Brick(3215,hb),
                  Brick(3245,hb),Brick(3790,hb),
                  Brick(3885,lb),Brick(3915,lb),
                  Brick(3945,lb),Brick(4115,lb),
                  Brick(4145,hb),Brick(4175,hb),
                  Brick(4205,lb),Brick(5395,hb),
                  Brick(5425,hb),Brick(5485,hb)]

        for brick in bricks:
            self.brickhitbox_list.add(brick.hit_block)

        for brick in bricks:
            self.coin_list.add(brick.coin)

        steppy = 560

        base = 5840

        base2 = 5840 + 30*9

        steps = [Step(4305,steppy),Step(4335,steppy),Step(4365,steppy),
                 Step(4395,steppy),Step(4335,steppy-30),Step(4365,steppy-30),
                 Step(4395,steppy-30),Step(4365,steppy-60),Step(4395,steppy-60),
                 Step(4395,steppy-90),

                 Step(4495,steppy),Step(4525,steppy),Step(4555,steppy),
                 Step(4585,steppy),Step(4495,steppy-30),Step(4525,steppy-30),
                 Step(4555,steppy-30),Step(4495,steppy-60),Step(4525,steppy-60),
                 Step(4495,steppy-90),

                 Step(4780-2,steppy),Step(4810-2,steppy),Step(4840-2,steppy),
                 Step(4870-2,steppy),Step(4810-2,steppy-30),Step(4840-2,steppy-30),
                 Step(4870-2,steppy-30),Step(4840-2,steppy-60),Step(4870-2,steppy-60),
                 Step(4870-2,steppy-90),

                 Step(4975,steppy),Step(5005,steppy),Step(5035,steppy),
                 Step(5065,steppy),Step(4975,steppy-30),Step(5005,steppy-30),
                 Step(5035,steppy-30),Step(4975,steppy-60),Step(5005,steppy-60),
                 Step(4975,steppy-90),

                 Step(base,steppy),Step(base+30,steppy),Step(base+30*2,steppy),
                 Step(base+30*3,steppy),Step(base+30*4,steppy),Step(base+30*5,steppy),
                 Step(base+30*6,steppy),Step(base+30*7,steppy),Step(base+30*8,steppy),

                 Step(base+30,steppy-30),Step(base+30*2,steppy-30),
                 Step(base+30*3,steppy-30),Step(base+30*4,steppy-30),Step(base+30*5,steppy-30),
                 Step(base+30*6,steppy-30),Step(base+30*7,steppy-30),Step(base+30*8,steppy-30),

                 Step(base+30*2,steppy-60),
                 Step(base+30*3,steppy-60),Step(base+30*4,steppy-60),Step(base+30*5,steppy-60),
                 Step(base+30*6,steppy-60),Step(base+30*7,steppy-60),Step(base+30*8,steppy-60),

    
                 Step(base+30*3,steppy-90),Step(base+30*4,steppy-90),Step(base+30*5,steppy-90),
                 Step(base+30*6,steppy-90),Step(base+30*7,steppy-90),Step(base+30*8,steppy-90),

                 Step(base+30*4,steppy-120),Step(base+30*5,steppy-120),
                 Step(base+30*6,steppy-120),Step(base+30*7,steppy-120),Step(base+30*8,steppy-120),

                 Step(base+30*5,steppy-150),
                 Step(base+30*6,steppy-150),Step(base+30*7,steppy-150),Step(base+30*8,steppy-150),

                
                 Step(base+30*6,steppy-180),Step(base+30*7,steppy-180),Step(base+30*8,steppy-180),

                 Step(base+30*7,steppy-210),Step(base+30*8,steppy-210)]

        step2 = [Step(base2 + 30*i,steppy - 30*n) for i in range(50) for n in range(8)]

        pipes = [Pipe(930,65,False),Pipe(1250,95,False),Pipe(1505,125,True),
                 Pipe(1855,125,False),Pipe(5250,65,False),Pipe(5765,65,False)]
        
        # Getting the pipe hitboxes
        for pipe in pipes:
            if pipe.hitbox:
                self.pipe_hitbox_list.add(pipe.hit_block)
                
        self.shrooms = [Shroom(528,hb-30)]

        clouds = [Cloud(660,76,'s'),Cloud(945,105,'t'),Cloud(1218,76,'s'),
                  Cloud(1840,106,'s'),Cloud(2190,75,'s'),Cloud(2485,110,'t'),
                  Cloud(2755,75,'t'),Cloud(3380,105,'s'),Cloud(3730,75,'s'),
                  Cloud(4020,105,'t'),Cloud(4290,75,'s'),Cloud(4915,110,'s'),
                  Cloud(5270,75,'s'),Cloud(5560,105,'t'),Cloud(5825,75,'t'),
                  Cloud(6450,105,'s'),Cloud(8040,125,'castle')]
        sn = [Cloud(6170,290,'sn')]

        bushy = 470

        bushes = [Cloud(373,bushy,'b3'),Cloud(754,bushy,'b1'),Cloud(1360,bushy,'b1'),
                  Cloud(1910,bushy,'b3'),Cloud(2290,bushy,'b1'),Cloud(2868,bushy,'b3'),
                  Cloud(3440,bushy,'b3'),Cloud(3830,bushy,'b1'),Cloud(5360,bushy,'b1')]
        goombas = [Goomba(1140,steppy+2), Goomba(1190,steppy+2),
                   Goomba(1795,steppy+2), Goomba(1745,steppy+2),
                   Goomba(2600,steppy+2), Goomba(2550,steppy+2),
                   Goomba(5700,steppy+2), Goomba(5650,steppy+2),
                   Goomba(5500,steppy+2), Goomba(5450,steppy+2)]

        flags = [Flag(7700, 112)]
        for flag in flags:
            self.flagpole.add(flag)

        for goomba in goombas:
            self.goomba_sides.add(goomba.l_hitbox)
            self.goomba_sides.add(goomba.r_hitbox)
            self.goomba_top.add(goomba.t_hitbox)
                  

        for mystery in mysteries:
            self.wall_list.add(mystery)
            self.mysteryblock_list.add(mystery)
        for brick in bricks:
            self.wall_list.add(brick)
            self.bricks_list.add(brick)
        for step in steps:
            self.wall_list.add(step)
        for step in step2:
            self.wall_list.add(step)
        for pipe in pipes:
            self.wall_list.add(pipe)
        for shroom in self.shrooms:
            self.shroom_list.add(shroom)
        for wall in walls:
            self.wall_list.add(wall)
        for cloud in clouds:
            self.cloud_list.add(cloud)
        for bush in bushes:
            self.cloud_list.add(bush)

        for s in sn:
            self.sn_list.add(s)

        for goomba in goombas:
            self.enemy_sprites.add(goomba)

class GameMain():

    done = False
    color_bg = Color(107,140,255)

    def __init__(self, width=800, height=650):

        
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        self.width,self.height = width,height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        self.player = Player(50,200)
##        self.player = Player(7750,100)
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.player)

        self.levels = [Level1(self.width, self.height)]

        self.current_level_number = 0
        self.current_level = self.levels[self.current_level_number]

        self.player.walls = self.current_level.wall_list
        self.player.shrooms = self.current_level.shroom_list
        self.player.mysteries = self.current_level.mystery_list
        self.player.blocks = self.current_level.brickhitbox_list
        self.player.pipe_hitboxes = self.current_level.pipe_hitbox_list
        self.player.enemies = self.current_level.enemy_sprites
        self.player.goomba_sides = self.current_level.goomba_sides
        self.player.goomba_top = self.current_level.goomba_top
        self.player.coin_list = self.current_level.coin_list
        self.player.flag = self.current_level.flagpole

        pygame.display.set_caption('Super Memio Bois')


        bg_music = pygame.mixer.music.load('mario_music.mp3')
        self.death_sound = pygame.mixer.Sound('./sound/death.wav')
        self.game_win_sound = pygame.mixer.Sound('./sound/game_over.ogg')
        pygame.mixer.music.play(5)
        self.current_screen = 'title'

        self.font = pygame.font.Font('mario_font.ttf',40)
        self.other_font = pygame.font.Font('other_font.ttf',14)

        self.time = 250
        self.animation_timer = 0

        self.counter3 = 0
        self.death_timer = 0
        self.win_timer = 0
        self.win2_timer = 0
        self.coolmode = False
        self.usuck = False
        self.d = False
        self.a = False
        self.t = False
        self.b = False
        self.o = False
        self.i = False

        # High Score

        with open('highscore.txt', 'rb') as f:
            self.highscore = int(f.read())

    def draw_title(self):
        self.__init__()
        self.screen.fill(Color('white'))
        self.death_timer = 0
        titlescreen = pygame.image.load('loadscreen.png')
        self.screen.blit(titlescreen, (0,0))
        pygame.display.flip()

    def draw_death(self):
        self.death_timer += 1
        pygame.mixer.music.stop()
        if self.counter3 == 0:
            self.death_sound.play()
            self.counter3 += 1
        self.screen.fill(Color('black'))
        self.game_over_label = self.font.render('GAME OVER',1,Color('white'))
        self.highscore_label = self.font.render('HIGHSCORE: {}'.format(self.highscore),1,Color('white'))
        self.screen.blit(self.highscore_label, (250,500))
        self.screen.blit(self.game_over_label, (280,300))
        pygame.display.flip()
        if self.death_timer > 2300:
            self.current_screen = 'title'

    def win(self):
        self.win_timer += 1
        pygame.mixer.music.stop()
        if self.win_timer > 200:
            self.current_screen = 'win2'

    def draw_win(self):
        self.game_win_sound.play()
        self.win2_timer += 1
        self.screen.fill(Color('black'))
        self.win_label = self.font.render('YOU WON!',1,Color('white'))
        self.screen.blit(self.win_label, (300,300))
        self.winscore_label  = self.font.render('SCORE: {}'.format(self.player.score + (self.time * 3)),1,Color('white'))
        self.screen.blit(self.winscore_label, (280,100))
        if self.player.score + (self.time * 3) > self.highscore:
            self.highscore = self.player.score + (self.time * 3)
        self.highscore_label = self.font.render('HIGHSCORE: {}'.format(self.highscore),1,Color('white'))
        self.screen.blit(self.highscore_label, (280,500))
        pygame.display.flip()
        with open('highscore.txt', 'w') as f:
            f.write('{}'.format(self.highscore))
        if self.win2_timer > 2000:
            self.current_screen = 'title'

    def handle_events_title(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.done == True
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    self.player.gmreset = False
                    self.current_screen = 'game'
                elif event.key == K_ESCAPE:
                    self.done = True
                                          


    def main_loop(self):
        while not self.done:
            self.handle_events()
            if self.time < 0:
                self.current_screen = 'death'
            if self.player.death:
                self.current_screen = 'death'
                self.player.death = False
            if self.player.flagpole:
                self.player.flagpole = False
                
                self.current_screen = 'win'
            elif self.current_screen == 'game':
                if self.player.rect.right >= 500:
                    diff = self.player.rect.right - 500
                    self.player.rect.right = 500
                    self.current_level.shift_world(-diff)
                elif self.player.rect.left <= 300:
                    diff = 300 - self.player.rect.left
                    self.player.rect.left = 300
                    self.current_level.shift_world(diff)
                self.player.update()
                self.current_level.mysteryblock_list.update()
                self.current_level.bricks_list.update()
                self.current_level.enemy_sprites.update()
                self.animation_timer += 1
                if self.animation_timer % 30 == 0:
                    self.time -= 1
    ##            self.change_level()
                self.draw()
                self.clock.tick(60)
            elif self.current_screen == 'title':
                self.draw_title()
                self.handle_events_title()
            elif self.current_screen == 'death':
                self.draw_death()
            elif self.current_screen == 'win':
                self.draw()
                self.win()
            elif self.current_screen == 'win2':
                self.draw_win()
        pygame.quit()


    def down_pipe(self):
        pass

    def draw(self):
        self.scoreplus_timer = 0
        self.screen.fill(self.color_bg)
        self.current_level.cloud_list.draw(self.screen)
        self.current_level.enemy_sprites.draw(self.screen)
        self.sprites.draw(self.screen)
        self.current_level.wall_list.draw(self.screen)
        self.current_level.shroom_list.draw(self.screen)
        self.current_level.pipe_hitbox_list.draw(self.screen)
        self.d_label = self.font.render('HELLO',1,Color('white'))
        self.a_label = self.font.render('MY',1,Color('white'))
        self.t_label = self.font.render('NAME',1,Color('white'))
        self.b_label = self.font.render('IS',1,Color('white'))
        self.o_label = self.font.render('DAT',1,Color('white'))
        self.i_label = self.font.render('BOI!',1,Color('white'))
        
##        Hit Boxes
##        self.current_level.mystery_list.draw(self.screen)
##        self.current_level.brickhitbox_list.draw(self.screen)
        self.current_level.pipe_hitbox_list.draw(self.screen)
        if self.coolmode:
            self.current_level.sn_list.draw(self.screen)
        if self.d:
            self.screen.blit(self.d_label, (self.player.rect.left - 50,self.player.rect.top-50))
        elif self.a:
            self.screen.blit(self.a_label, (self.player.rect.left - 50,self.player.rect.top-50))
        elif self.t:
            self.screen.blit(self.t_label, (self.player.rect.left - 50,self.player.rect.top-50))
        elif self.b:
            self.screen.blit(self.b_label, (self.player.rect.left - 50,self.player.rect.top-50))
        elif self.o:
            self.screen.blit(self.o_label, (self.player.rect.left - 50,self.player.rect.top-50))
        elif self.i:
            self.screen.blit(self.i_label, (self.player.rect.left - 50,self.player.rect.top-50))
##        self.current_level.goomba_top.draw(self.screen)
##        self.current_level.goomba_sides.draw(self.screen)
        self.current_level.coin_list.draw(self.screen)

        self.current_level.flagpole.draw(self.screen)

        # Mario Word
        self.mario_label = self.font.render('MARIO',1,Color('white'))
        self.screen.blit(self.mario_label, (60,30))

        # Score
        self.score_label = self.font.render('{:05d}'.format(self.player.score),1,Color('white'))
        self.screen.blit(self.score_label, (60,60))

        # Coin Amount
        self.coin_label = self.font.render('x{:02d}'.format(self.player.coins),1,Color('white'))
        self.screen.blit(self.coin_label, (300,60))

        # Coin
        self.coin_group = pygame.sprite.Group()
        self.coins12 = [Coin(270,65)]
        for coin in self.coins12:
            self.coin_group.add(coin)
        self.coin_group.draw(self.screen)
        

        # World Word
        self.world_word_label = self.font.render('WORLD',1,Color('white'))
        self.screen.blit(self.world_word_label, (450,30))

        # World
        self.world_label = self.font.render(' 1-1 ',1,Color('white'))
        self.screen.blit(self.world_label, (450,60))

        # Time Word
        self.time_word_label = self.font.render('TIME',1,Color('white'))
        self.screen.blit(self.time_word_label, (650,30))

        # Time
        self.time_label = self.font.render(' {}'.format(self.time),1,Color('white'))
        self.screen.blit(self.time_label, (650,60))

        pygame.display.flip()

    def handle_events(self):

        events = pygame.event.get()

        keys = pygame.key.get_pressed()

        for event in events:

            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.done = True
                elif event.key == K_LEFT:
                    self.player.change_x = -5
                    self.player.direction = 'left'
                elif event.key == K_RIGHT:
                    self.player.change_x = 5
                    self.player.direction = 'right'
                elif event.key == K_SPACE:
                    self.player.jump()
                elif event.key == K_c:
                    self.coolmode = True
                elif event.key == K_DOWN:
                    if self.player.pipetouch:
                        down_pipe()
                elif event.key == K_d:
                    self.d = True
                elif event.key == K_a:
                    self.a = True
                elif event.key == K_t:
                    self.t = True
                elif event.key == K_b:
                    self.b = True
                elif event.key == K_o:
                    self.o = True
                elif event.key == K_i:
                    self.i = True
                

            elif event.type == KEYUP:
                if event.key == K_LEFT and self.player.change_x < 0:
                    self.player.change_x = 0
                elif event.key == K_RIGHT and self.player.change_x > 0:
                    self.player.change_x = 0
                elif event.key == K_c:
                    self.coolmode = False
                elif event.key == K_d:
                    self.d = False
                elif event.key == K_a:
                    self.a = False
                elif event.key == K_t:
                    self.t = False
                elif event.key == K_b:
                    self.b = False
                elif event.key == K_o:
                    self.o = False
                elif event.key == K_i:
                    self.i = False
##                elif event.key == K_DOWN:
##                    if self.player.health == 2:
##                        self.player.upgrade(self.player.rect.x,self.player.rect.y)

                                                

if __name__ == '__main__':
    game = GameMain()
    game.main_loop()
