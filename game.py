#http://puu.sh/hppnD/aab9072693.msi
import pygame
import math
from pygame.locals import *
from Box2D import *

from Map import *
from Player import *

class App:	
	#player creator
	def createPlayer(self, x, y):
		body = self.world.CreateDynamicBody(position = (x, y))
		body.fixedRotation = True
		box = body.CreatePolygonFixture(box=(5,10), density=1, friction=1)
		self.player = Player(x, y, [])
		self.player.setBody(body)
		self.player.addItem(0, 100)
		self.player.addItem(1, 1)
		self.player.selectItem(0)
	
	#static tile creator
	def createStatic(self, x, y):
		return self.world.CreateStaticBody(shapes = b2EdgeShape(vertices = [(5, -5), (5, 5), (-5, 5), (-5, -5)]), position = (x, y))
		
	def __init__(self):
		self._running = True
		self._display_surf = None
		self.size = self.weight, self.height = 1600, 900
		self.PPM=20.0
		self.h_speed = 0
		self.v_speed = 0
		
	def on_init(self):
		pygame.init()
		self.world = b2World((0,75), True)
		self._display_surf = pygame.display.set_mode(self.size, 0, 32)
		self._running = True
 
	def on_event(self, event):
		if event.type == pygame.QUIT:
			self._running = False
		#add movement
		if event.type == pygame.KEYDOWN:
			print event.key
			if pygame.K_d == event.key:
				self.h_speed = 5
			elif pygame.K_a == event.key:
				self.h_speed = -5
			if pygame.K_SPACE == event.key:
				self.v_speed = -750
				
			if pygame.K_1 == event.key:
				self.player.nextSelected()
		#stop h_movement
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a or event.key == pygame.K_d:
				self.h_speed = 0
			
		#block breaking
		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			
			if self.player.getSelected() != None:
				for y in range(len(self.map.getBlocks())):
					for x in range(len(self.map.getBlocks()[y])):
						if abs(y * 10 + 20 - pos[1]) < 5 and abs(x * 10 + 5 - pos[0]) < 5:
							body = self.player.getBody()
							if abs(x * 10 + 5 - body.position.x) < 50 and abs(y * 10 + 20 - body.position.y) < 50:
								if (self.player.getSelected().getId() == 0 and self.map.getBlocks()[y][x].getTile() != 0):
									self.player.addItem(self.map.getBlocks()[y][x].getTile(), 1)
									self.map.getBlocks()[y][x].setTile(0)
									if (self.map.getBlocks()[y][x].getBody() != None):
										self.world.DestroyBody(self.map.getBlocks()[y][x].getBody())
										self.map.getBlocks()[y][x].setBody(None)
								elif self.player.getSelected().getId() != 0:
									if (self.map.getBlocks()[y][x].getBody() == None):
										self.map.getBlocks()[y][x].setTile(self.player.getSelected().getId())
										self.map.getBlocks()[y][x].setBody(self.createStatic(x * 10, y * 10))
										self.player.removeItem(self.player.getSelected().getId(), 1)
							return
									
	def on_loop(self):
		pass
		
	def on_render(self):
		self._display_surf.fill((255,255,255))
		#render blocks
		for y in range(len(self.map.getBlocks())):
			for x in range(len(self.map.getBlocks()[y])):
				block = self.map.getBlocks()[y][x]
				blockX = block.getX()
				blockY = block.getY()
				color = (255, 255, 255)
				if block.getTile() == 1:
					color = color = (255, 0, 255)
				if block.getTile() == 2:
					color = color = (0, 0, 255)
				pygame.draw.rect(self._display_surf, color, (blockX * 10, blockY * 10 + 15, 10, 10))
			
		i = 0
		for item in self.player.getItems():
			if self.player.getSelected() != None and self.player.getSelected().getId() == item.getId():
				pygame.draw.rect(self._display_surf, (125, 225, 125), [10 + i * 25 + 5, 10, 25, 25])
			else:
				pygame.draw.rect(self._display_surf, (225, 225, 225), [10 + i * 25 + 5, 10, 25, 25])
			pygame.draw.rect(self._display_surf, (0, 0, 0), [10 + i * 25 + 5, 10, 25, 25], 2)
			color = (255, 255, 255)
			if item.getId() == 1:
				color = color = (255, 0, 255)
			if item.getId() == 2:
				color = color = (0, 0, 255)
			pygame.draw.rect(self._display_surf, color, [10 + i * 25 + 10, 10 + 5, 15, 15])
			i += 1
		#render player		
		body = self.player.getBody()
		pygame.draw.rect(self._display_surf, (125, 125, 125), (body.position.x, body.position.y, 10, 20))
		vel = body.linearVelocity
		vel.x += self.h_speed
		if abs(body.linearVelocity.y) < .5:
			vel.y += self.v_speed	
			body.linearVelocity = vel
		self.v_speed = 0
		
		pygame.display.flip()
	def on_cleanup(self):
		pygame.quit()

	def on_execute(self):
		if self.on_init() == False:
			self._running = False
		self.clock = pygame.time.Clock()
		#generate map and create player
		self.map = Map("test")
		self.map.generate(200, 75)
		self.boxes = []
		self.createPlayer(100, 100)
		
		print self.player.getSelected()
		print self.player.getItems()
		
		#add static bodies to map
		for y in range(len(self.map.getBlocks())):
			for x in range(len(self.map.getBlocks()[y])):
				block = self.map.getBlocks()[y][x]
				if int(block.getTile()) != 0:
					#print "Creating static", block.getTile()
					block.setBody(self.createStatic(x * 10, y * 10))
					#print "Static created"				
		timeStep = 1.0 / 30
		vel_iters, pos_iters = 1, 1
		
		#while out game is playing
		while( self._running ):
			self.clock.tick(60)
			#step physics
			self.world.Step(timeStep, vel_iters, pos_iters)
			#clear forces on objects
			self.world.ClearForces()
			
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

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)