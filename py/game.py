import pygame, random, sys, time

def ini():
    err = pygame.init()
    if err[1] == 0:
        print('Hello')
    else:
        print('Errors detected')
        sys.exit()
    

ini()

playSurface = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Pythonчик')
time.sleep(1)
position = [50, 50]
body = [[80, 50], [70, 50], [60, 50]]
bait = [random.randrange(1, 80)*10, random.randrange(1, 60)*10]
baitVisible = True
fpsController = pygame.time.Clock()
direction = 'RIGHT'
changeto = direction
score = 0

white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
lightslateblue = pygame.Color(132, 112, 255)

def music():
    pygame.mixer.init()
    pygame.mixer.music.load('riff.mp3')
    pygame.mixer.music.play(loops = -1)
    

def gameOver():
    gaOFont = pygame.font.SysFont('Garamond', 48)
    gaOSurface = gaOFont.render('Game Over!', True, red)
    gaORectangular = gaOSurface.get_rect()
    gaORectangular.midtop = (400, 25)
    playSurface.blit(gaOSurface, gaORectangular)
    pygame.display.flip()
    showScore()
    time.sleep(3)
    pygame.quit()
    sys.exit()
    
def showScore(choice=1):
    scoreFont = pygame.font.SysFont('Garamond', 24)
    scoreSurface = scoreFont.render('Score: {0}'.format(score), True, red)
    scoreRectangular = scoreSurface.get_rect()
    if choice == 1:
        scoreRectangular.midtop = (50, 25)
    else:
        scoreRectangular.midtop = (400, 125)
    playSurface.blit(scoreSurface, scoreRectangular)
    #pygame.display.flip()
    


while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                changeto = 'RIGHT'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                changeto = 'LEFT'
            if event.key == pygame.K_UP or event.key == ord('w'):
                changeto = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                changeto = 'DOWN'
            if event.key == pygame.K_ESCAPE:
                gameOver()
                
            if event.key == ord('p'):
                music()
            if event.key == ord('m'):              
                pygame.mixer.music.stop()    
            
    if direction != 'LEFT' and changeto == 'RIGHT':
        direction = 'RIGHT'
    if direction != 'RIGHT' and changeto == 'LEFT':
        direction = 'LEFT'
    if direction != 'DOWN' and changeto == 'UP':
        direction = 'UP'
    if direction != 'UP' and changeto == 'DOWN':
        direction = 'DOWN'               
            
    if direction == 'RIGHT':
        position[0] += 10
    if direction == 'LEFT':
        position[0] -= 10    
    if direction == 'UP':
        position[1] -= 10
    if direction == 'DOWN':
        position[1] += 10    
            
    body.insert(0, list(position))
    if position[0] == bait[0] and position[1] == bait[1]:
        baitVisible = False
        score += 1
    else:
        body.pop()
        
    if baitVisible == False:
        baitVisible = True
        bait = [random.randrange(1, 80)*10, random.randrange(1, 60)*10]
        
    playSurface.fill(white)
    #pygame.display.flip()
        
    for element in body:
        pygame.draw.rect(playSurface, green, pygame.Rect(element[0], element[1], 10, 10))
        
    pygame.draw.rect(playSurface, blue, pygame.Rect(bait[0], bait[1], 10, 10))
        
    if position[0] > 790 or position[0] < 0:
        position[0] = 400
    if position[1] > 590 or position[1] < 0:
        position[1] = 300   
        
    for element in body[1: ]:
        if position[0] == element[0] and position[1] == element[1]:
            position = [50, 50]
            body = [[80, 50], [70, 50], [60, 50]]
        
    showScore()
    pygame.display.flip()
    fpsController.tick(4)
        
        
