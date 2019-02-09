import numpy as np
import brain
import creature
import worldmap
import zoo
import random
import sys
import os
import copy

#Dynamically loading all brain implementations:
def loadBrains():
    brainDirectory = "brains"
    fileList = [f for f in os.listdir(brainDirectory) if (
        os.path.isfile(os.path.join(brainDirectory, f) ) and ( os.path.splitext(f)[1] == ".py" ))]

    for f in fileList:
        print(f)
        moduleName = os.path.splitext(f)[0]
        __import__(brainDirectory+"."+moduleName, fromlist=[''])


loadBrains()

#There should be spawn method that creates new creatures to the map for every player class

class Game:

	def __init__(self, mapsize = (100,100), tilesize = (5,5), waterlevel = 0.1):

		#Creating game map
		self.worldmap = worldmap.Map(mapsize,tilesize, waterlevel)
		self.creatures = []
		self.zoo = zoo.Zoo()

		# all the brain subclasses
		self.brains = brain.Brain.__subclasses__() # all the brain subclasses
		self.numberOfBrains = len(self.brains)

		self.hueValues()

		#current number of alive creatures on the map
		self.noOfCreatures = 0

		#minimum necessary number of alive creatures on the map
		self.lowerNoOfCreatures = 1

		#max number of creatures that each brain class can have at the beginning of each round
		self.upperNoOfCreatures = 10

		self.highScoreCreatures = {}
		self.highScoreThreshold = 0
		self.keepTopK = 10


	#Giving a random color to all different brain implementations
	def hueValues(self):

		self.brainHueValues = {}
		#this line allows brains to have hue values distributed over the color values.
		hueArray = np.linspace( 0, 1.0, num = self.numberOfBrains, endpoint = False )
		i = 0

		for brain in self.brains:

			self.brainHueValues[brain.__name__] = hueArray[i]
			i += 1


	def spawnCreatures(self):

		if self.noOfCreatures < self.lowerNoOfCreatures:
			for brain in self.brains:
						print(brain.__name__, ' ' , brain.teamScore)

			#if there is no creature on the map, this means another new round is beginning, 99x vegatation growth
			self.worldmap.resetVegetation()

			#for every player
			for brain in self.brains:

				# there will be upperNoOfCreatures of creatures for every player at the beginning of each turn
				for i in range(self.upperNoOfCreatures):

					self.spawnCreature(brain)


	def spawnCreature(self,brain):

		position = np.array( [random.randint(0,self.worldmap.mapsize[0]-1), random.randint(0,self.worldmap.mapsize[1]-1) ] )

		#spawn position should be on the land, until find a suitable place, we repeat
		while True:


			if self.worldmap.worldframe[:,:,self.worldmap.LAYERID_WATERDEPTH][position[0],position[1]] == 0:
				break

			position = np.array( [random.randint(0,self.worldmap.mapsize[0]-1), random.randint(0,self.worldmap.mapsize[1]-1) ] )

		#creating new random positioned creature
		newCreature = creature.Creature(position)

		#setting fresh new brain
		worldViewShape = (newCreature.sight*2 + 1,newCreature.sight*2 + 1,self.worldmap.LAYERS)
		newCreature.setBrain(self,brain(numberOfActions = newCreature.numberOfActions, creatureStatsShape = newCreature.creatureStatsShape, worldViewShape  = worldViewShape), worldmap = self.worldmap)



		self.creatures.append(newCreature)
		self.noOfCreatures += 1

	#updating game each round
	def update(self):

		# 1x growth on vegatation
		self.worldmap.updateMap()

		self.spawnCreatures()

		#updating every creature in every round
		for creature in self.creatures:

			#if creature is dead, we call death method of its brain's death method and remove it from creature list of game
			if not creature.update(self.worldmap,self):

				creature.getBrain().death(creatureStats = np.copy(creature.creatureStats), worldViewOfCreature = np.copy(self.worldmap.getEnvironmentOfCreature(creature)), score = copy.copy(creature.creatureStats[creature.POS_ALIVECOUNTER]))

				self.creatures.remove(creature)
				self.noOfCreatures -= 1

				#if ( self.zoo.checkForHighscore(creature) ):

					#self.zoo.printHighscore()

	def render(self):
		self.worldmap.render(self)

	#return the rendered pygame picture
	def getImage(self):
		return self.worldmap.getImage()
