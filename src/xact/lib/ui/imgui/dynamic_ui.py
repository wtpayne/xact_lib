# -*- coding: utf-8 -*-
"""
Dynamic immediate mode graphical user interface component for xact.

"""

import sys

import imgui
import imgui.integrations.pygame
import OpenGL.GL
import pygame

import xact
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the bus component.

    """
    size  = (1024, 768)
    title = 'xact'
    mode  = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE

    state['pygame'] = pygame
    state['pygame'].init()
    state['pygame'].display.set_mode(size, mode)
    state['pygame'].display.set_caption(title)

    state['imgui'] = imgui
    state['imgui'].create_context()

    state['impl'] = imgui.integrations.pygame.PygameRenderer()

    state['io'] = state['imgui'].get_io()
    state['io'].display_size = size

    state['gl'] = OpenGL.GL

    state['function_table'] = dict()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the bus component.

    """
    _update_function_table(inputs, state)
    size = pygame.display.get_surface().get_size()
    state['io'].display_size = size

    for event in state['pygame'].event.get():
        if event.type == state['pygame'].QUIT:
            sys.exit(0)
        state['impl'].process_event(event)

    state['imgui'].new_frame()

    _main_menu(state)

    for (key, function) in state['function_table'].items():
        function(inputs, state, outputs)

    _render(state)


# -----------------------------------------------------------------------------
def _update_function_table(inputs, state):
    """
    """
    if inputs['functions']['ena']:
        for (key, value) in inputs['functions'].items():
            if key == 'ena':
                continue
            # if isinstance(value, string)
            state['function_table'][key] = xact.util.function_from_source(value)


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