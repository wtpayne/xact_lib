# -*- coding: utf-8 -*-
"""
Simple controller component to set the real-time step rate of a system.

"""


import datetime
import time

import xact.sys.exception


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the controller.

    """
    state['max_idx'] = None
    if 'max_idx' in cfg:
        state['max_idx'] = cfg['max_idx']

    state['period_secs'] = None
    if 'frequency_hz' in cfg:
        state['period_secs'] = 1 / cfg['frequency_hz']

    state['idx'] = 0


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Send a message once per period.

    """
    if state['period_secs'] is not None:
        time.sleep(state['period_secs'])
        # TODO: Consider more accurate sleeps, based on elapsed time.

    for key in outputs.keys():
        outputs[key]['ena']    = True
        outputs[key]['idx']    = state['idx']
        outputs[key]['ts']     = time.monotonic()
        outputs[key]['gmtime'] = time.gmtime()

    state['idx'] = state['idx'] + 1
    if state['max_idx'] is not None:
        if state['idx'] > state['max_idx']:
            raise xact.sys.exception.RunComplete(0)


# -----------------------------------------------------------------------------
def prev_time(gmtime, **kwargs):
    """
    Return the time

    """
    dt_most_recent = datetime.datetime.fromtimestamp(time.mktime(gmtime))
    dt_previous    = dt_most_recent - datetime.timedelta(**kwargs)
    return dt_previous.timetuple()


# -----------------------------------------------------------------------------
def is_new_period(inputs, state, name_period):
    """
    Return true if we are in a new period. False otherwise

    """
    if not inputs['control']['ena']:
        return False

    gmt = inputs['control']['gmtime']
    if name_period == 'mon':
        id_period = (gmt.tm_year, gmt.tm_mon),
    elif name_period == 'week':
        dt_day    = datetime.datetime(gmt.tm_year, gmt.tm_mon, gmt.tm_mday)
        iso_date  = dt_day.isocalendar()
        iso_week  = iso_date[1]
        id_period = (iso_week,)
    elif name_period == 'day':
        id_period = (gmt.tm_year, gmt.tm_yday),
    elif name_period == 'hour':
        id_period = (gmt.tm_year, gmt.tm_yday, gmt.tm_hour),
    elif name_period == 'min':
        id_period = (gmt.tm_year, gmt.tm_yday, gmt.tm_hour, gmt.tm_min),
    elif name_period == 'sec':
        id_period = (gmt.tm_year, gmt.tm_yday,
                     gmt.tm_hour, gmt.tm_min, gmt.tm_sec)
    else:
        raise RuntimeError('Did not recognize name_period.')

    recent_period = 'recent_' + name_period
    if recent_period not in state:
        state[recent_period] = []

    is_new = id_period not in state[recent_period]
    if is_new:
        state[recent_period].append(id_period)
        if len(state[recent_period]) > 2:
            state[recent_period] = sorted(state[recent_period])[2:]

    return is_new