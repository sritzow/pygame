import math
from math import *
import pygame
from pygame import *

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30
background = pygame.image.load('background.png')
background = pygame.transform.scale(background, (WIN_WIDTH, WIN_HEIGHT))
bg2 = pygame.image.load('bg2.gif')
bg2 = pygame.transform.scale(bg2, (WIN_WIDTH, WIN_HEIGHT))

tile_image = [pygame.image.load('tile1.jpg'), pygame.image.load('tile1.jpg')]

class Camera(object):
	def __init__(self, camera_func, width, height):
		self.camera_func = camera_func
		self.state = Rect(0, 0, width, height)

	def applyPoint(self, target):
		return target + (self.state.topleft.x, self.stat.topleft.y)
		
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
		
class Item:
	def __init__(self, id, count, pic):
		self.id = id
		self.count = count
		self.pic = pic
		if id > 0:
			self.isBlock = True
		else:
			self.isBlock = False
		
	def add(self, count):
		self.count += count
		
	def remove(self, count):
		self.count -= count

class Player(Entity):
	def selectNext(self):
		next = False
		if self.selectedItem != None:
			print "Current: ", self.selectedItem.id
			for item in self.inventory:
				if next:
					print "New1: ", item.id
					self.selectedItem = item
					return
				if item.id == self.selectedItem.id:
					next = True
				
		for item in self.inventory:
			self.selectedItem = item
			print "New: ", item.id
			return
			
	def select(self, num):
		i = 0
		for item in self.inventory:
			if i == num:
				self.selectedItem = item
				return
			i += 1
		
	def removeItem(self, id, count):
		item = self.getItem(id)
		if item.count > count:
			item.remove(count)
		elif item.count == count:
			self.inventory.remove(item)
			self.selectedItem = None
		
	def getItem(self, id):
		for item in self.inventory:
			if item.id == id:
				return item
		return None
		
	def hasItem(self, id):
		for item in self.inventory:
			if item.id == id:
				return item.count
		return 0	
		
	def addItem(self, id, count):
		if self.hasItem(id) == 0:
			if id == 4:
				pic = pygame.image.load('tile' + str(id) + '_closed.jpg')
			else:
				pic = pygame.image.load('tile' + str(id) + '.jpg')
			pic = pygame.transform.scale(pic, (25, 25))
			self.inventory.append(Item(id, count, pic))
		else:
			item = self.getItem(id)
			item.add(count)
			
	def __init__(self, x, y):
		Entity.__init__(self)
		self.xvel = 0
		self.yvel = 0
		self.onGround = False
		self.image = Surface((16,32))
		self.image.fill(Color("#0000FF"))
		self.image.convert()
		self.rect = Rect(x, y, 16, 32)
		self.inventory = []
		self.selectedItem = None
		self.addItem(0, 1)
		self.addItem(4, 1)
		self.addItem(5, 5)
		self.selectNext()

	def update(self, up, down, left, right, running, climb, platforms):
		onLadder = False
		for p in platforms:
			if p.type == 5:
				if pygame.sprite.collide_rect(self, p):
					onLadder = True
					
		if climb and onLadder:
			self.yvel = -4
		elif onLadder:
			self.yvel = 0
		if up:
			# only jump if on the ground
			if self.onGround: self.yvel -= 6
		if down:
			if not self.onGround:
				self.yvel =+ 4
		if left:
			self.xvel = -4
		if right:
			self.xvel = 4
		if not self.onGround:
			# only accelerate with gravity if in the air
			if not onLadder:
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
				if p.type != 5:
					if xvel > 0:
						self.rect.right = p.rect.left
						print "collide right"
					if xvel < 0:
						self.rect.left = p.rect.right
						print "collide left"
					if yvel > 0:
						if p.type != 5:
							self.rect.bottom = p.rect.top
						self.onGround = True
						self.yvel = 0
					if yvel < 0:
						if p.type != 5:
							self.rect.top = p.rect.bottom
						self.yvel = 0


class Platform(Entity):
	def __init__(self, x, y, type):
		Entity.__init__(self)
		self.image = None
		self.canBreak = True
		self.closed = False
		if type == 99:
			self.canBreak = False
		if type != -1:
			self.image = Surface((32, 32))
			self.image.convert()
		if type == -1:
			pass
		elif type == 4:
			self.closed = True
			self.image = pygame.image.load('tile' + str(type) + '_closed.jpg')
		else:
			self.image = pygame.image.load('tile' + str(type) + '.jpg')
		self.rect = Rect(x, y, 32, 32)
		self.type = type

	def update(self, type):
		if type != -1:
			self.image = Surface((32, 32))
			self.image.convert()
		if type == -1:
			self.image = None
		elif type == 4:
			self.image = pygame.image.load('tile' + str(type) + '_closed.jpg')
		else:
			self.image = pygame.image.load('tile' + str(type) + '.jpg')
		self.type = type
		
	def switch(self):
		print "SWITCH:", self.closed
		if self.closed:
			self.image = pygame.image.load('tile' + str(self.type) + '_closed.jpg')
			self.closed = False
		else:
			self.image = pygame.image.load('tile' + str(self.type) + '_open.jpg')
			self.closed = True
		
