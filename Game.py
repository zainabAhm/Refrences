
import pygame 
from os import path
import pickle
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()

canvasWeidth=500
canvasHeight=500
canvas= pygame.display.set_mode((canvasWeidth,canvasHeight))
pygame.display.set_caption("Term Project")

#Defining variables
tileSize=25
gameOver = 0
menu=True

fps=30
moveRight= False
moveLeft=False
moveUp=False
moveDown=False
index=0
score = 0       
level = 1
maximumLevels = 3
#colors
sage = (157, 193, 131)
red=(190, 6, 0)
black=(0, 0, 0)
#loading images and adjusting their sizes
background =pygame.image.load("Background.png")
bkg = pygame.transform.scale(background,((500,500)))
restartImage=pygame.image.load("pics/restart.png")
restartImage=pygame.transform.scale(restartImage,((30,30)))
playImage=pygame.image.load("pics/play.png")
playImage=pygame.transform.scale(playImage,((70,30)))
exitImage=pygame.image.load("pics/exit.png")
exitImage=pygame.transform.scale(exitImage,((90,30)))
gemImage=pygame.image.load("pics/gem.png")
saveImage=pygame.image.load("pics/save.png")
# bulletImage=pygame.image.load("pics/bullet.png")
# bulletImage=pygame.transform.scale(bulletImage,((10,10)))

 



#to move to next levels
def startLevel(level):
    character.reset(30,canvasHeight-60)
    zombie_group.empty()
    platform_group.empty()
    lava_group.empty()
    flag_group.empty()
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        gameSetup = pickle.load(pickle_in)
    world=World(gameSetup)
    
    return world
#buttons for restarting/exiting the main menu and starting the game
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed=False
    
    def draw(self):
        canvas.blit(self.image,self.rect)
        clicking=False

#         #Mouse position
        mousePosition = pygame.mouse.get_pos()

        if self.rect.collidepoint(mousePosition):
            if pygame.mouse.get_pressed()[0] == 1 and self.pressed == False:
                clicking = True
                self.pressed = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.pressed = False


        #draw button
        canvas.blit(self.image, self.rect)

        return clicking
    
 
#The player(ball)
class Character:
    def __init__(self, x, y):
        self.images_Right=list()
        self.images_Left=list()
        self.index=0
        self.counter=0
        for num in range(1,10):
            rightImage=pygame.image.load("ball.png")
            rightImage=pygame.transform.scale(rightImage,(30,30))
            leftImage = pygame.transform.flip(rightImage, True, False)
            self.images_Right.append(rightImage)
            self.images_Left.append(leftImage)
        
        self.deadImage =pygame.image.load("pics/dead.png")
        self.image = self.images_Right[self.index]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.pixelsMovementsY=0
        self.jump =False
        self.direction=0
        self.inAir = True
        self.bullets = []
        self.x = x
        self.y = y
        
    def drawCharacter(self,gameOver):
        x=0
        y=0
        walkingDelay=10
        verticalTilesCollision=20
        
             #player keyboard movements       
        if gameOver == 0:
            userInput = pygame.key.get_pressed()
            if userInput[pygame.K_SPACE] and self.jump==False and self.inAir==False:
                self.pixelsMovementsY= -15
                self.jump=True
            if userInput[pygame.K_SPACE]==False:
                self.jump=False
            if userInput[pygame.K_LEFT]:
                x -=5
                self.counter +=1
                self.direction=-1
            if userInput[pygame.K_RIGHT]:
                x +=5
                self.counter +=1
                self.direction=1
            if userInput[pygame.K_LEFT] == False and userInput[pygame.K_RIGHT]==False:
                self.counter=0
                self.index=0
                if self.direction==1:
                    self.imgae=self.images_Right[self.index]
                if self.direction==-1:
                    self.imgae=self.images_Left[self.index]



            if self.counter > walkingDelay:
                self.counter=0
                self.index +=1
                if self.index >= len(self.images_Right):
                    self.index=0
                if self.direction==1:
                    self.imgae=self.images_Right[self.index]
                if self.direction==-1:    
                    self.imgae=self.images_Left[self.index]
         
      
         
        #to bring the player back to ground after jumping
            self.pixelsMovementsY +=1
            if self.pixelsMovementsY >9:
                self.pixelsMovementsY=9 
            y +=self.pixelsMovementsY
            #collision:
            self.inAir=True
            for tile in world.tileList:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.pixelsMovementsY < 0:
                        y = tile[1].bottom - self.rect.top
                        self.pixelsMovementsY = 0
                    elif self.pixelsMovementsY >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.pixelsMovementsY = 0
                        self.inAir=False
            
            
                        # collision with zombies
            if pygame.sprite.spritecollide(self, zombie_group, False):
                gameOver = -1

                #Falling into lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                gameOver = -1
                
                #collision with the end of level flag
            if pygame.sprite.spritecollide(self, flag_group, False):
                gameOver = 1
