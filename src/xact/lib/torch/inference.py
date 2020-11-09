# -*- coding: utf-8 -*-
"""
Pytorch inference node.

"""


import torch


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the pytorch inference node.

    """
    state['device'] = None
    state['model']  = None


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Run an inference step.

    """
    outputs['result']['ena']  = False

    if inputs['model']['ena']:
        state['device'] = torch.device(
                                "cuda" if torch.cuda.is_available() else "cpu")
        state['model'] = inputs['model']['model']
        state['model'].to(state['device'])
        state['model'].eval()

    if state['model'] and inputs['sample']['ena']:
        outputs['result']['ena']  = True
        outputs['result']['ts']   = inputs['sample']['ts']
        outputs['result']['data'] = state['model'](
                                                inputs['sample']['buff'].to(
                                                            state['device']))