# -*- coding: utf-8 -*-
"""
Xact pygame component.

"""


import os
import sys

import pygame


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the pygame component.

    """
    state['headless'] = cfg.get('headless', False)
    state['width']    = cfg.get('width',    512)
    state['height']   = cfg.get('height',   512)
    state['size']     = (state['width'], state['height'])
    state['speed']    = [2, 2]

    if state['headless']:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1,1))
        state['screen'] = pygame.Surface(state['size'], pygame.SRCALPHA, 32)
        pygame.draw.rect(state['screen'],
                         (0,0,0),
                         (0, 0, state['width'], state['height']),
                         0)

    else:
        pygame.init()
        state['screen'] = pygame.display.set_mode(state['size'])

    state['boat']     = pygame.image.load('/media/wtp/Data/dev/xact_lib/src/xact/app/xact_pygame/boat.jpeg')
    state['boatrect'] = state['boat'].get_rect()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the pygame component.

    """
    black = 0, 0, 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    state['boatrect'] = state['boatrect'].move(state['speed'])
    if state['boatrect'].left < 0 or state['boatrect'].right > state['width']:
        state['speed'][0] = -state['speed'][0]

    if state['boatrect'].top < 0 or state['boatrect'].bottom > state['height']:
        state['speed'][1] = -state['speed'][1]

    state['screen'].fill((0,0,0))
    state['screen'].blit(state['boat'], state['boatrect'])
    pygame.display.flip()

    print(dir(state['screen']))



# import sys, pygame
# pygame.init()

# size = width, height = 320, 240
# speed = [2, 2]
# black = 0, 0, 0

# screen = pygame.display.set_mode(size)

# ball = pygame.image.load("intro_ball.gif")
# ballrect = ball.get_rect()

# while 1:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT: sys.exit()

#     ballrect = ballrect.move(speed)
#     if ballrect.left < 0 or ballrect.right > width:
#         speed[0] = -speed[0]
#     if ballrect.top < 0 or ballrect.bottom > height:
#         speed[1] = -speed[1]

#     screen.fill(black)
#     screen.blit(ball, ballrect)
#     pygame.display.flip()