def main():
	global cameraX, cameraY
	pygame.init()
	screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
	pygame.display.set_caption("Ayy Lmao")
	timer = pygame.time.Clock()

	up = down = left = right = running = climb = False
	bg = Surface((32,32))
	bg.convert()
	bg.fill(Color("#000000"))
	entities = pygame.sprite.Group()
	player = Player(750, 32)
	platforms = []

	x = y = 0

	# build the level
	ySize = 100
	xSize = 100
	for y in range(ySize):
		for x in range(xSize):
			if y == 0 or x == 0 or y == 99 or x == 99:
				p = Platform(x * 32, y * 32, 99)
				platforms.append(p)
				entities.add(p)
			elif y > 48 and y < 64:
				p = Platform(x * 32, y * 32, 1)
				platforms.append(p)
				entities.add(p)
			elif y >= 64:
				p = Platform(x * 32, y * 32, 2)
				platforms.append(p)
				entities.add(p)
			else:
				entities.add(Platform(x * 32, y * 32, -1))
				
	total_level_width  = xSize * 32
	total_level_height = ySize * 32
	camera = Camera(complex_camera, total_level_width, total_level_height)
	entities.add(player)

	while 1:
		timer.tick(60)

		for e in pygame.event.get():
			if e.type == QUIT: raise SystemExit, "QUIT"
			if e.type == KEYDOWN and e.key == K_ESCAPE:
				raise SystemExit, "ESCAPE"
			if e.type == KEYDOWN and e.key == K_SPACE:
				up = True
			if e.type == KEYDOWN and e.key == K_w:
				climb = True
			if e.type == KEYDOWN and e.key == K_s:
				down = True
			if e.type == KEYDOWN and e.key == K_a:
				left = True
			if e.type == KEYDOWN and e.key == K_d:
				right = True
			if e.type == KEYDOWN and e.key == K_TAB:
				print player.inventory
				player.selectNext()

			if e.type == KEYUP and e.key == K_SPACE:
				up = False
			if e.type == KEYUP and e.key == K_w:
				climb = False
			if e.type == KEYUP and e.key == K_s:
				down = False
			if e.type == KEYUP and e.key == K_d:
				right = False
			if e.type == KEYUP and e.key == K_a:
				left = False
				
			if e.type == MOUSEBUTTONDOWN:
				#for ent in self.entities:
				pos = pygame.mouse.get_pos()
				pos = (abs(camera.state.left) + pos[0], abs(camera.state.top) + pos[1])
				print pos
				
				for ent in entities:
					if ent.rect.collidepoint(pos[0], pos[1]):
						if (abs(player.rect.left - ent.rect.left) <= 96 and abs(player.rect.top - ent.rect.top) <= 96):
							if ent != player:
								if e.button == 1:
									if player.selectedItem != None:
										if ent.type == -1:
											if player.selectedItem.isBlock:
												ent.update(player.selectedItem.id)
												#if player.selectedItem.id != 5:
												platforms.append(ent)
												player.removeItem(player.selectedItem.id, 1)
										elif ent.canBreak:
											if not player.selectedItem.isBlock:
												player.addItem(ent.type, 1)
												ent.update(-1)
												platforms.remove(ent)
								else:
									if ent.type == 4:
										if ent in platforms:
											platforms.remove(ent)
											ent.switch()
										else:
											platforms.append(ent)
											ent.switch()
						break

		# draw background
		screen.blit(bg2, [0, 0, WIN_WIDTH, WIN_HEIGHT])		
		
		camera.update(player)

		# update player, draw everything else
		player.update(up, down, left, right, running, climb, platforms)
		for e in entities:
			if e.image != None and e != player:
				screen.blit(e.image, camera.apply(e))
				
		screen.blit(player.image, camera.apply(player))
		
		for x in range(10):
			pygame.draw.rect(screen, (0, 0, 0), (25 + x * 40, 25, 35, 35), 2)
			i = 0
			for item in player.inventory:
				if i == x:
					if player.selectedItem == item:	
						pygame.draw.rect(screen, (255, 255, 0), (25 + x * 40, 25, 35, 35))
					else:
						pygame.draw.rect(screen, (225, 225, 225), (25 + x * 40, 25, 35, 35))
					#pygame.draw.rect(screen, item.color, (25 + 5 + x * 40, 30, 25, 25))
					screen.blit(item.pic, (25 + 5 + x * 40, 30, 25, 25))
					font = pygame.font.Font(None, 24)
					text = font.render(str(item.count), 1, (10, 10, 10))
					textpos = text.get_rect()
					textpos.centerx = (25 + 10 + x * 40)
					textpos.centery = (35)
					screen.blit(text, textpos)
				i += 1
				
		pygame.display.update()

if __name__ == "__main__":
	main()