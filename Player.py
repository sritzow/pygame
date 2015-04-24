from Item import *
class Player:
	def __init__(self, x, y, inv = None):
		self.x = x
		self.y = y
		self.inv = inv
		self.body = None
		self.selected = None
		
	def getX():
		return self.x
	def getY():
		return self.y
	def getItems(self):
		return self.inv
		
	def setBody(self, body):
		self.body = body
	def getBody(self):
		return self.body
		
	def nextSelected(self):
		new = False
		for i in range(len(self.inv)):
			if self.inv[i] == self.selected:
				if len(self.inv) - 1 > i:
					self.selected = self.inv[i + 1]
					new = True
					break
					
		if not new:
			self.selected = self.inv[0]
		print "New selected item", self.selected.getId(), self.selected.getCount()
	def getSelected(self):
		return self.selected
	def selectItem(self, id):
		for item in self.inv:
			if item.getId() == id:
				self.selected = item
				return True
		self.selected = None
	def hasItem(self, id, count):
		for item in self.inv:
			if item.getId() == id:
				return item.count >= count
		return False
	def addItem(self, id, count):
		for item in self.inv:
			if item.getId() == id:
				item.count += count
				return
		self.inv.append(Item(id, count))
	def removeItem(self, id, count):
		for item in self.inv:
			if item.getId() == id:
				if (item.count - count > 0):
					item.count -= count
					return True
				else:
					self.inv.remove(item)
					self.selected = None
					return True
		return False