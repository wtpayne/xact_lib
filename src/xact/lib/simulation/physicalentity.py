# -*- coding: utf-8 -*-
"""
Xact component for physical entity simulation.

"""


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the physical entity simulation component.

    """
    state['pos_x'] = cfg['pos_x']
    state['pos_y'] = cfg['pos_y']
    state['pos_z'] = cfg['pos_z']

    state['vel_x'] = cfg['vel_x']
    state['vel_y'] = cfg['vel_y']
    state['vel_z'] = cfg['vel_z']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the physical entity simulation component.

    """
    state['pos_x'] = state['pos_x'] + state['vel_x']
    state['pos_y'] = state['pos_y'] + state['vel_y']
    state['pos_z'] = state['pos_z'] + state['vel_z']

    outputs['pos']['x'] = state['pos_x']
    outputs['pos']['y'] = state['pos_y']
    outputs['pos']['z'] = state['pos_z']
