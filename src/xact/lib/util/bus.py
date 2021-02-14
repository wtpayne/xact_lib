# -*- coding: utf-8 -*-
"""
Xact component to bus data.

"""


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the bus component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the bus component.

    """
    outputs['bus'].clear()
    for (key, value) in inputs.items():
        if key == 'control':
            continue
        outputs['bus'][key] = dict()
        outputs['bus'][key].update(value)
