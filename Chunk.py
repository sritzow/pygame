class Chunk:	
	def __init__(self, x, y, blocks = None):
		self.x = x
		self.y = y
		self.blocks = blocks
	
	def getBlock(self, x, y):
		return self.blocks[y][x]
	def getX(self):
		return self.x
	def getY(self):
		return self.y
	def getBlocks(self):
		return self.blocks