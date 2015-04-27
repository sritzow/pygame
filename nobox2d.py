import pygame
from pygame import *
import math
from pygame.locals import *


WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30
class Camera(object):
	def __init__(self, camera_func, width, height):
		self.camera_func = camera_func
		self.state = Rect(0, 0, width, height)

	def apply(self, target):
		return target.rect.move(self.state.topleft)

	def update(self, target):
		self.state = self.camera_func(self.state, target.rect)
		
def simple_camera(camera, target_rect):
	l, t, _, _ = target_rect
	_, _, w, h = camera
	return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
	l, t, _, _ = target_rect
	_, _, w, h = camera
	l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

	l = min(0, l)						   # stop scrolling at the left edge
	l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
	t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
	t = min(0, t)						   # stop scrolling at the top
	return Rect(l, t, w, h)
	
class Entity(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

class Player(Entity):
	def __init__(self, x, y):
		Entity.__init__(self)
		self.xvel = 0
		self.yvel = 0
		self.onGround = False
		self.image = Surface((16,32))
		self.image.fill(Color("#0000FF"))
		self.image.convert()
		self.rect = Rect(x, y, 16, 32)

	def update(self, up, down, left, right, running, platforms):
		if up:
			# only jump if on the ground
			if self.onGround: self.yvel -= 10
		if down:
			pass
		if running:
			self.xvel = 12
		if left:
			self.xvel = -8
		if right:
			self.xvel = 8
		if not self.onGround:
			# only accelerate with gravity if in the air
			self.yvel += 0.3
			# max falling speed
			if self.yvel > 100: self.yvel = 100
		if not(left or right):
			self.xvel = 0
		# increment in x direction
		self.rect.left += self.xvel
		# do x-axis collisions
		self.collide(self.xvel, 0, platforms)
		# increment in y direction
		self.rect.top += self.yvel
		# assuming we're in the air
		self.onGround = False;
		# do y-axis collisions
		self.collide(0, self.yvel, platforms)

	def collide(self, xvel, yvel, platforms):
		for p in platforms:
			if pygame.sprite.collide_rect(self, p):
				if isinstance(p, ExitBlock):
					pygame.event.post(pygame.event.Event(QUIT))
				if xvel > 0:
					self.rect.right = p.rect.left
					print "collide right"
				if xvel < 0:
					self.rect.left = p.rect.right
					print "collide left"
				if yvel > 0:
					print "collide bottom"
					self.rect.bottom = p.rect.top
					self.onGround = True
					self.yvel = 0
				if yvel < 0:
					print "collide top"
					self.rect.top = p.rect.bottom


class Platform(Entity):
	def __init__(self, x, y, type):
		Entity.__init__(self)
		self.image = Surface((32, 32))
		self.image.convert()
		if type == 1:
			self.image.fill(Color("#009911"))
		elif type == 2:
			self.image.fill(Color("#954354"))
		else:
			self.image.fill(Color("#564355"))
		self.rect = Rect(x, y, 32, 32)
		self.type = type
		
	def update(self):
		pass

class ExitBlock(Platform):
	def __init__(self, x, y):
		Platform.__init__(self, x, y)
		self.image.fill(Color("#0033FF"))

class App:		
	def __init__(self):
		self._running = True
		self._display_surf = None
		self.size = self.weight, self.height = 1600, 900

	def on_init(self):
		global cameraX, cameraY
		pygame.init()
		
		self._running = True
		
		self.up = self.down = self.left = self.right = self.running = False
		self.screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
		self.timer = pygame.time.Clock()
		self.bg = Surface((32,32))
		self.bg.convert()
		self.bg.fill(Color("#000000"))
		self.entities = pygame.sprite.Group()
		self.player = Player(32, 32)
		self.platforms = []
		
		self.x = self.y = 0
		self.total_level_width  = 100 * 32
		self.total_level_height = 75 * 32
		
		for y in range(100):
			for x in range(75):
				if y < 48:
					p = Platform(x * 32, y * 32, 0)
				elif y < 64:
					p = Platform(x * 32, y * 32, 1)
					self.platforms.append(p)
				else:
					p = Platform(x * 32, y * 32, 2)
					self.platforms.append(p)
				self.entities.add(p)
				
		self.camera = Camera(complex_camera, self.total_level_width, self.total_level_height)
		self.entities.add(self.player)
					
		
	def on_event(self, e):
		pass
									
	def on_loop(self):
		pass
		
	def on_render(self):
		for y in range(100):
			for x in range(75):
				self.screen.blit(self.bg, (x * 32, y * 32))
		
		for e in pygame.event.get():
			if e.type == QUIT: 
				raise SystemExit, "QUIT"
			if e.type == KEYDOWN and e.key == K_ESCAPE:
				raise SystemExit, "ESCAPE"
			if e.type == KEYDOWN and e.key == K_UP:
				up = True
			if e.type == KEYDOWN and e.key == K_DOWN:
				down = True
			if e.type == KEYDOWN and e.key == K_LEFT:
				left = True
			if e.type == KEYDOWN and e.key == K_RIGHT:
				right = True
			if e.type == KEYDOWN and e.key == K_SPACE:
				running = True

			if e.type == KEYUP and e.key == K_UP:
				up = False
			if e.type == KEYUP and e.key == K_DOWN:
				down = False
			if e.type == KEYUP and e.key == K_RIGHT:
				right = False
			if e.type == KEYUP and e.key == K_LEFT:
				left = False
				
		self.camera.update(self.player)
		
		self.player.update(self.up, self.down, self.left, self.right, self.running, self.platforms)
		
		for e in self.entities:
			#print "Blit:", e.rect
			self.screen.blit(e.image, self.camera.apply(e))
			
		pygame.display.update()
	def on_cleanup(self):
		pygame.quit()

	def on_execute(self):
		if self.on_init() == False:
			self._running = False
			
		self.timer = pygame.time.Clock()
		while( self._running ):
			self.timer.tick(60)
			
			#loop through keyboard/mouse events
			for event in pygame.event.get():
				self.on_event(event)
				
			#game loop
			self.on_loop()
			
			#render objects
			self.on_render()
		self.on_cleanup()
 
if __name__ == "__main__" :
	theApp = App()
	theApp.on_execute()