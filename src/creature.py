GFX = True

import numpy as np
import random
import copy
from abc import ABC, abstractmethod
import enum
import uuid
import brain
import itertools
import colorsys

class Creature():

    #indexes in the creature properties array
    POS_POSITION_X = 0
    POS_POSITION_Y = 1
    POS_HEALTH = 2
    POS_ALIVE = 3
    POS_ALIVECOUNTER = 4
    TOTAL = 5

    #
    def __init__( self,position):
        #unique id for every creature
        self.id = uuid.uuid4().hex
        #self.color = np.random.randint(low=0, high=255, size=(4))
        #self.color[3] = 255
        self.size = (3,3)

        if GFX:
            self.image = np.zeros((self.size[0],self.size[1],4), np.uint8)

        self.reproductionCounter = 0 # is it necessary to keep?

        #This is the array that we keep the necessary properties of creature
        self.creatureStats = np.zeros(self.TOTAL,dtype=np.float64)

        self.creatureStats[self.POS_POSITION_X] = position[0]
        self.creatureStats[self.POS_POSITION_Y] = position[1]
        self.creatureStats[self.POS_HEALTH] = 1
        self.creatureStats[self.POS_ALIVE] = 1
        self.creatureStats[self.POS_ALIVECOUNTER] = 0


        #new features
        self.numberOfActions = 6
        self.creatureStatsShape = 5 # its the shape of creatues's status np array
        self.sight = 5 #the number of tiles that creature can see, for one axis, towards one side

    #ACTIONS OF CREATURE    


    def setBrain(self,game,brain,worldmap,parentBrain = None):

        #new fresh brain for each creature
        self.brain = brain

        #Calling the birth method whenever a new brain is created.
        self.brain.birth(np.copy(self.creatureStats), worldViewOfCreature = np.copy(worldmap.getEnvironmentOfCreature(self)), parentBrain = parentBrain)

        
        if GFX:
            hue = game.brainHueValues[self.brain.__class__.__name__]
            brightness = self.brain.brightness()

            color = self.hsvTorgb(hue,brightness,brightness) #this returns rgb in 3 size tuple
            self.color = np.array([int(color[0]),int(color[1]),int(color[2]),255])


    def getBrain(self):
        return self.brain


    def moveUp(self,worldmap):

        newPosition = (self.creatureStats[self.POS_POSITION_X],self.creatureStats[self.POS_POSITION_Y]-1)

        #If the creature's new position is out of bounds, we slide it
        newPosition = self.slideCreature(newPosition,worldmap)

        #The creature cannot be on the ocean
        if self.validMove(newPosition,worldmap) == True:
            self.creatureStats[self.POS_POSITION_X] = newPosition[0]
            self.creatureStats[self.POS_POSITION_Y] = newPosition[1]



    def moveDown(self,worldmap):
        newPosition = (self.creatureStats[self.POS_POSITION_X],self.creatureStats[self.POS_POSITION_Y]+1)

        newPosition = self.slideCreature(newPosition,worldmap)

        if self.validMove(newPosition,worldmap) == True:
            self.creatureStats[self.POS_POSITION_X] = newPosition[0]
            self.creatureStats[self.POS_POSITION_Y] = newPosition[1]



    def moveLeft(self,worldmap):
        newPosition = (self.creatureStats[self.POS_POSITION_X]-1,self.creatureStats[self.POS_POSITION_Y])

        newPosition = self.slideCreature(newPosition,worldmap)

        if self.validMove(newPosition,worldmap) == True:
            self.creatureStats[self.POS_POSITION_X] = newPosition[0]
            self.creatureStats[self.POS_POSITION_Y] = newPosition[1]



    def moveRight(self,worldmap):
        newPosition = (self.creatureStats[self.POS_POSITION_X]+1,self.creatureStats[self.POS_POSITION_Y])

        newPosition = self.slideCreature(newPosition,worldmap)

        if self.validMove(newPosition,worldmap) == True:
            self.creatureStats[self.POS_POSITION_X] = newPosition[0]
            self.creatureStats[self.POS_POSITION_Y] = newPosition[1]


    def eat(self,worldmap):
        
        self.creatureStats[self.POS_HEALTH] += worldmap.worldframe[int(self.creatureStats[self.POS_POSITION_X]),int(self.creatureStats[self.POS_POSITION_Y]),worldmap.LAYERID_VEGETATION]
        if ( self.creatureStats[self.POS_HEALTH] ) > 1.0:
            self.creatureStats[self.POS_HEALTH] = 1.0
        worldmap.worldframe[int(self.creatureStats[self.POS_POSITION_X]),int(self.creatureStats[self.POS_POSITION_Y]),worldmap.LAYERID_VEGETATION] = 0


    #gives birth to a child creature
    def reproduce(self,game,worldmap,parentBrain):
        self.reproductionCounter += 1
        self.creatureStats[self.POS_HEALTH] *= 0.5 #reproduction costs health
        child = self.clone(game,worldmap = worldmap,parentBrain=parentBrain)
        return child

    #creates a fresh identical exemplar of this creature
    def clone(self,game,worldmap,parentBrain, position = None,):
        #Creating totally new creature independent of its parent
        clone = copy.deepcopy(self)
        clone.id = uuid.uuid4().hex #new unique id

        #creating a new brain for new child
        #this new brain will be the same type with parent brain. For example, if mother is simpleBrain, child is simpleBrain but new fresh instance
        clone.setBrain(game,self.getBrain().__class__(numberOfActions = self.numberOfActions, creatureStatsShape = self.creatureStatsShape, worldViewShape=(self.sight*2+1,self.sight*2+1,worldmap.LAYERS)),worldmap = worldmap,parentBrain = self.brain)
        clone.creatureStats[self.POS_ALIVE] = 1
        clone.creatureStats[self.POS_ALIVECOUNTER] = 0
        clone.reproductionCounter = 0
        clone.creatureStats[self.POS_HEALTH] = self.creatureStats[self.POS_HEALTH]
        if (not(position is None)):
            clone.position = position
        return clone


    #if the creature excess the size of the map, it comes up on the other side of map
    def slideCreature(self,position,worldmap):
        
        newPosition =list(position)

        if newPosition[0] < 0 :
            newPosition[0] += worldmap.mapsize[0]

        elif newPosition[0] >= worldmap.mapsize[0]:
            newPosition[0] -= worldmap.mapsize[0]

        if newPosition[1] < 0 :
            newPosition[1] += worldmap.mapsize[1]

        elif newPosition[1] >= worldmap.mapsize[1]:
            newPosition[1] -= worldmap.mapsize[1]

        return tuple(newPosition)
    
    
    def validMove( self, newPosition, worldmap ):

        if ( worldmap.worldframe[int(newPosition[0]),int(newPosition[1]),worldmap.LAYERID_WATERDEPTH] != 0.0 ): return False
        return True
        

    #creature update method, for each round
    def update(self, worldmap, game):

        #Creature environment
        worldViewOfCreature = worldmap.getEnvironmentOfCreature(self)

        #brain gives the decision
        action = self.brain.act(np.copy(self.creatureStats),np.copy(worldViewOfCreature))

        self.creatureStats[self.POS_ALIVECOUNTER] += 1
 
        #move up
        if ( action == 0 ):
            self.moveUp(worldmap)
        #move left
        elif ( action == 1 ):
            self.moveLeft(worldmap)
        #move down
        elif ( action == 2 ):
           self.moveDown(worldmap)
        #move right
        elif ( action == 3 ):
            self.moveRight(worldmap)
        
        #eat vegetation
        elif ( action == 4 ):
            self.eat(worldmap)

        #reproduce
        elif ( action == 5 ):
            child = self.reproduce(game,worldmap,self.brain)

            game.creatures.append(child)
            game.noOfCreatures += 1


        #creature loses health in every round
        self.creatureStats[self.POS_HEALTH] -= 0.01

        if self.creatureStats[self.POS_HEALTH] <= 0:
            self.creatureStats[self.POS_ALIVE] = 0


        return self.creatureStats[self.POS_ALIVE]
        
    def getSize(self):
        return self.size
        
    def render(self):
        self.image[:,:] = self.color
        return self.image

    def hsvTorgb(self,h,s,v):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

