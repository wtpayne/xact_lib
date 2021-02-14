# -*- coding: utf-8 -*-
"""
Xact component for web UI layout.

"""


import xact.lib.ui.web.markup.html as html
import xact.lib.ui.web.markup.svg as svg
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

    if not inputs['control']['ena']:
        return

    list_params = [{'_content': 'Item A', 'href': '#0'},
                   {'_content': 'Item B', 'href': '#0'},
                   {'_content': 'Item C', 'href': '#0'}]

    with html.div(_class = ('absolute', 'top-1', 'left-1')) as menu:
        menu.add(_hamburger_button())
        menu.add(_dropdown_menu(iter_params = list_params))

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(menu = menu)

    # Resource IDs for parent UI component to load.
    outputs['id_ui']['ena']  = True
    outputs['id_ui']['list'] = list(map_res.keys())

    # Resource IDs for the page to subscribe to.
    outputs['id_subs']['ena']  = True
    outputs['id_subs']['list'] = list(map_res.keys())

    # Resources to publish.
    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def _hamburger_button():
    """
    Return a hamburger button.

    """
    with html.div(data_script = "on click toggle .hidden on #menu",
                  _class      = ('h-10', 'w-10')) as hamburger_button:
        with svg.svg(focusable = "false",
                     viewBox   = "0 0 25 25",
                     _class    = ('h-full',
                                  'w-full',
                                  'rounded-xl',
                                  'hover:bg-gray-200')):
            svg.path(d = 'M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z')
    return hamburger_button


# -----------------------------------------------------------------------------
def _dropdown_menu(iter_params):
    """
    Return a dropdown menu.

    """
    with html.tag({'_tagtype': 'div',
                   'id':       'menu',
                   '_class':   ('hidden',
                                'w-48',
                                'py-2',
                                'block',
                                'rounded-2xl',
                                'overflow-hidden',
                                'bg-white',
                                'shadow-lg')}) as dropdown_menu:
        for params in iter_params:
           html.button('BUTTON',
                       data_hx_post = '/clicked')
           html.tag(_params = params,
                    _type   = 'a',
                    _class  = ('px-4',
                               'py-2',
                               'block',
                               'text-gray-500',
                               'hover:bg-gray-200',
                               'hover:text-black'))

    return dropdown_menu


# with tag.div(data_hx_sse = 'connect:/sub/{query}'.format(
#                                 query = '-'.join(list_id_resource))):
#     for id_resource in list_id_resource:
#         tag.div(data_hx_trigger = 'changed',
#                 data_hx_get = '/req/{id}'.format(id = id_resource),
#                 data_hx_sse = 'swap:{id}'.format(id = id_resource))


