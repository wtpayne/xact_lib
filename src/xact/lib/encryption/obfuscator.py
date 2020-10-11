# -*- coding: utf-8 -*-
"""
Xact component to obfuscate data.

"""


import copy
import Crypto.Cipher


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data obfuscator.

    """
    state['key'] = cfg['key']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data obfuscator.

    """
    aes_cipher = Crypto.Cipher.AES.new(state['key'],
                                       Crypto.Cipher.AES.MODE_CBC,
                                       'This is an IV456')
    num_bytes_data                 = len(inputs['data']['buffer'])
    num_bytes_packing              = 16 - (num_bytes_data % 16)
    num_bytes_buffer               = num_bytes_data + num_bytes_packing
    input_buffer                   = bytearray(num_bytes_buffer)
    input_buffer[0:num_bytes_data] = inputs['data']['buffer']
    input_buffer[-1]               = num_bytes_data
    outputs['data']['buffer']      = aes_cipher.encrypt(bytes(input_buffer))
