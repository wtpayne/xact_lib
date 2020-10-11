# -*- coding: utf-8 -*-
"""
Xact component to pack data.

"""


import struct


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data packer.

    """
    state['fields'] = cfg['fields']
    state['format'] = cfg['format']
    num_bytes = struct.calcsize(state['format'])
    outputs['packed']['buffer'] = bytearray(num_bytes)


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data packer.

    """
    list_items = []
    for path in state['fields']:
        list_items.append(inputs['data']['values'][path])

    struct.pack_into(state['format'],
                     outputs['packed']['buffer'],
                     0,                             # offset
                     *list_items)