#                 global score
#                 score +=1



         #collision with moivng tiles(platforms)
            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x=0
                    
                if platform.rect.colliderect(self.rect.x ,  self.rect.y+y, self.width, self.height):
                    if abs((self.rect.top + y) - platform.rect.bottom )< verticalTilesCollision:
                        self.pixelsMovementsY=0
                        y=platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + y) - platform.rect.top) < verticalTilesCollision:
                        self.rect.bottom=platform.rect.top -1 
                        y=0
                        self.inAir=False
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
            
   

            
        
            #update the character's position
            self.rect.x += x
            self.rect.y += y
            
            
        elif gameOver == -1:
            self.image = self.deadImage
            canvas.fill(red)
            alert(canvas , "YOU LOST ! ")
            self.rect.y -= 5
        
        canvas.blit(self.image, self.rect)

        return gameOver   

        #Create the character
        canvas.blit(self.image,self.rect)
        
         
#     def shoot(self):
#         userInput = pygame.key.get_pressed()
#         if userInput[pygame.K_s]:
#             bullet = Bullet(self.x, self.y, self.direction())
#             self.bullets.append(bullet)
#         for bullet in self.bullets:
#             bullet.move()
            
            
            
    def reset(self, x, y):
        self.images_Right=list()
        self.images_Left=list()
        self.index=0
        self.counter=0
        for num in range(1,10):
            rightImage=pygame.image.load("pics/ball.png")
#             rightImage=pygame.image.load(f'pics/right{num}.png')
            rightImage=pygame.transform.scale(rightImage,(20,20))
            leftImage = pygame.transform.flip(rightImage, True, False)
            self.images_Right.append(rightImage)
            self.images_Left.append(leftImage)
        
        self.deadImage =pygame.image.load("pics/dead.png")
        self.image = self.images_Right[self.index]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.pixelsMovementsY=0
        self.jump =False
        self.direction=0
        self.inAir = True
        
        

            
            


# class Bullet:
#     def __init__(self, x, y, direction):
#         self.xx = xx + 15
#         self.y = yy + 25
#         self.direction = direction
# 
#     def draw_bullet(self):
#         canvas.blit(bulletImage, (self.x, self.y))
#       #movement of the bullet
#     def move(self):
#         if self.direction == 1:
#             self.x += 15
#         if self.direction == -1:
#             self.x -= 15
        
        
       
        

# text on the side of the game screen




def sideBar(canvas):
    font = pygame.font.SysFont("Arial Bold", 30)
    offset = 40
    text = font.render("Score:", True, (0,0,0))
    text_rect = text.get_rect(center=(70, (offset) ))
    canvas.blit(text, text_rect)
    
    
    text = font.render(str(score), True, (0,0,0))
    text_rect = text.get_rect(center=(110, (offset) ))
    canvas.blit(text, text_rect)
    
def alert(canvas, text):

    font = pygame.font.SysFont("Arial Bold", 70)

    text = font.render(text, True, black)
    text_rect = text.get_rect(center=(canvasWeidth/2, canvasHeight/2 ))
    canvas.blit(text, text_rect)
        
