import json
from Block import *
from Chunk import *

class Map:
	def load(self, name):
		json_data = open(str(name) + ".json").read()
		data = json.loads(json_data)
		self.chunks = []
		for c in range(len(data)):
			chunk_string = "chunk" + str(c + 1)
			print "Loading chunk data:", c, "X:", data[chunk_string]["x"], "Y:", data[chunk_string]["y"]
			newChunk = []
			for y in range(len(data[chunk_string]["blocks"])):
				yChunk = []
				for x in range(len(data[chunk_string]["blocks"][y])):
					newBlock = Block(data[chunk_string]["blocks"][y][x], x, y)
					yChunk.append(newBlock)
				newChunk.append(yChunk)
			self.chunks.append(Chunk(data[chunk_string]["y"], data[chunk_string]["x"], newChunk))
			
	def __init__(self, name):
		self.name = name
		print "Map created"
		print str(name) + ".json"
	def getBlock(self, x, y):
		return self.blocks[y][x]
		
	def getBlocks(self):
		return self.blocks
		
	def generate(self,  blockX, blockY):
		self.blocks = []
		for y in range(blockY):
			blocks = []
			for x in range(blockX):
				if y > 48 and y < 64:
					blocks.append(Block(1, x, y))
				elif y >= 64:
					blocks.append(Block(1, x, y))
				else:
					blocks.append(Block(0, x, y))
			self.blocks.append(blocks)
			
		
	