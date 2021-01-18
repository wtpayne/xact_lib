# -*- coding: utf-8 -*-
"""
Documentation index generator for xact design documents.

"""

import collections
import os

import dominate
import dominate.tags as tag

import xact.lib.web.util
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration distributor component.

    """
    state['cache'] = set()


# -----------------------------------------------------------------------------
def _update_cache(cache, list_content):
    """
    Updae the cache.

    """
    for map_content in list_content:
        filepath = map_content['filepath']
        cache.add(filepath)


# -----------------------------------------------------------------------------
def _path(filepath, dirpath_root):
    """
    Return the path in the index corresponding to the specified filepath.

    """
    path = filepath[len(dirpath_root):].split(os.sep)
    if path[0] == '':
        path = path[1:]
    return [dirpath_root] + path


# -----------------------------------------------------------------------------
def _url(filepath, view):
    """
    Return the URL for the specified view of the specified file.

    """
    filepath = filepath.replace(os.sep, '.')
    return xact.lib.web.util.url(view + filepath)


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration distributor component.

    """
    xact.util.clear_outputs(outputs             = outputs,
                            list_name_output    = ('resources', ),
                            list_field_to_clear = ('list', ))

    if not inputs['content']['ena']:
        return

    _update_cache(cache        = state['cache'],
                  list_content = inputs['content']['list'])

    list_filepath = list(state['cache'])
    dirpath_root  = os.path.commonpath(list_filepath)
    index         = xact.util.PathDict()
    index.delim   = None
    for filepath in list_filepath:

        item = tag.div()
        item.add(tag.a('source',
                       href = _url(filepath, 'source')))
        index[_path(filepath, dirpath_root)] = item.render()

    css = {
        '#foldable':       {'margin':                0,
                            'padding':               0,
                            'max-width':             '100%',
                            'font-size':             '0.85rem'},
        '#foldable, li':   {'list-style':            'none',
                            'padding':               '0em',
                            'border':                0},
                            #'border-bottom':         '1px solid var(--rgb-fg-0)'},
        '#foldable li:last-child': {
                            'border':                0},
        '#foldable label': {'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'cursor':                'pointer'},
        '#foldable div':   {'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'cursor':                'text'},
        '#foldable input[type=text]': {
                            'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'border':                'none',
                            'outline':               'none',
                            'cursor':                'text',
                            'background-color':      'var(--rgb-bg-0)', # 'transparent',
                            'color':                 'var(--rgb-fg-0)'},
        '#foldable input[type=checkbox]': {
                            'display':               'none'},             # Hide checkbox }
        'li.foldable ul':  {'visibility':            'hidden',            # Fold (hide) by default
                            'opacity':               0,
                            'max-height':            0,                   # CSS bug. Height animation
                            'transition':            'all 0.25s',
                            'padding-inline-start':  0},                  # Depth-dependent indent }
        'li.foldable input:checked ~ ul': {
                            'visibility':            'visible',           # Unfold (shiw) when checked
                            'opacity':               1,
                            'max-height':            '999px',             # Enough height for animation
                            'padding-inline-start':  0},                  # Depth-dependent indent }
        '.foldable':       {'border-bottom':         0}, # '1px solid white'},
        '.tree-leaf':      {'display':               'grid',
                            'grid-template-rows':    '1fr',
                            'grid-template-columns': '14em 30em'},
        '.tree-leaf-content': {
                            'text-align':            'justify'},
    }



    doc = dominate.document(title = 'Index')
    with doc.head:
        tag.meta(charset = 'utf-8')
        tag.link(rel     = 'stylesheet',
                 href    = 'https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;900&display=swap')
        tag.link(rel     = 'stylesheet',
                 type    = 'text/css',
                 href    = xact.lib.web.util.url('style'))
    with doc:
        with tag.div(cls = 'content') as tag_content:
            (foldable_html, foldable_css) = xact.lib.web.util.foldable(index)
            tag_content.add(foldable_html)
            css.update(foldable_css)

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(index2 = doc.render())
    map_res.css(style = css)

    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]
