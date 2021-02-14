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
    state['list'] = list()
    for cfg_item in cfg['list']:
        state_item = dict()
        state_item.update(cfg_item)
        state_item['last_modified'] = 0
        state['list'].append(state_item)


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the xact component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('resources',),
                    list_field_to_clear = ('list', ))

    if not inputs['control']['ena']:
        return

    map_res = xact.lib.web.util.ResMap()
    for state_item in state['list']:

        modified = os.path.getmtime(state_item['filepath'])
        if state_item['last_modified'] >= modified:
            return
        state_item['last_modified'] = modified

        if state_item['is_binary']:
            mode_file = 'rb'
        else:
            mode_file = 'rt'

        with open(state_item['filepath'], mode_file) as file:
            map_res.add(media_type = state_item['media_type'],
                        **{state_item['id_resource']: file.read()})


    if map_res:
        outputs['resources']['ena']  = True
        outputs['resources']['list'] = [dict(map_res)]

