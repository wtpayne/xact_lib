# -*- coding: utf-8 -*-
"""
Xact component to bus data.

"""

import sys

import imgui
import imgui.integrations.pygame
import OpenGL.GL
import pygame

import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the bus component.

    """
    size = (1024, 768)

    state['pygame'] = pygame
    state['pygame'].init()
    state['pygame'].display.set_mode(size,
                                     (   state['pygame'].DOUBLEBUF
                                       | state['pygame'].OPENGL
                                       | state['pygame'].RESIZABLE))
    state['pygame'].display.set_caption('xact')

    state['imgui'] = imgui
    state['imgui'].create_context()

    state['impl'] = imgui.integrations.pygame.PygameRenderer()

    state['io'] = state['imgui'].get_io()
    state['io'].display_size = size

    state['gl'] = OpenGL.GL


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the bus component.

    """
    size = pygame.display.get_surface().get_size()
    state['io'].display_size = size

    for event in state['pygame'].event.get():

        if event.type == state['pygame'].QUIT:
            sys.exit(0)

        state['impl'].process_event(event)

    state['imgui'].new_frame()

    data = {
        'x':     100,
        'y':     100,
        'z':     100,
        'vel_x': 100,
        'vel_y': 100,
        'vel_z': 100
    }

    _main_menu(state)
    _data_window(state, data)
    _render(state)


# -----------------------------------------------------------------------------
def _data_window(state, data):
    """
    Draw a data window.

    """
    state['imgui'].set_next_window_size(200, 200, imgui.ONCE)
    state['imgui'].begin('Instantaneous values', True)
    state['imgui'].begin_child('region',
                               width  = 0.0,
                               height = 0.0,
                               border = False)

    for (tup_path, leaf) in xact.util.walkobj(data,
                                              gen_leaf    = True,
                                              gen_nonleaf = False,
                                              gen_path    = True,
                                              gen_obj     = True):

        text = '{path} - {value}'.format(path  = '.'.join(tup_path),
                                         value = str(leaf))
        state['imgui'].text(text)

    state['imgui'].end_child()

    # state['imgui'].text("Bar")
    # state['imgui'].text_colored("Eggs", 0.2, 1., 0.)
    state['imgui'].end()


# -----------------------------------------------------------------------------
def _main_menu(state):
    """
    """
    if state['imgui'].begin_main_menu_bar():
        if state['imgui'].begin_menu('File', True):
            (clicked_quit, selected_quit) = state['imgui'].menu_item(
                                                'Quit', 'Cmd+Q', False, True)
            if clicked_quit:
                sys.exit(0)
            state['imgui'].end_menu()
        state['imgui'].end_main_menu_bar()


# -----------------------------------------------------------------------------
def _render(state):
    """
    Render.

    """
    # note: cannot use screen.fill((1, 1, 1)) because pygame's screen
    #       does not support fill() on OpenGL sufraces
    state['gl'].glClearColor(1, 1, 1, 1)
    state['gl'].glClear(state['gl'].GL_COLOR_BUFFER_BIT)
    state['imgui'].render()
    state['impl'].render(state['imgui'].get_draw_data())
    state['pygame'].display.flip()
