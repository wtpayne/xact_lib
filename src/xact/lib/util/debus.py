# -*- coding: utf-8 -*-
"""
Xact component to debus data.

"""


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the debus component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the debus component.

    """
    for (key, value) in inputs['bus'].items():
        outputs[key].clear()
        outputs[key].update(value)