#creating zombie enemies
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("pics/zombie.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        
#drawing zombie enemies        
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter +=1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
 

zombie_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
gem_group=pygame.sprite.Group()
flag_group=pygame.sprite.Group()
platform_group=pygame.sprite.Group()



class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        lavaImage = pygame.image.load('pics/lava.png')
        self.image = pygame.transform.scale(lavaImage, (tileSize, tileSize // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
      


class Gem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        gemImage = pygame.image.load('pics/gem.png')
        self.image = pygame.transform.scale(gemImage, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('pics/flag.png')
        self.image = pygame.transform.scale(image, (tileSize-10, tileSize ))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
        


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y,move_x,move_y):
        pygame.sprite.Sprite.__init__(self)
        imageT = pygame.image.load('pics/stepp.png')
        self.image = pygame.transform.scale(imageT, (tileSize, tileSize//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y
        

        
    def update(self):
        self.rect.x += self.move_direction*self.move_x
        self.rect.y += self.move_direction*self.move_y
        self.move_counter +=1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
            
          

                        
            

 

class World():
    def __init__(self,Setup):
        self.tileList=[]
        
        #the image of the steps(tiles)
        steppp=pygame.image.load("pics/steppp.png")
        stepp=pygame.image.load("pics/stepp.png")
        rowCount=0
        for row in Setup:
            columnCount=0
            for tile in row:
                if tile==1:
                    img=pygame.transform.scale(steppp,(tileSize,tileSize))
                    img_rect=img.get_rect()
                    img_rect.x= columnCount*tileSize
                    img_rect.y= rowCount*tileSize
                    tile=(img,img_rect)
                    self.tileList.append(tile)
                if tile==2:
                    img=pygame.transform.scale(stepp,(tileSize,tileSize))
                    img_rect=img.get_rect()
                    img_rect.x= columnCount*tileSize
                    img_rect.y= rowCount*tileSize
                    tile=(img,img_rect)
                    self.tileList.append(tile)
                    #creation of the zombie
                if tile == 3:
                    zombie = Enemy(columnCount * tileSize, rowCount * tileSize -15)
                    zombie_group.add(zombie)
                if tile==4:
                    platform=Platform(columnCount * tileSize, rowCount * tileSize,1,0)
                    platform_group.add(platform)
                if tile==5:
                    platform=Platform(columnCount * tileSize, rowCount * tileSize,0,1)
                    platform_group.add(platform)                    
                if tile==6:
                    lava = Lava(columnCount * tileSize, rowCount * tileSize + (tileSize // 2))
                    lava_group.add(lava)
                if tile ==7:
                    gem= Gem(columnCount * tileSize+(tileSize//2), rowCount * tileSize + (tileSize // 2))
                    gem_group.add(gem)
                if tile==8:
                    flag = Flag(columnCount * tileSize, rowCount * tileSize)
                    flag_group.add(flag)                      
                columnCount +=1
            rowCount +=1
            
    def draw(self):
        for tile in self.tileList:
            canvas.blit(tile[0],tile[1])
            pygame.draw.rect(canvas,(255,255,255),tile[1],1)
            
               
#choosing the coordinates to place the tiles/platforms/characters
gameSetup =[
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
    [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

#starting place of the character(player) and pictures
character=Character(30,canvasHeight-60)
restartButton = Button(canvasWeidth//2 , canvasHeight//2-50, restartImage)
playButton= Button(canvasWeidth//2-20 , canvasHeight//2-30, playImage)
exitButton=Button(canvasWeidth//2-240 , canvasHeight//2-240, exitImage)




#set up world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    gameSetup = pickle.load(pickle_in)
world=World(gameSetup)



execution=True

while execution:
#     character.shoot()
    clock.tick(fps)
    canvas.fill((0,0,0))
    canvas.blit(bkg, (0, 0))
#     for bullet in character.bullets:
#         bullet.draw_bullet()
    
    if menu==True:
        if playButton.draw()==True:
            menu=False
        if exitButton.draw() ==True:
            execution=False


    else:
        world.draw()
        
        if gameOver == 0:
            zombie_group.update()
            platform_group.update()
            
            if pygame.sprite.spritecollide(character,gem_group,True):
                score =score + 1
            sideBar(canvas)
        
        zombie_group.draw(canvas)
        lava_group.draw(canvas)
        gem_group.draw(canvas)
        flag_group.draw(canvas)
        platform_group.draw(canvas)


        gameOver = character.drawCharacter(gameOver)




#player lost
        if gameOver== -1:
            if restartButton.draw():
                gameSetup =[]
                world=startLevel(level)
                gameOver=0
                score=0
                


#player goes to next level                
        if gameOver== 1:
            level += 1
            if level <= maximumLevels:
                gameSetup =[]
                world=startLevel(level)
                gameOver=0
                
            else:
                if restartButton.draw():
                    level = 1
                    gameSetup =[]
                    world = startLevel(level)
                    gameOver=0

                
        if level > 3:
            canvas.fill(sage)
            alert(canvas, 'Congratulations!')        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            execution=False

    pygame.display.update()            
pygame.quit()
#Refrences:
#for the ghost:https://opengameart.org/content/upwards-floating-soul
#https://opengameart.org/content/pixel-art-2d-basic-menu-buttons
##https://opengameart.org/content/pixel-art-forest
#https://realpython.com/pygame-a-primer/
#all sprites from open game art.org
#youtube refernce:https://www.youtube.com/watch?v=3a--b-QbEcw&list=PL30AETbxgR-feEfqwQxZ-_8s0fcvMQgqJ
#For the pickle part:https://www.youtube.com/watch?v=XzkhtWYYojg
#https://opengameart.org/content/2d-lost-garden-tileset-transition-to-jetrels-wood-tileset
#https://opengameart.org/content/colored-spheres
#https://opengameart.org/content/pixel-art-2d-basic-menu-buttons
#https://opengameart.org/content/flags-0