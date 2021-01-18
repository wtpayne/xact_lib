# -*- coding: utf-8 -*-
"""
Xact component for web UI layout.

"""


import xact.lib.ui.web.util
import xact.lib.ui.web.markup.html as html
import xact.lib.web.util
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the xact component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the xact component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('id_ui', 'id_subs', 'resources'),
                    list_field_to_clear = ('list', ))

    if not inputs['id_ui']['ena']:
        return

    tag_dashboard = xact.lib.ui.web.util.dashboard(
                                        list_id_ui = inputs['id_ui']['list'])

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(dashboard = tag_dashboard)

    # Resource IDs for parent UI component to load.
    outputs['id_ui']['ena']  = True
    outputs['id_ui']['list'] = list(map_res.keys())

    # Resource IDs for the page to subscribe to.
    outputs['id_subs']['ena']  = True
    outputs['id_subs']['list'] = list(map_res.keys())

    # Resources to publish.
    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]
