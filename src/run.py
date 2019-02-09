GFX = True

import worldmap as wm
import game as g

if GFX:
    import pygame
    from pygame.locals import *
import numpy as np



def main():
    # mapsize in (height, width)
    game = g.Game( mapsize = (40,60), tilesize = (18,18), waterlevel = 0.1 )

    if GFX:
        # Initialise screen
        pygame.init()

        screen = pygame.display.set_mode(game.worldmap.worldsizeInPixels())
        pygame.display.set_caption('Evolution')

        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))



    # Event loop
    while 1:
        if GFX:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return

        game.update()

        if GFX:
            game.render()
            #coordinates in width, height
            screen.blit(game.getImage(), (0, 0))
            pygame.display.flip()


if __name__ == '__main__': main()
