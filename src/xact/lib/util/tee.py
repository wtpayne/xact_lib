# -*- coding: utf-8 -*-
"""
Duplicate a single input data item onto all outputs.

"""


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the tee.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the tee.

    """
    assert len(inputs) == 1
    input_data = next(iter(inputs.values()))
    for key in outputs.keys():
        outputs[key].clear()
        outputs[key].update(input_data)