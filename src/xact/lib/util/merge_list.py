# -*- coding: utf-8 -*-
"""
Merge multiple input lists onto a single output list.

"""


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the list merge component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the list merge component.

    """
    assert len(outputs) == 1
    id_out = next(iter(outputs.keys()))

    outputs[id_out].clear()
    outputs[id_out]['ena']  = False
    outputs[id_out]['list'] = list()

    for key in inputs.keys():
        if not inputs[key]['ena']:
            continue
        outputs[id_out]['ena']  = True
        outputs[id_out]['list'].extend(inputs[key]['list'])
