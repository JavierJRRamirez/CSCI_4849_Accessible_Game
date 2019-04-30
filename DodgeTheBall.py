#!/usr/bin/env python

"""This is a much simpler version of the aliens.py
	example. It makes a good place for beginners to get
	used to the way pygame works. Gameplay is pretty similar,
	but there are a lot less object types to worry about,
	and it makes no attempt at using the optional pygame
	modules.
	It does provide a good method for using the updaterects
	to only update the changed parts of the screen, instead of
	the entire screen surface. This has large speed benefits
	and should be used whenever the fullscreen isn't being changed."""


#import
import random, os.path, sys
import pygame
from pygame.locals import *

if not pygame.image.get_extended():
	raise SystemExit("Requires the extended image loading from SDL_image")


#constants
FRAMES_PER_SEC = 40
PLAYER_SPEED = 12
MAX_SHOTS = 2
#SHOT_SPEED     = 10
ALIEN_SPEED = 5

EXPLODE_TIME = 6
SCREENRECT = Rect(0, 0, 1024, 768)


#some globals for friendly access
dirtyrects = [] # list of update_rects
next_tick = 0   # used for timing
class Img: pass # container for images
main_dir = os.path.split(os.path.abspath(__file__))[0]  # Program's diretory


#first, we define some utility functions

