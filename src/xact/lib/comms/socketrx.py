# -*- coding: utf-8 -*-
"""
Xact component for UDP data reception.

"""


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the udprx component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the udprx component.

    """
    outputs['data'].clear()
    outputs['data']['buffer'] = inputs['data']['buffer']
