#CSCI 4849 Project 3 - Accessible Game
#
#Dodge the Peppers!
#By Connor Guerin and Javier Ramirez
#
#Some of the code used was taken an adapted from pygames' default example "aliens.py"
#All sprites/images used in this game were created using GIMP, an open source version of Photoshop




import random, os.path, sys
import pygame
from pygame.locals import *

if not pygame.image.get_extended():
	raise SystemExit("Requires the extended image loading from SDL_image")

FRAMES_PER_SEC = 40
PLAYER_SPEED = 12
FALL_SPEED = 5
EXPLODE_TIME = 40
SCREENRECT = Rect(0, 0, 1024, 768)

dirtyrects = []
next_tick = 0
class Img: pass
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file, transparent):
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

#Classes for game objects

class Actor:
	def __init__(self, image):
		self.image = image
		self.rect = image.get_rect()
	
	def update(self):
		pass
	
	def draw(self, screen):
		r = screen.blit(self.image, self.rect)
		dirtyrects.append(r)
	
	def erase(self, screen, background):
		r = screen.blit(background, self.rect, self.rect)
		dirtyrects.append(r)


class Player(Actor):
	def __init__(self):
		Actor.__init__(self, Img.player)
		self.alive = 1
		self.reloading = 0
		self.rect.centerx = SCREENRECT.centerx
		self.rect.bottom = SCREENRECT.bottom - 10
	
	def move(self, direction):
		self.rect = self.rect.move(direction * PLAYER_SPEED, 0).clamp(SCREENRECT)


class Pepper(Actor):
	def __init__(self):
		choice = random.randint(0, 9)
		if choice < 3:
			Actor.__init__(self, Img.pepper1)
		elif choice >= 3 and choice < 7:
			Actor.__init__(self, Img.pepper2)
		else:
			Actor.__init__(self, Img.pepper3)
		
		self.rect.right = random.choice(range(SCREENRECT.left, SCREENRECT.right, 10))
	
	def update(self):
		global SCREENRECT
		self.rect[1] = self.rect[1] + FALL_SPEED

	def update(self):
		global SCREENRECT
		self.rect[1] = self.rect[1] + FALL_SPEED


class Explosion(Actor):
	def __init__(self, actor):
		Actor.__init__(self, Img.splat)

		self.life = EXPLODE_TIME
		self.rect.center = actor.rect.center
	
	def update(self):
		self.life = self.life - 1


def main():
	global dirtyrects
	global spawn_odds
	spawn_odds = 50

	pygame.init()
	screen = pygame.display.set_mode(SCREENRECT.size, 0)

	clock = pygame.time.Clock()
	level = 0

	Img.background = load_image('background.gif', 0)
	Img.pepper1 = load_image('pepper1.gif', 1)
	Img.pepper2 = load_image('pepper2.gif', 1)
	Img.pepper3 = load_image('pepper3.gif', 1)
	Img.player = load_image('player.gif', 1)
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

	screen.blit(background, (0,0))
	pygame.display.flip()

	player = Player()
	peppers = [Pepper()]
	explosions = []

	myfont = pygame.font.SysFont('Comic Sans MS', 30)
	prevTime = ""

	endWait = False


	while player.alive or explosions:

		clock.tick(FRAMES_PER_SEC)
		
		pygame.event.pump()
		keystate = pygame.key.get_pressed()
		if keystate[K_ESCAPE] or pygame.event.peek(QUIT):
			break
	   
		for actor in [player] + peppers + explosions:
			actor.erase(screen, background)
			actor.update()
		
		for e in explosions:
			if e.life <= 0:
				explosions.remove(e)

		#Clears screen so that time etc. can be re-blit
		screen.blit(background, (0,0))

		#Move the player
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


		total_seconds = pygame.time.get_ticks() // 1000

		#Adjust spawn odds based on level (i.e. time elapsed)
		if total_seconds >= 10 and level == 0:
			spawn_odds = spawn_odds - 10
			level = 1
		elif total_seconds >= 20 and level == 1:
			spawn_odds = spawn_odds - 10
			level = 2
		elif total_seconds >= 30 and level == 2:
			spawn_odds = spawn_odds - 7
			level = 3
		elif total_seconds >= 40 and level == 3:
			spawn_odds = spawn_odds - 5
			level = 4
		elif total_seconds >= 50 and level == 4:
			spawn_odds = spawn_odds - 5
			level = 5
	
		# Use python string formatting to format in leading zeros
		total_minutes = total_seconds // 60
		display_seconds = total_seconds - (60 * total_minutes)

		output_string = "Time: {0:02}:{1:02}".format(total_minutes, display_seconds)
		prevTime = output_string

		text = myfont.render(output_string, True, (0,0,0))
		levelText = myfont.render("Level " + str(level), True, (0, 0, 0))

		screen.blit(text, (10,0))
		screen.blit(levelText, (910, 0))


		#Spawn more peppers!
		if not int(random.random() * spawn_odds):
			peppers.append(Pepper())
		
		pepperRects = []
		for a in peppers:
			pepperRects.append(a.rect)
		
		#Dedect if a pepper has hit the player
		hit = player.rect.collidelist(pepperRects)
		if hit != -1:
			hitPepper = peppers[hit]
			explosions.append(Explosion(hitPepper))
			peppers.remove(hitPepper)
			player.alive = 0
			endWait = True

		for actor in [player] + peppers + explosions:
			actor.draw(screen)

		if endWait:
			looseText = myfont.render("Game Over :(", True, (0,0,0))
			screen.blit(looseText, (430,300))

		pygame.display.flip()

		pygame.display.update(dirtyrects)
		dirtyrects = []

	if endWait:
		pygame.time.wait(2300)
	else:
		pygame.time.wait(50)


if __name__ == '__main__':
	main()
