from abc import ABC, abstractmethod

class Brain:
	'''
	Interface that a player needs to implement in order to play the game.
	'''
	def __init__(self, numberOfActions, creatureStatsShape, worldViewShape):
		pass


	@abstractmethod 
	def getId(self):
		pass


	@abstractmethod 
	def birth(self, creatureStats, worldViewOfCreature, parentBrain):
		pass
	    

	@abstractmethod
	def act(self,creatureStats,worldView):
		pass


	@abstractmethod
	def death(self, creatureStats, worldViewOfCreature, score):
		pass

	@abstractmethod
	def brightness(self):
		pass