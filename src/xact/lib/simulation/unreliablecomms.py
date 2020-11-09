# -*- coding: utf-8 -*-
"""
Xact component for simulating unreliable communications of some sort.

"""


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the unreliable_comms simulation component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the unreliable_comms simulation component.

    """
    outputs['data'].clear()
    outputs['data']['buffer'] = inputs['data']['buffer']
