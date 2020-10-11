# -*- coding: utf-8 -*-
"""
Xact component to deobfuscate data.

"""


import Crypto.Cipher


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data deobfuscator.

    """
    state['key'] = cfg['key']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data deobfuscator.

    """
    aes_cipher = Crypto.Cipher.AES.new(state['key'],
                                       Crypto.Cipher.AES.MODE_CBC,
                                       'This is an IV456')

    output_buffer  = aes_cipher.decrypt(bytes(inputs['data']['buffer']))
    num_bytes_data = output_buffer[-1]
    outputs['data']['buffer'] = output_buffer[0:num_bytes_data]
