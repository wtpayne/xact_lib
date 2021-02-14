# -*- coding: utf-8 -*-
"""
Cache pre-pipeline component.

"""


import sqlite3

import xact.util.serialization


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the cache reader component.

    """
    state['connection'] = sqlite3.connect(cfg['filepath_db'])
    state['cursor']     = state['connection'].cursor()
    _ensure_cache_exists(cursor = state['cursor'])


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the cache reader component.

    """
    xact.util.clear_outputs(outputs             = outputs,
                            list_name_output    = ('cached_results',
                                                   'params_compute',
                                                   'params_cache'),
                            list_field_to_clear = ('list', ))

    if not inputs['parameters']['ena']:
        return

    for parameters in inputs['parameters']['list']:
        cache_line_item = _try_read_cache(cursor     = state['cursor'],
                                          parameters = parameters)
        if cache_line_item:
            outputs['cached_results']['list'].append(cache_line_item)
        else:
            outputs['params_compute']['list'].append(parameters)
            outputs['params_cache']['list'].append(parameters)

    if outputs['params_compute']['list']:
        outputs['params_compute']['ena'] = True

    if outputs['params_cache']['list']:
        outputs['params_cache']['ena'] = True


# -----------------------------------------------------------------------------
def _ensure_cache_exists(cursor):
    """
    Make sure the cache table exists in the database.

    """
    cursor.execute(' '.join((
            'CREATE TABLE IF NOT EXISTS cache',
            '(key TEXT PRIMARY KEY, value BLOB NOT NULL);')))


# -----------------------------------------------------------------------------
def _try_read_cache(cursor, parameters):
    """
    Try to read a line item from the cache.

    """
    try:
        cursor.execute(' '.join((
                'SELECT value FROM cache',
                'WHERE key = "{key}";'.format(
                        key = xact.util.serialization.hexdigest(parameters)))))
    except sqlite3.OperationalError as err:
        raise
    result = cursor.fetchone()
    if result:
        print('READ FROM CACHE: ' + parameters)
        return xact.util.serialization.deserialize(result[0])
    else:
        return None
