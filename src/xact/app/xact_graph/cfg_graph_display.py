# -*- coding: utf-8 -*-
"""
Xact UI component for displaying SVG content.

"""


import xact.lib.web.util
import xact.lib.ui.web.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the SVG UI component.

    """
    state['metadata_cache'] = dict()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the SVG UI component.

    """
    xact.util.clear_outputs(outputs             = outputs,
                            list_name_output    = ('resources', ),
                            list_field_to_clear = ('list', ))


    if not inputs['svg']['ena']:
        return

    # Create a page for each SVG that we are given.
    map_res = xact.lib.web.util.ResMap()
    for (id_content, svg_content) in inputs['svg']['map'].items():
        (map_res_single, map_meta) = _single_svg_page(id_content, svg_content)
        map_res.update(map_res_single)
        state['metadata_cache'][id_content] = map_meta

    # Create an 'index' that will let us choose an SVG to view.
    map_res.update(_selectable_svg_page(
                                    id_content     = 'dataflow_graphs',
                                    metadata_cache = state['metadata_cache']))
    map_res.js(
        xact_htmx_extension = xact.lib.ui.web.util.xact_htmx_extension())

    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def _selectable_svg_page(id_content, metadata_cache):
    """
    Return a ResMap for a page with a 'live' view of some selectable SVG.

    """
    # A page where each SVG can be selected for display.
    id_svg         = id_content + '_svg'
    id_div_content = id_content + '_div'
    id_div_menu    = id_content + '_menu'
    id_topic       = id_content + '_updates'
    id_page        = id_content
    str_title      = id_content.replace('_', ' ').title()

    html           = xact.lib.ui.web.markup.html
    div_content    = html.div(id = id_div_content)
    div_menu       = html.div()

    list_id_target = list()
    for map_meta in metadata_cache.values():
        list_id_target.append(map_meta['id_svg'])
        div_menu.add(
            html.div(map_meta['str_title'],
                data_hx_trigger = 'click',
                data_hx_get     = '/{id}'.format(id = map_meta['id_div_content']),
                data_hx_target  = '#{id}'.format(id = id_div_content),
                data_hx_swap    = 'innerHTML'))

    page_content = xact.lib.ui.web.util.page(
                                    title      = str_title,
                                    id_topic   = id_topic,
                                    list_id_ui = [id_div_menu, id_div_content])

    map_res = xact.lib.web.util.ResMap()
    map_res.topic(**{id_topic: list_id_target})
    map_res.htm(**{id_div_content: div_content})
    map_res.htm(**{id_div_menu: div_menu})
    map_res.htm(**{id_page: page_content})

    return map_res


# -----------------------------------------------------------------------------
def _single_svg_page(id_content, svg_content):
    """
    Return a ResMap for a page with a 'live' view of some fixed SVG resource.

    """
    id_svg         = id_content + '_svg'
    id_div_content = id_content + '_div'
    id_topic       = id_content + '_updates'
    id_page        = id_content
    str_title      = id_content.replace('_', ' ').title()

    div_content = xact.lib.ui.web.markup.html.div()
    div_content.add(
            xact.lib.ui.web.util.sse_swapping_streamer([id_svg])[0])
    page_content = xact.lib.ui.web.util.page(title      = str_title,
                                             id_topic   = id_topic,
                                             list_id_ui = [id_div_content])

    map_res = xact.lib.web.util.ResMap()
    map_res.topic(**{id_topic: [id_svg]})
    map_res.svg(**{id_svg: svg_content})
    map_res.htm(**{id_div_content: div_content})
    map_res.htm(**{id_page: page_content})

    map_meta = {
        'str_title':      str_title,
        'id_svg':         id_svg,
        'id_div_content': id_div_content
    }
    return (map_res, map_meta)