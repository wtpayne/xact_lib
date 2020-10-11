# -*- coding: utf-8 -*-
"""
Xact component for test vector generation.

"""


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the signal generator.

    """
    state['channels'] = cfg['channels']
    for channel in state['channels']:
        channel['num_samples'] = len(channel['signal'])


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the signal generator.

    """
    for channel in state['channels']:
        offset       = inputs['clock']['idx'] % channel['num_samples']
        sample_value = channel['signal'][offset]

        path   = channel['path']
        cursor = outputs
        for name in path[:-1]:
            if name not in cursor:
                cursor[name] = dict()
            cursor = cursor[name]
        cursor[path[-1]] = sample_value