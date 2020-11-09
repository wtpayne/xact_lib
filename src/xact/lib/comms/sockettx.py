# -*- coding: utf-8 -*-
"""
Xact component for UDP data transmission.

"""


import socket


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the udptx component.

    """
    state['test']   = cfg['test']
    state['ip']     = cfg['ip']
    state['port']   = cfg['port']
    state['family'] = cfg['family']
    state['type']   = cfg['type']

    if not state['test']:
        state['socket'] = socket.socket(state['family'], state['type'])

        state['socket'].setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        state['socket'].setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# cs.sendto('This is a test', ('255.255.255.255', 54545))


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the udptx component.

    """
    if state['test']:
        outputs['data'].clear()
        outputs['data']['buffer'] = inputs['data']['buffer']
    else:
        state['sock'].sendto(inputs['data']['buffer'],
                             (state['ip'], state['port']))
