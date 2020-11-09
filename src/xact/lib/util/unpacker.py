# -*- coding: utf-8 -*-
"""
Xact component to unpack data.

"""


import struct


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data packer.

    """
    state['fields'] = cfg['fields']
    state['format'] = cfg['format']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data packer.

    """
    iter_values = struct.unpack(state['format'], inputs['packed']['buffer'])

    outputs['data']['values'] = dict()
    for (path, value) in zip(state['fields'], iter_values):
        outputs['data']['values'][path] = value
