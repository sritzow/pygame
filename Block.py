class Block:
	def __init__(self, tile, x, y):
		self.tile = tile
		self.x = x
		self.y = y
		self.body = None
		
	def setBody(self, body):
		self.body = body
	def getBody(self):
		return self.body
	def setTile(self, t):
		self.tile = t
	def getTile(self):
		return self.tile
	def getX(self):
		return self.x
	def getY(self):
		return self.y