# -*- coding: utf-8 -*-
"""
Xact component to bus data.

"""

import sys
import inspect

import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the bus component.

    """
    state['has_updated'] = False


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the bus component.

    """
    if state['has_updated']:
        outputs['functions']['ena'] = False

    else:
        outputs['functions']['ena'] = True
        outputs['functions']['inspector'] = inspect.getsource(inspector_step)


# -----------------------------------------------------------------------------
def inspector_step(inputs, state, outputs):
    """
    Step the inspector UI.

    """
    import xact.util

    for (key, data_item) in inputs.items():

        if key == 'control':
            continue

        if key == 'functions':
            continue

        title = key
        state['imgui'].set_next_window_size(200, 200, state['imgui'].ONCE)
        state['imgui'].begin(title, True)
        state['imgui'].begin_child('region',
                                   width  = 0.0,
                                   height = 0.0,
                                   border = False)

        for (tup_path, leaf) in xact.util.walkobj(data_item,
                                                  gen_leaf    = True,
                                                  gen_nonleaf = False,
                                                  gen_path    = True,
                                                  gen_obj     = True):

            str_path = '.'.join(str(item) for item in tup_path)
            text = '{path} - {value}'.format(path  = str_path,
                                             value = str(leaf))
            state['imgui'].text(text)

        state['imgui'].end_child()
        state['imgui'].end()
