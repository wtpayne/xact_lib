# -*- coding: utf-8 -*-
"""
Filesystem watchdog component for xact.

"""


import collections
import multiprocessing
import queue
import sys
import time

import watchdog.observers
import watchdog.events

import xact.lib.fs.search


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the filesystem watchdog component.

    """
    state['generator'] = _filtered_filepath_generator(
                                      path      = cfg['dirpath_root'],
                                      recursive = cfg.get('recursive', True),
                                      pathincl  = cfg.get('pathincl',  None),
                                      pathexcl  = cfg.get('pathexcl',  None))


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the filesystem watchdog component.

    """
    outputs['filepath'].clear()
    outputs['filepath']['ena']  = False
    outputs['filepath']['list'] = next(state['generator'])
    if outputs['filepath']['list']:
        outputs['filepath']['ena'] = True

# -----------------------------------------------------------------------------
def _filtered_filepath_generator(path, recursive, pathincl, pathexcl):
    """
    Yield filepaths of matching modified files.

    """
    observer  = watchdog.observers.Observer()
    handler   = EventEnqueueingHandler()
    indicator = xact.lib.fs.search.get_dual_regex_indicator_fcn(
                                                            incl = pathincl,
                                                            excl = pathexcl)

    observer.schedule(event_handler = handler,
                      path          = path,
                      recursive     = recursive)
    observer.start()

    while True:
        yield sorted(
            (path for path in _filepath_generator(handler) if indicator(path)))


# -----------------------------------------------------------------------------
def _filepath_generator(handler):
    """
    Yield filepaths from the specified handler.

    """
    for event in handler.get():

        if event.is_dir:
            continue

        if event.path_dst is not None:
            filepath = event.path_dst
            yield filepath
            continue

        if event.path_src is not None:
            filepath = event.path_src
            yield filepath
            continue


# =============================================================================
TupEvent = collections.namedtuple(
                        'TupEvent', ['type', 'path_src', 'path_dst', 'is_dir'])


# =============================================================================
class EventEnqueueingHandler(watchdog.events.FileSystemEventHandler):
    """
    Enqueues watchdog filesystem events for xact to pick up.

    """

    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Construct a EventEnqueueingHandler instance.

        """
        super(EventEnqueueingHandler, self).__init__()
        self.queue = multiprocessing.Queue()


    # -------------------------------------------------------------------------
    def on_moved(self, event):
        """
        Dispatch watchdog.events.FileMovedEvent events.

        """
        super(EventEnqueueingHandler, self).on_moved(event)
        self._enqueue(event)

    # -------------------------------------------------------------------------
    def on_created(self, event):
        """
        Dispatch watchdog.events.FileCreatedEvent events.

        """
        super(EventEnqueueingHandler, self).on_created(event)
        self._enqueue(event)

    # -------------------------------------------------------------------------
    def on_deleted(self, event):
        """
        Dispatch watchdog.events.FileDeletedEvent events.

        """
        super(EventEnqueueingHandler, self).on_deleted(event)
        self._enqueue(event)

    # -------------------------------------------------------------------------
    def on_modified(self, event):
        """
        Dispatch watchdog.events.FileModifiedEvent events.

        """
        super(EventEnqueueingHandler, self).on_modified(event)
        self._enqueue(event)

    # -------------------------------------------------------------------------
    def _enqueue(self, event):
        """
        Add the specified event to the queue.

        """
        path_src   = None
        path_dst   = None
        is_dir     = False

        if hasattr(event, 'src_path'):
            if event.src_path:
                path_src = event.src_path

        if hasattr(event, 'dest_path'):
            if event.dest_path:
                path_dst = event.dest_path

        if hasattr(event, 'is_directory'):
            if event.is_directory:
                is_dir = event.is_directory

        tup_event = TupEvent(type     = event.event_type,
                             path_src = path_src,
                             path_dst = path_dst,
                             is_dir   = is_dir)
        self.queue.put(tup_event, block = False)

    # -------------------------------------------------------------------------
    def get(self):
        """
        Get all events currently on the queue.

        """
        set_tup_event = set()
        while True:
            try:
                set_tup_event.add(self.queue.get(block = False))
            except queue.Empty:
                break
        list_tup_event = list(set_tup_event)
        return(list_tup_event)