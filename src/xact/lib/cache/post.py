# -*- coding: utf-8 -*-
"""
Cache post-pipeline component.

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
                            list_name_output    = ('results', ),
                            list_field_to_clear = ('list', ))

    if inputs['cached_results']['ena']:
        outputs['results']['list'].extend(inputs['cached_results']['list'])

    if inputs['computed_results']['ena']:
        outputs['results']['list'].extend(inputs['computed_results']['list'])

        for (parameters, result) in zip(
            inputs['parameters']['list'], inputs['computed_results']['list']):
            _try_write_cache(connection = state['connection'],
                             cursor     = state['cursor'],
                             parameters = parameters,
                             item       = result)
        return


# -----------------------------------------------------------------------------
def _ensure_cache_exists(cursor):
    """
    Make sure the cache table exists in the database.

    """
    cursor.execute(' '.join((
            'CREATE TABLE IF NOT EXISTS cache',
            '(key TEXT PRIMARY KEY, value BLOB NOT NULL);')))


# -----------------------------------------------------------------------------
def _try_write_cache(connection, cursor, parameters, item):
    """
    Try to write a line item to the cache.

    """
    try:
        cursor.execute(' '.join((
                'INSERT INTO cache VALUES',
                '("{key}", "{value}");'.format(
                        key   = xact.util.serialization.hexdigest(parameters),
                        value = xact.util.serialization.serialize(item)))))
    except sqlite3.OperationalError as err:
        raise

    connection.commit()

    print('INSERT OK')