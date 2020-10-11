# -*- coding: utf-8 -*-
"""
Simple reporting component.

"""


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the reporting component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the reporting component.

    """
    if not inputs['rollup']['ena']:
        return
