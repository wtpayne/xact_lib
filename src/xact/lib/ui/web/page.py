# -*- coding: utf-8 -*-
"""
Xact component for web UI layout.

"""


import xact.lib.ui.web.util
import xact.lib.ui.web.markup.html
import xact.lib.web.util
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the xact component.

    """
    state['page_title']       = cfg['page_title']
    state['id_resource_page'] = cfg['id_resource']
    state['id_topic']         = cfg['id_topic']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the xact component.

    """
    xact.util.clear_outputs(outputs             = outputs,
                            list_name_output    = ('resources', ),
                            list_field_to_clear = ('list', ))

    map_res = xact.lib.web.util.ResMap()
    if inputs['id_subs']['ena']:
        map_res.topic(**{state['id_topic']: inputs['id_subs']['list']})

    if inputs['id_ui']['ena']:
        map_res.htm(
            **{state['id_resource_page']: xact.lib.ui.web.util.page(
                                    title      = state['page_title'],
                                    id_topic   = state['id_topic'],
                                    list_id_ui = inputs['id_ui']['list'])})
        map_res.js(
            xact_htmx_extension = xact.lib.ui.web.util.xact_htmx_extension())

    if map_res:
        outputs['resources']['ena']  = True
        outputs['resources']['list'] = [dict(map_res)]


