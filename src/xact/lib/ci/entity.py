# -*- coding: utf-8 -*-
"""
Entity renderer.

"""


import copy

import dominate
import dominate.tags as tag
import esper

import xact.lib.web.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the entity renderer component.

    """
    state['cache'] = xact.lib.web.util.ResMap()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the entity renderer component.

    """
    if not inputs['control']['ena']:
        return

    list_entities = [{'id':         'A',
                      'list_class': ['foo', 'bar'],
                      'text':       'OOH SCARY'},
                     {'id':         'B',
                      'list_class': ['foo', 'bar'],
                      'text':       'SOMETHING AWFUL'}]

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(test_entities = _test_document(id_res = 'entities'))
    map_res.htm(entities = _render_entities(list_entities))

    if is_unchanged(state, map_res):
        outputs['resources']['ena'] = False
    else:
        outputs['resources']['ena']  = True
        outputs['resources']['list'] = [copy.deepcopy(dict(map_res))]


# -----------------------------------------------------------------------------
def is_unchanged(state, map_res):
    """
    Return true if map_res unchanged from last cached.

    """
    is_unchanged = dict(state['cache']) == dict(map_res)
    state['cache'] = map_res
    return is_unchanged


# -----------------------------------------------------------------------------
def _render_entities(list_entities):
    """
    """
    container = tag.div()
    for entity in list_entities:
        container.add(
            tag.div(
                entity['text'],
                cls = ' '.join(entity['list_class']),
                id  = str(entity['id'])))
    return container.render()

 # -----------------------------------------------------------------------------
def _test_document(id_res):
    """
    Return a 'live' test document for the specified resource.

    """
    title            = 'Test: {id}'.format(id = id_res)
    url_event_stream = '/sub/{id}'.format(id = id_res)
    sse_cmd_connect  = 'connect:{url}'.format(url = url_event_stream)

    doc        = dominate.document(title = title)
    url_roboto = ('https://fonts.googleapis.com/css2'
                  '?family=Roboto:wght@100;300;900&display=swap')
    with doc.head:
        tag.meta(charset = 'utf-8')
        tag.link(rel     = 'stylesheet',
                 href    = url_roboto)
        tag.script(type  = 'text/javascript',
                   src   = 'https://unpkg.com/htmx.org@0.4.0')
        tag.link(rel     = 'stylesheet',
                 type    = 'text/css',
                 href    = xact.lib.web.util.url('style'))
    with doc.head:
        with tag.div(data_hx_sse = sse_cmd_connect):
            tag.div(data_hx_get     = xact.lib.web.util.url(id_res),
                    data_hx_trigger = ', '.join(
                        ('sse:{id}'.format(id = id_res),
                         'load')))
    return doc.render()
