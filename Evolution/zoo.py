import numpy as np

import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')


class Zoo(dict):

    def __init__(self):
        super().__init__()
        self.highScoreThreshold = 0
        self.keepTopK = 10

    def checkForHighscore(self, creature):
        score = creature.creatureStats[creature.POS_ALIVECOUNTER]
        id = creature.id
        
        if ( score < self.highScoreThreshold ):
            return False
        
        if ( id in self ):
            if ( creature.creatureStats[creature.POS_ALIVECOUNTER] > self[id].creatureStats[creature.POS_ALIVECOUNTER] ):
                self[id] = creature
        else:
            self[id] = creature
            
        setOfCreatures = self.getBestCreatures()
        
        #remove last entry (which is the one that is over the max count in highscore)
        if ( np.shape(setOfCreatures)[0] > self.keepTopK ):
            self.highScoreThreshold = (setOfCreatures[self.keepTopK-1]).creatureStats[(setOfCreatures[self.keepTopK-1]).POS_ALIVECOUNTER]
            self.pop(setOfCreatures[self.keepTopK].id)
        
        return True
    
    def getBestCreatures(self):
        setOfCreatures = self.values()
        setOfCreatures = [x for x in setOfCreatures]
        scores = np.array([x.creatureStats[x.POS_ALIVECOUNTER] for x in setOfCreatures], ndmin=1)
        sortedIndexes = (np.argsort(scores))[::-1]
        return [setOfCreatures[x] for x in sortedIndexes]
        
    def printHighscore(self):
        cls()
        setOfCreatures = self.getBestCreatures()
        for i in range( np.shape(setOfCreatures)[0] ):
            print(str(i+1)+". "+str( (setOfCreatures[i]).id)+ "_" + (setOfCreatures[i]).getBrain().__class__.__name__ + " score: "+str( (setOfCreatures[i]).creatureStats[(setOfCreatures[i]).POS_ALIVECOUNTER]))
