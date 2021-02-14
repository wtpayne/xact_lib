# -*- coding: utf-8 -*-
"""
Xact UI component for displaying SVG content.

"""


import xact.lib.ui.web.widget.search
import xact.lib.ui.web.widget.titleblock
import xact.lib.ui.web.util
import xact.lib.web.util

import dill


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
    map_res.update(_single_page_app(id_app   = 'app',
                                    metadata = state['metadata_cache']))
    map_res.js(
        xact_htmx_extension = xact.lib.ui.web.util.xact_htmx_extension())

    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def _single_page_app(id_app, metadata):
    """
    Return a ResMap for a page with a 'live' view of some selectable SVG.

    """
    list_id_ui = list()
    list_subs  = list()
    map_res    = xact.lib.web.util.ResMap()

    id_div_content = id_app + '_div'
    div_content = xact.lib.ui.web.markup.html.div(id = id_div_content)
    map_res.htm(**{id_div_content: div_content})
    list_id_ui.append(id_div_content)

    tup_commands = ('add-host',
                    'add-process',
                    'add-node',
                    'add-edge')

    search_index = dict()
    for item in tup_commands:
        search_index[item] = item

    (map_res_search,
     id_search,
     list_search_subs) = xact.lib.ui.web.widget.search.box(
                                                id_base   = id_app,
                                                map_index = search_index)
    list_id_ui.append(id_search)
    list_subs.append(id_search)
    map_res.update(map_res_search)

    # TODO: Pull out different diagram types from metadata
    list_systems  = list(metadata.values())
    list_diagrams = [{'str_title':      'Data flow (deployment)',
                      'id_div_content': 'id_div_TBD'},
                     {'str_title':      'Some other diagram type.',
                      'id_div_content': 'id_div_TBD'}]

    (map_res_titleblock,
     id_titleblock,
     list_titleblock_subs) = xact.lib.ui.web.widget.titleblock.box(
                                                id_base       = id_app,
                                                list_systems  = list_systems,
                                                list_diagrams = list_diagrams,
                                                id_div_target = id_div_content)

    list_id_ui.append(id_titleblock)
    list_subs.append(id_titleblock)
    list_subs.extend(list_titleblock_subs)
    map_res.update(map_res_titleblock)

    id_topic  = id_app + '_updates'
    id_page   = id_app
    page_content = xact.lib.ui.web.util.page(
                            title      = id_app.replace('_', ' ').title(),
                            id_topic   = id_topic,
                            list_id_ui = list_id_ui)
    map_res.topic(**{id_topic: list_subs})
    map_res.htm(**{id_page: page_content})

    return map_res


# -----------------------------------------------------------------------------
def _single_svg_page(id_content, svg_content):
    """
    Return a ResMap for a page with a 'live' view of some fixed SVG resource.

    """
    id_diagram     = id_content + '_diagram'
    id_div_content = id_content + '_div'
    id_topic       = id_content + '_updates'
    id_page        = id_content
    str_title      = id_content.replace('_', ' ').title()

    div_content = xact.lib.ui.web.markup.html.div()
    div_content.add(
            xact.lib.ui.web.util.sse_swapping_streamer([id_diagram])[0])
    page_content = xact.lib.ui.web.util.page(title      = str_title,
                                             id_topic   = id_topic,
                                             list_id_ui = [id_div_content])

    map_res = xact.lib.web.util.ResMap()
    map_res.topic(**{id_topic: [id_diagram]})
    map_res.svg(**{id_diagram: svg_content})
    map_res.htm(**{id_div_content: div_content})
    map_res.htm(**{id_page: page_content})

    map_meta = {
        'str_title':      str_title,
        'id_diagram':     id_diagram,
        'id_div_content': id_div_content
    }
    return (map_res, map_meta)