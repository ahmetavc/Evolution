from brain import Brain


class Simple(Brain):

    teamScore = 0
    #img = pygame.image.load(os.path.dirname(__file__),'intro_ball.gif')

    def __init__(self, numberOfActions, creatureStatsShape, worldViewShape):

        Simple.numberOfActions = numberOfActions
        Simple.creatureStatsShape = creatureStatsShape
        Simple.worldViewShape = worldViewShape



    def getId(self):
        pass

    def birth(self, creatureStats, worldViewOfCreature, parentBrain):
        pass


    def act(self,creatureStats,worldView):
        return 3


    def death(self, creatureStats, worldViewOfCreature, score):
        pass


    def brightness(self):
        return 0.5
