# -*- coding: utf-8 -*-
"""
Continuous integration python type checker for xact.

"""


_NAME_TOOL = 'xact.lib.ci.pytype'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration python type checker component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration python type checker component.

    """
    list_name_output = ('conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True