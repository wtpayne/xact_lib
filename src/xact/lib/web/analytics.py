# -*- coding: utf-8 -*-
"""
Simple analytics component.

"""


import textwrap
import time

import xact.lib.util.simple_controller


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the analytics component.

    """
    state['st_previous'] = None


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the analytics component.

    """
    outputs['rollup']['ena'] = False
    if xact.lib.util.simple_controller.is_new_period(inputs, state, 'min'):
        st_most_recent = inputs['time']['gmtime']

        if state['st_previous'] is None:
            state['st_previous'] = xact.lib.util.simple_controller.prev_time(
                                                st_most_recent, minutes = 1)

        sql_query = ' '.join(textwrap.dedent("""
                SELECT * FROM analytics
                WHERE (minute_idx >= {lo} AND minute_idx < {hi})
                """).splitlines()).format(
                        lo = _minute_index(state['st_previous']),
                        hi = _minute_index(st_most_recent))

        state['st_previous'] = st_most_recent

        outputs['rollup']['ena']   = True
        outputs['rollup']['query'] = sql_query

    outputs['analytics']['ena'] = False
    if inputs['analytics']['ena']:

        outputs['analytics'].clear()
        outputs['analytics']['ena']        = True
        outputs['analytics']['gmtime']     = []
        outputs['analytics']['ts']         = []
        outputs['analytics']['hour_idx']   = []
        outputs['analytics']['minute_idx'] = []

        for analytic in inputs['analytics']['list']:

            gmtime   = inputs['analytics']['gmtime']
            iso_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', gmtime)

            outputs['analytics']['gmtime'].append(iso_time)
            outputs['analytics']['ts'].append(inputs['analytics']['ts'])
            outputs['analytics']['hour_idx'].append(_hour_index(gmtime))
            outputs['analytics']['minute_idx'].append(_minute_index(gmtime))

            for (key, value) in analytic.items():
                if key not in outputs['analytics']:
                    outputs['analytics'][key] = [value]
                else:
                    outputs['analytics'][key].append(value)


# -----------------------------------------------------------------------------
def _minute_index(tup_time):
    """
    Return an integer minute-precision time value to use as the index.

    """
    return int(time.strftime('%Y%j%H%M', tup_time))


# -----------------------------------------------------------------------------
def _hour_index(tup_time):
    """
    Return an integer hour-precision time value to use as the index.

    """
    return int(time.strftime('%Y%j%H', tup_time))