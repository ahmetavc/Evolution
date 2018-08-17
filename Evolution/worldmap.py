GFX = True

import numpy as np
import cv2

if GFX:
    import pygame
import creature as c
import random
import zoo

class Map:

    LAYERID_HEIGHT = 0
    LAYERID_WATERDEPTH = 1
    LAYERID_HUMIDITY = 2
    LAYERID_VEGETATION = 3
    LAYERS = 4


    def scaleTo01(self,matrix):
        min = np.amin(matrix)
        return ( matrix - min ) / (np.amax(matrix) - min)

    
    #mapsize = height, width
    def __init__(self, mapsize = (20,20), tilesize = (5,5), waterlevel = 0.1):

        #map properties
        self.mapsize = mapsize #in tiles
        self.tilesize = tilesize #in pixels, height, width
        
        #basic core calculations
        self.mapsizeInPixels = (self.mapsize[0]*self.tilesize[0],self.mapsize[1]*self.tilesize[1])
        
        #init the overall world data array:
        self.worldframe = np.zeros((self.mapsize[0], self.mapsize[1], self.LAYERS), dtype=np.float64)
        
        
        #create the heightmap
        heightmap = np.random.rand(self.mapsize[0], self.mapsize[1]) #random value between 0. and 1.
        kernel = np.ones((5,5),np.float64)/25
        heightmap = cv2.filter2D(heightmap,-1,kernel)
        self.worldframe[:,:,self.LAYERID_HEIGHT] = self.scaleTo01(heightmap)
        
        #create water map (flood everything such that waterlevel amount of tiles are full of water)
        indexOfWaterLevel = int(self.mapsize[0] * self.mapsize[1] * waterlevel)
        heightmap = self.worldframe[:,:,self.LAYERID_HEIGHT]
        sortedFlattenedHeights = np.sort(np.ndarray.flatten(heightmap))
        waterLevel = sortedFlattenedHeights[indexOfWaterLevel]
        waterDepthMap = waterLevel - heightmap
        waterDepthMap[waterDepthMap <= 0] = 0.0
        self.worldframe[:,:,self.LAYERID_WATERDEPTH] = waterDepthMap
        
        #create humidity
        self.humidity = np.random.rand(self.mapsize[0], self.mapsize[1]) #random value between 0. and 1.
        kernel = np.ones((5,5),np.float32)/25
        self.humidity = cv2.filter2D(self.humidity,-1,kernel)
        self.worldframe[:,:,self.LAYERID_HUMIDITY] = self.scaleTo01(self.humidity)
        

        
        #create vegetation
        vegetationMap = np.zeros(self.mapsize, dtype=np.float64)
        self.vegetationBaseGrowth = 0.0001
        self.worldframe[:,:,self.LAYERID_VEGETATION] = vegetationMap
        
        if GFX:
            #image: y-axis, x-axis, rgba
            self.image = np.zeros((self.mapsizeInPixels[0], self.mapsizeInPixels[1],4), np.uint8)
        
        self.highScoreCreatures = {}
        self.highScoreThreshold = 0
        self.keepTopK = 10
        
        self.zoo = zoo.Zoo()


    def updateVegetation(self, steps = 1):
       #increase the vegatation on the land according to humidity
       mask = (self.worldframe[:,:,self.LAYERID_WATERDEPTH] == 0)
       self.worldframe[:,:,self.LAYERID_VEGETATION][mask] += self.worldframe[:,:,self.LAYERID_HUMIDITY][mask] * self.vegetationBaseGrowth * steps

       #max vegetation level is 1.0
       mask2 = (self.worldframe[:,:,self.LAYERID_VEGETATION]>1.0)
       self.worldframe[:,:,self.LAYERID_VEGETATION][mask2] = 1.0


    def resetVegetation(self):
       self.worldframe[:,:,self.LAYERID_VEGETATION] = 0
       self.updateVegetation(steps = 100)


    def updateMap(self):

        #increase the vegatation on the land according to humidity
        self.updateVegetation()

        
    def worldsizeInPixels(self):
        return (self.mapsizeInPixels[1], self.mapsizeInPixels[0])


    #creatures see only the small part of the map, just their environement
    def getEnvironmentOfCreature(self,creature):

        creaturePos = np.array((creature.creatureStats[creature.POS_POSITION_X],creature.creatureStats[creature.POS_POSITION_X]))
        viewRange = np.array((creature.sight,creature.sight))
        shift = ( viewRange - creaturePos )

        shiftedWorldFrame = np.roll( self.worldframe, shift=int(shift[0]), axis=0 )
        shiftedWorldFrame = np.roll( shiftedWorldFrame, shift=int(shift[1]), axis=1 )
        creaturesEnvironment = shiftedWorldFrame[0:viewRange[0]*2+1, 0:viewRange[1]*2+1,:]

        return creaturesEnvironment


       
    #run the render loop that renders the whole world  
    def render(self, game):
        t0 = self.tilesize[0]
        t1 = self.tilesize[1]
        self.image[:,:,3] = 255 #alpha
        
        dry = np.array([174,114,0])
        wet = np.array([0,100,0])
                    
        for i in range(self.mapsize[0]):
            for j in range (self.mapsize[1]):
                x0s = i*t0
                x1s = j*t1
                x0e = (i+1)*t0
                x1e = (j+1)*t1
            
                if ( self.worldframe[i,j,self.LAYERID_WATERDEPTH] != 0.0 ) :
                    self.image[x0s:x0e,x1s:x1e,0] = 0
                    self.image[x0s:x0e,x1s:x1e,1] = 0
                    self.image[x0s:x0e,x1s:x1e,2] = 255
                elif ( self.worldframe[i,j,self.LAYERID_WATERDEPTH] == 0 ):
                    l = self.worldframe[i,j,self.LAYERID_VEGETATION]
                    self.image[x0s:x0e,x1s:x1e,0:3] = ((1.0 - l) * dry ) + ( l * wet )
                
        #kernel = np.ones((7,7),np.float32)/49
        #self.image = cv2.filter2D(self.image,-1,kernel)
        
        for creature in game.creatures:
            position = (creature.creatureStats[creature.POS_POSITION_X],creature.creatureStats[creature.POS_POSITION_Y])
            size = creature.getSize()
            
            x0s = int(position[0]*t0)
            x1s = int(position[1]*t1)
            x0e = int(x0s + size[0])
            x1e = int(x1s + size[1])

            self.image[x0s:x0e,x1s:x1e] = creature.render()

    #return the rendered pygame picture  
    def getImage(self):
        return pygame.image.frombuffer(self.image.tostring(), (self.image.shape[:2])[::-1],"RGBA")

    