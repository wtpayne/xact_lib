# -*- coding: utf-8 -*-
"""
Live reload node.

"""


import importlib
import os.path
import time

import xact.log


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the live reload component.

    """
    state['runtime']       = runtime
    state['cfg']           = cfg
    state['py_module']     = cfg['py_module']
    state['module']        = importlib.import_module(state['py_module'])
    state['filepath']      = state['module'].__file__
    state['last_modified'] = os.path.getmtime(state['filepath'])
    state['module'].reset(runtime, cfg, inputs, state, outputs)


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the live reload component.

    """
    modified = os.path.getmtime(state['filepath'])
    if state['last_modified'] < modified:
        state['last_modified'] = modified
        _try_reload(inputs, state, outputs)
    _try_step(inputs, state, outputs)


# -----------------------------------------------------------------------------
def _try_reload(inputs, state, outputs):
    """
    Try to reload the specified component.

    """
    err_msg = None
    while True:
        try:
            importlib.reload(state['module'])
        except Exception as err:
            if err_msg != str(err):
                err_msg = str(err)
                xact.log.logger.exception(
                            'Live module reload failed for "{module}"',
                            module = state['py_module'])

            time.sleep(2)
        else:
            # Reset on successful reload
            state['module'].reset(state['runtime'],
                                  state['cfg'],
                                  inputs,
                                  state,
                                  outputs)
            return


# -----------------------------------------------------------------------------
def _try_step(inputs, state, outputs):
    """
    Try to step the specified component.

    """
    err_msg = None
    while True:
        try:
            state['module'].step(inputs, state, outputs)
        except (Exception) as err:
            if err_msg != str(err):
                err_msg = str(err)
                xact.log.logger.exception(
                            'Live module step function failed for "{module}"',
                            module = state['py_module'])
            time.sleep(2)
            _try_reload(inputs, state, outputs)
        else:
            return