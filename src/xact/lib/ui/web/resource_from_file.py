# -*- coding: utf-8 -*-
"""
Xact component for live web resource updating.

"""


import os.path
import time

import xact.lib.ui.web.markup.html as html
import xact.lib.web.util
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the xact component.

    """
    state['id_resource']   = cfg['id_resource']
    state['media_type']    = cfg['media_type']
    state['filepath']      = cfg['filepath']
    state['last_modified'] = 0


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the xact component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('resources',),
                    list_field_to_clear = ('list', ))

    modified = os.path.getmtime(state['filepath'])
    if state['last_modified'] >= modified:
        return
    state['last_modified'] = modified

    map_res = xact.lib.web.util.ResMap()
    with open(state['filepath'], 'rt') as file:
        map_res.add(media_type = state['media_type'],
                    **{state['id_resource']: file.read()})

    # Resources to publish.
    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]