def load_image(file, transparent):
	"loads an image, prepares it for play"
	file = os.path.join(main_dir, 'data', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit('Could not load image "%s" %s' %
						 (file, pygame.get_error()))
	if transparent:
		corner = surface.get_at((0, 0))
		surface.set_colorkey(corner, RLEACCEL)
	return surface.convert()



# The logic for all the different sprite types

class Actor:
	"An enhanced sort of sprite class"
	def __init__(self, image):
		self.image = image
		self.rect = image.get_rect()
	
	def update(self):
		"update the sprite state for this frame"
		pass
	
	def draw(self, screen):
		"draws the sprite into the screen"
		r = screen.blit(self.image, self.rect)
		dirtyrects.append(r)
	
	def erase(self, screen, background):
		"gets the sprite off of the screen"
		r = screen.blit(background, self.rect, self.rect)
		dirtyrects.append(r)


class Player(Actor):
	"Cheer for our hero"
	def __init__(self):
		Actor.__init__(self, Img.player)
		self.alive = 1
		self.reloading = 0
		self.rect.centerx = SCREENRECT.centerx
		self.rect.bottom = SCREENRECT.bottom - 10
	
	def move(self, direction):
		self.rect = self.rect.move(direction*PLAYER_SPEED, 0).clamp(SCREENRECT)


class Alien(Actor):
	"Destroy him or suffer"
	def __init__(self):
		choice = random.randint(0, 9)
		if choice < 3:
			Actor.__init__(self, Img.alien)
		elif choice >= 3 and choice < 7:
			Actor.__init__(self, Img.alien2)
		else:
			Actor.__init__(self, Img.alien3)
		#self.facing = random.choice((-1,1)) * ALIEN_SPEED
		
		self.rect.right = random.choice(range(SCREENRECT.left, SCREENRECT.right, 10))
	
	def update(self):
		global SCREENRECT
		self.rect[1] = self.rect[1] + ALIEN_SPEED
# if not SCREENRECT.contains(self.rect):
#     self.facing = -self.facing;
#     self.rect.top = self.rect.bottom + 3
#     self.rect = self.rect.clamp(SCREENRECT)
			
	def update(self):
		global SCREENRECT
		self.rect[1] = self.rect[1] + ALIEN_SPEED
		# if not SCREENRECT.contains(self.rect):
		#     self.facing = -self.facing;
		#     self.rect.top = self.rect.bottom + 3
		#     self.rect = self.rect.clamp(SCREENRECT)


class Explosion(Actor):
	"Beware the fury"
	def __init__(self, actor):
		Actor.__init__(self, Img.splat)

		self.life = EXPLODE_TIME
		self.rect.center = actor.rect.center
	
	def update(self):
		self.life = self.life - 1


#class Shot(Actor):
#    "The big payload"
#    def __init__(self, player):
#        Actor.__init__(self, Img.shot)
#        self.rect.centerx = player.rect.centerx
#        self.rect.top = player.rect.top - 10
#
#    def update(self):
#        self.rect.top = self.rect.top - SHOT_SPEED




def main():
	"Run me for adrenaline"
	global dirtyrects
	global alien_odds
	alien_odds = 50
	# Initialize SDL components
	pygame.init()
	screen = pygame.display.set_mode(SCREENRECT.size, 0)

	clock = pygame.time.Clock()

	level = 0

	# Load the Resources
	Img.background = load_image('background.gif', 0)
	Img.shot = load_image('shot.gif', 1)
	Img.bomb = load_image('bomb.gif', 1)
	Img.danger = load_image('danger.gif', 1)
	Img.alien = load_image('alien1.gif', 1)
	Img.alien2 = load_image('alien2.gif', 1)
	Img.alien3 = load_image('alien3.gif', 1)
	Img.player = load_image('oldplayer.gif', 1)
	Img.splat = load_image('splat.gif', 1)
	Img.leftButton = load_image('leftButton.gif', 1)
	Img.rightButton = load_image('rightButton.gif', 1)
	Img.divider = load_image('divider.gif', 1)
	
	#Apparently the only way to fill the screen properly is to do it in sections!?
	background = pygame.Surface(SCREENRECT.size)
	for x in range(0, SCREENRECT.width, Img.background.get_width()):
		background.blit(Img.background, (x, 0))

	background.blit(Img.divider, (329, 0))
	background.blit(Img.divider, (670, 0))


	#screen.fill(pygame.Color("white"))
	#background.blit(Img.markedBackground, (0, 0))
	screen.blit(background, (0,0))
	pygame.display.flip()

# Initialize Game Actors
	player = Player()
	aliens = [Alien()]
#    shots = []
	explosions = []

	myfont = pygame.font.SysFont('Comic Sans MS', 30)
	prevTime = ""

	endWait = False

	# Main loop
	while player.alive or explosions:

		clock.tick(FRAMES_PER_SEC)
		
		# Gather Events
		pygame.event.pump()
		keystate = pygame.key.get_pressed()
		if keystate[K_ESCAPE] or pygame.event.peek(QUIT):
			break
	   

		# Clear screen and update actors
		for actor in [player] + aliens + explosions:
			actor.erase(screen, background)
			actor.update()
		
		# Clean Dead Explosions and Bullets
		for e in explosions:
			if e.life <= 0:
				explosions.remove(e)
#        for s in shots:
#            if s.rect.top <= 0:
#                shots.remove(s)

		#screen.fill(pygame.Color("white")) #Clears screen so that time etc. can be re-blit
		screen.blit(background, (0,0))

		# Move the player
		mousex, mousey = pygame.mouse.get_pos()
		direction = 0
		if mousex < SCREENRECT.width // 3:
			direction = -1
		elif mousex > (SCREENRECT.width // 3) * 2:
			direction = 1
		else:
			direction = 0

		player.move(direction)

		if direction == -1:
			screen.blit(Img.leftButton, (0, 0))
		elif direction == 1:
			screen.blit(Img.rightButton, (666, 0))

		# leftRect = Img.leftButton.get_rect()
		# screen.blit(Img.leftButton, (0, 0))

		# pygame.display.flip()
			# dirtyrects.append(r)


		total_seconds = pygame.time.get_ticks() // 1000

		if total_seconds >= 10 and level == 0:
			alien_odds = alien_odds - 5
			level = 1
		elif total_seconds >= 20 and level == 1:
			alien_odds = alien_odds - 5
			level = 2
		elif total_seconds >= 30 and level == 2:
			alien_odds = alien_odds - 5
			level = 3
		elif total_seconds >= 40 and level == 3:
			alien_odds = alien_odds - 10
			level = 4
		elif total_seconds >= 50 and level == 4:
			alien_odds = alien_odds - 10
			level = 5

	
		# Divide by 60 to get total minutes
		minutes = total_seconds // 60
	
		# Use modulus (remainder) to get seconds
		seconds = total_seconds % 60
	
		# Use python string formatting to format in leading zeros
		output_string = "Time: {0:02}:{1:02}".format(minutes, seconds)
		prevTime = output_string

		# screen.fill(pygame.Color("white")) #Clears screen so that time can be re-blit

		text = myfont.render(output_string, True, (0,0,0))
		levelText = myfont.render("Level " + str(level), True, (0, 0, 0))
		screen.blit(text, (10,0))
		screen.blit(levelText, (910, 0))
		# total_seconds = start_time - (frame_count // frame_rate)
		# if total_seconds < 0:
		#     total_seconds = 0
		# frame_count += 1
		# clock.tick(frame_rate)
	

	   


		# direction = keystate[K_RIGHT] - keystate[K_LEFT]

		# player.move(direction)
			# direction = -1
		# elif mousex > 682:
		#	direction = 1
		# else:
		#	direction = 0
#        player.move(direction)
#            direction = -1
#        elif mousex > 682:
#            direction = 1
#        else:
#            direction = 0


		# direction = keystate[K_RIGHT] - keystate[K_LEFT]
		
		
		# Create new shots
#        if not player.reloading and keystate[K_SPACE] and len(shots) < MAX_SHOTS:
#            shots.append(Shot(player))
#        player.reloading = keystate[K_SPACE]

		# Create new alien
		if not int(random.random() * alien_odds):
			aliens.append(Alien())
		
		# Detect collisions
		alienrects = []
		for a in aliens:
			alienrects.append(a.rect)
		
		hit = player.rect.collidelist(alienrects)
		if hit != -1:
			alien = aliens[hit]
			explosions.append(Explosion(alien))
			# explosions.append(Explosion(player))
			aliens.remove(alien)
			player.alive = 0
			
			
			endWait = True
#        for shot in shots:
#            hit = shot.rect.collidelist(alienrects)
#            if hit != -1:
#                alien = aliens[hit]
#                explosions.append(Explosion(alien))
#                shots.remove(shot)
#                aliens.remove(alien)
#                break

		# Draw everybody
		for actor in [player] + aliens + explosions:
			actor.draw(screen)

		if endWait:
			# screen.blit(background, (0,0))
			looseText = myfont.render("Game Over :(", True, (0,0,0))
			screen.blit(looseText, (430,300))

		pygame.display.flip()

		pygame.display.update(dirtyrects)
		dirtyrects = []

	if endWait:
		pygame.time.wait(2300)
	else:
		pygame.time.wait(50)



#if python says run, let's run!
if __name__ == '__main__':
	main()
