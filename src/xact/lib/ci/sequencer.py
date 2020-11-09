# -*- coding: utf-8 -*-
"""
Continuous integration sequencer for xact.

"""


import collections
import os
import os.path

import xact.lib.fs.search
import xact.sys.exception


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration sequencer component.

    """
    state['size_batch']     = cfg.get('size_batch', 1)
    state['clock']          = None
    state['priority_queue'] = collections.deque()  # Moves from left to right.


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration sequencer component.

    """
    outputs['filepath'].clear()
    outputs['filepath']['ena']  = False
    outputs['filepath']['list'] = []

    if inputs['clock']['ena']:
        state['clock'] = inputs['clock']

    if state['clock'] is None:
        return

    if inputs['low_priority']['ena']:
        for filepath in inputs['low_priority']['list']:

            if '.git' in filepath:
                continue

            if '__pycache__' in filepath:
                continue

            _ensure_present(state['priority_queue'], filepath)

    if inputs['high_priority']['ena']:
        for filepath in inputs['high_priority']['list']:

            if '.git' in filepath:
                continue

            if '__pycache__' in filepath:
                continue

            _ensure_high_priority(state['priority_queue'], filepath)

    if not state['priority_queue']:
        return

    set_filepath = set()
    for idx in range(state['size_batch']):
        try:
            set_filepath.add(_rotate_right(state['priority_queue']))
        except Indexerror:
            break

    if set_filepath:
        outputs['filepath']['ena']  = True
        outputs['filepath']['list'] = list(set_filepath)


# -----------------------------------------------------------------------------
def _ensure_present(deque, item):
    """
    Add item to the LHS (low priority) of the queue if not already present.

    """
    if item not in deque:
        deque.appendleft(item)


# -----------------------------------------------------------------------------
def _ensure_high_priority(deque, item):
    """
    Add or move item to the RHS (high priority) of the queue

    """
    try:
        deque.remove(item)
    except ValueError:
        pass
    deque.append(item)


# -----------------------------------------------------------------------------
def _rotate_right(deque):
    """
    Return RHS (high priority) item and move it to the LHS (low priority) end.

    """
    item = deque.pop()  # pop RHS
    deque.appendleft(item)
    return item
