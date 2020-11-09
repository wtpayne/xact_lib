# -*- coding: utf-8 -*-
"""
Continuous integration nonconformity reporter for xact.

"""


import collections
import hashlib
import json
import os
import string
import textwrap

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
    Reset the continuous integration nonconformity reporter component.

    """
    state['cache'] = dict()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration nonconformity reporter component.

    Turns a list of nonconformity data structures into
    a list of report document data structures.

    """
    outputs['documents']['ena'] = False

    if inputs['nonconformity']['ena']:
        list_nonconformity = inputs['nonconformity']['list']
    else:
        list_nonconformity = []

    if inputs['conformity']['ena']:
        list_conformity = inputs['conformity']['list']
    else:
        list_conformity = []

    _update_cache(cache              = state['cache'],
                  list_conformity    = list_conformity,
                  list_nonconformity = list_nonconformity)

    cfg = {
        'nc_fp': {
            'title': 'Nonconformity by filepath',
            'order': ('_root', '_branch', '_title')
        },
        'nc_id': {
            'title': 'Nonconformity by id',
            'order': ('tool', 'msg_id', 'filepath', '_title')
        }
    }

    map_report = _report(cfg   = cfg,
                         cache = state['cache'])

    if map_report is None:
        return

    outputs['documents']['ena'] = True
    outputs['documents']['list'] = []
    for (id_report, cfg_report) in cfg.items():
        outputs['documents']['list'].append({
            'id':    id_report,
            'title': cfg_report['title'],
            'data':  dict(map_report[id_report])})


# -----------------------------------------------------------------------------
def _report(cfg, cache):
    """
    Return a report dict.

    """
    report = dict()
    for key in cfg.keys():
        report[key] = xact.util.PathDict()
        report[key].delim = None

    list_path = list(path for (_, path) in cache.keys())
    if not list_path:
        return report

    dirpath_root = os.path.commonpath(list_path)
    format_title = '{msg_id} - ({line:03d}:{col:02d})'

    for item in _iter_items(cache):

        # Add computed fields.
        item['_root'] = dirpath_root
        branch = item['filepath'][len(dirpath_root):].split(os.sep)
        if branch[0] == '':
            branch = branch[1:]
        item['_branch'] = branch
        item['_title']  = format_title.format(**item)

        uri_file  = 'file://{path}&line={line}'.format(
                                                    path = item['filepath'],
                                                    line = item['line'])
        uri_subl  = 'subl://open?url={uri_file}'.format(uri_file = uri_file)
        link_subl = '<a href = {uri_subl}>subl</a>'.format(uri_subl = uri_subl)

        # Format message
        list_para = list()
        for para in item['msg'].split('\n\n'):
            list_para.append(textwrap.dedent(para))
        # msg = '<p>' + '</p><p>'.join(list_para) + '</p>'
        msg = '<br><br>'.join(list_para) + '<br>'
        msg += '[{link_subl}]'.format(link_subl = link_subl)

        # import pprint
        # print('#' * 80)
        # pprint.pprint(msg)
        # print('.' * 80)
        # pprint.pprint(list_para)
        # print('#' * 80)
        # print('')

        # Fill report data structure.
        for (id_report, cfg_report) in cfg.items():
            path = list()
            for id_part in cfg_report['order']:
                path_part = item[id_part]
                if isinstance(path_part, list):
                    path.extend(path_part)
                else:
                    path.append(path_part)
            report[id_report][path] = msg

    return report


# -----------------------------------------------------------------------------
def _iter_items(cache):
    """
    Yield each item in the cache.

    """
    for set_item in cache.values():
        for tup_item in set_item:
            yield dict(tup_item)


# -----------------------------------------------------------------------------
def _update_cache(cache, list_conformity, list_nonconformity):
    """
    Update the cache, removing stale items and adding new ones.

    """
    _remove_conforming_items_from_cache(cache, list_conformity)
    _remove_stale_items_from_cache(cache, list_nonconformity)
    _add_new_items_to_cache(cache, list_nonconformity)


# -----------------------------------------------------------------------------
def _remove_conforming_items_from_cache(cache, list_conformity):
    """
    Remove conforming items from the cache.

    """
    set_conforming_keys = set()
    for item in list_conformity:
        key = (item['tool'], item['filepath'])
        set_conforming_keys.add(key)

    for key in set_conforming_keys:
        cache.pop(key, None)


# -----------------------------------------------------------------------------
def _remove_stale_items_from_cache(cache, list_nonconformity):
    """
    Remove stale items from the cache.

    """
    set_stale_keys = set()
    for item in list_nonconformity:
        key = (item['tool'], item['filepath'])
        set_stale_keys.add(key)

    for key in set_stale_keys:
        cache.pop(key, None)


# -----------------------------------------------------------------------------
def _add_new_items_to_cache(cache, list_nonconformity):
    """
    Add new items to the cache, indexed by the specified key.

    """
    for item in list_nonconformity:
        key = (item['tool'], item['filepath'])
        if key not in cache:
            cache[key] = set()
        cache[key].add(tuple(item.items()))
