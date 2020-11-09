# -*- coding: utf-8 -*-
"""
Continuous integration collapsible document renderer for xact.

"""


import collections
import hashlib
import string
import textwrap
import json

import dominate
import dominate.dom_tag
import dominate.svg as svg
import dominate.tags as tag
import dominate.util
import yaml

import xact.util
import xact.lib.web.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration collapsible document renderer component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration collapsible document renderer component.

    """
    outputs['resources']['ena']  = False
    outputs['resources']['list'] = list()

    if not inputs['documents']['ena']:
        return

    css     = dict()
    map_res = xact.lib.web.util.ResMap()
    for doc in inputs['documents']['list']:
        (doc_html, doc_css) = _collapsible_doc_html(title = doc['title'],
                                                    data  = doc['data'])
        css.update(doc_css)
        args = {doc['id']: doc_html}
        map_res.htm(**args)

    map_res.css(style = css)

    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def _collapsible_doc_html(title, data):
    """
    Return a collapsible document as HTML

    """
    css = dict()
    doc = dominate.document(title = title)
    with doc.head:
        tag.meta(charset = 'utf-8')
        tag.link(rel     = 'stylesheet',
                 href    = 'https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;900&display=swap')
        tag.link(rel     = 'stylesheet',
                 type    = 'text/css',
                 href    = xact.lib.web.util.url('style'))
    with doc:
        with tag.div(cls = 'content') as tag_content:
            (foldable_html, foldable_css) = _foldable(data)
            tag_content.add(foldable_html)
            css.update(foldable_css)

    css.update({
        # ':root':           {'--rgb-fg-0':            '#FFFFFF',
        #                     '--rgb-fg-1':            '#CCC7E2',
        #                     '--rgb-bg-0':            '#0C0238',
        #                     '--rgb-bg-1':            '#07031A' },
        ':root':           {'--rgb-bg-0':            '#FFFFFF',
                            '--rgb-bg-1':            '#CCC7E2',
                            '--rgb-fg-0':            '#0C0238',
                            '--rgb-fg-1':            '#07031A' },
        '::selection':     {'background':            'var(--rgb-fg-1)'},
        'html, body':      {'width':                 '100%',
                            'height':                '100%',
                            'display':               'grid',
                            'border':                0,
                            'margin':                0,
                            'padding':               0,
                            'color':                 'var(--rgb-fg-0)',
                            'background-color':      'var(--rgb-bg-0)',
                            'font-family':           '"Roboto", sans-serif',
                            'font-size':             '100%',
                            'font-weight':           '100'},
        '.content':        {'margin':                '5em',
                            'width':                 '95%'}
    })

    return (doc, css)


# -----------------------------------------------------------------------------
def _foldable(data):
    """
    A foldable widget for displaying hierarchical data.

    """
    root_element   = tag.ul(id = 'foldable')
    map_tag_parent = {_id(tuple()): root_element}
    depth_first = xact.util.gen_path_value_pairs_depth_first(data)

    for (path, value) in depth_first:

        path_parent = path[:-1]
        id_parent   = _id(path_parent)
        tag_parent  = map_tag_parent[id_parent]

        is_leaf = not xact.util.is_container(value)
        if is_leaf:
            li_class = 'foldable tree-leaf'
        else:
            li_class = 'foldable tree-branch'

        # The <li> tag holds the content for each leaf/branch.
        id_li  = _id(path)
        tag_li = tag.li(cls = li_class)
        tag_li.add(tag.input_(id = id_li, type = 'checkbox'))
        tag_parent.add(tag_li)

        # Indent the label as appropriate.
        name_li       = str(path[-1]).strip()
        depth_in_tree = len(path)
        indent_size   = depth_in_tree - 1
        inline_style  = 'padding-inline-start: {n}em'.format(n = indent_size)
        tag_li.add(tag.label(name_li, fr = id_li, style = inline_style))

        # Leaves and branches are handled differently.
        if is_leaf:
            tag_li.add(
                tag.div(
                    dominate.util.raw(value),
                    cls = 'tree-leaf-content'))
        else:
            tag_child_list = tag.ul()
            tag_li.add(tag_child_list)
            map_tag_parent[id_li] = tag_child_list

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
    return (root_element, css)


# -----------------------------------------------------------------------------
def _id(data):
    """
    Return a content-based ID for the specified data structure.

    """
    sha = hashlib.sha256()
    sha.update(json.dumps(data).encode('utf-8'))
    return 'ID' + sha.hexdigest()[0:8]