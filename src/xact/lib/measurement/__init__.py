# -*- coding: utf-8 -*-
"""
Package with tools to record and replay data.

"""


import base64
import math
import os.path

import dill


# -----------------------------------------------------------------------------
def write_frame(file, inputs, protocol):
    """
    Write the current data frame to file.

    """
    bytes_serialized = dill.dumps(inputs, protocol = protocol)
    bytes_encoded    = base64.b64encode(bytes_serialized)
    bytes_line_item  = bytes_encoded + b'\n'
    file.write(bytes_line_item)


# -----------------------------------------------------------------------------
def file_rec(idx, state, mode):
    """
    Return an open recording file.

    """
    id_block    = math.floor(idx / state['size_block'])
    if id_block != state['id_block']:
        if state['file'] is not None:
            state['file'].close()
        state['id_block'] = id_block
        state['file']     = open(_filepath_rec(state), mode, 0)

    return state['file']


# -----------------------------------------------------------------------------
def _filepath_rec(state):
    """
    Return the filepath of the current recording file.

    """
    filename_rec = state['format_name'].format(id_block  = state['id_block'])
    filepath_rec = os.path.join(state['dirpath_rec'], filename_rec)
    return filepath_rec

