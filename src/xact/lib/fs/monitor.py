# -*- coding: utf-8 -*-
"""
Filesystem monitor component for xact.

Monitor one or more directories for content and changes.

"""


import collections
import itertools
import multiprocessing
import os
import queue
import sys
import time

import watchdog.observers
import watchdog.events

import xact.lib.fs.search
import xact.sys.exception
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the filesystem monitor component.

    """
    state['generator'] = _batch_filepath_generator(
                            dirpath_root     = cfg['dirpath_root'],
                            pathincl         = cfg.get('pathincl',     None),
                            pathexcl         = cfg.get('pathexcl',     None),
                            direxcl          = cfg.get('direxcl',      None),
                            size_batch       = cfg.get('batch_size',   50),
                            do_changes       = cfg.get('changes',      False),
                            do_static_files  = cfg.get('static_files', True),
                            do_repeat_static = cfg.get('do_repeat',    False),
                            do_halt_after    = cfg.get('halt_after',   True))


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the filesystem monitor component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('filepath',),
                    list_field_to_clear = ('list', ))

    if not inputs['control']['ena']:
        return

    outputs['filepath']['list'] = next(state['generator'])
    if outputs['filepath']['list']:
        outputs['filepath']['ena'] = True


# -----------------------------------------------------------------------------
def _batch_filepath_generator(dirpath_root,
                              pathincl,
                              pathexcl,
                              direxcl,
                              size_batch,
                              do_changes,
                              do_static_files,
                              do_repeat_static,
                              do_halt_after):
    """
    Yield filepaths from the specified search criteria.

    """
    if not isinstance(dirpath_root, list):
        list_dirpath_root = [dirpath_root]
    else:
        list_dirpath_root = dirpath_root

    if do_changes:
        modified_files = _gen_list_filepath_modified(list_dirpath_root,
                                                     direxcl  = direxcl,
                                                     pathincl = pathincl,
                                                     pathexcl = pathexcl)
    else:
        modified_files = None

    # For each repeat pass over the filesystem tree.
    while True:

        static_files = _generate_all_static_files(list_dirpath_root,
                                                  direxcl  = direxcl,
                                                  pathincl = pathincl,
                                                  pathexcl = pathexcl)

        # For each batch of filepaths to be returned (simulation step).
        while True:
            batch = list()
            # Start by adding any recently modified files.
            if do_changes:
                batch.extend(next(modified_files))
            if not do_static_files:
                yield batch
            # Now fill the rest of the batch up with static files.
            try:
                while len(batch) < size_batch:
                    batch.append(next(static_files))
                yield batch
            except StopIteration:
                if batch:
                    yield batch
                break
        if do_repeat_static:
            continue
        elif do_halt_after:
            raise xact.sys.exception.RunComplete(return_code = 0)
        else:
            do_static_files = False
            continue


# -----------------------------------------------------------------------------
def _generate_all_static_files(list_dirpath_root, pathincl, pathexcl, direxcl):
    """
    Yield filepaths of matching files from the list of roots.

    """
    list_generator = list()
    for dirpath_root in list_dirpath_root:
        list_generator.append(
            xact.lib.fs.search.filtered_filepath_generator(
                                                        dirpath_root,
                                                        direxcl  = direxcl,
                                                        pathincl = pathincl,
                                                        pathexcl = pathexcl))
    return itertools.chain.from_iterable(list_generator)


# -----------------------------------------------------------------------------
def _gen_list_filepath_modified(list_dirpath_root,
                                direxcl,
                                pathincl,
                                pathexcl):
    """
    Yield a list of filepaths of recently modified matching files.

    """
    list_exclude = list()
    if direxcl:
        list_exclude.extend(direxcl)
    if pathexcl:
        list_exclude.extend(pathexcl)
    indicator = xact.lib.fs.search.get_dual_regex_indicator_fcn(
                                                        incl = pathincl,
                                                        excl = list_exclude)
    list_tup_observer_handler = _list_tup_observer_handler(list_dirpath_root)

    while True:
        list_path = list()
        for (observer, handler) in list_tup_observer_handler:
            list_path.extend(
                (path for path in _modified_files(handler) if indicator(path)))
        yield sorted(list_path)


# -----------------------------------------------------------------------------
def _list_tup_observer_handler(list_dirpath_root):
    """
    Return a list of change-observer, change-handler tuple pairs.

    """
    list_tup_observer_handler = list()
    for dirpath_root in list_dirpath_root:
        observer  = watchdog.observers.Observer()
        handler   = EventEnqueueingHandler()
        observer.schedule(event_handler = handler,
                          path          = dirpath_root,
                          recursive     = True)
        observer.start()
        list_tup_observer_handler.append((observer, handler))
    return list_tup_observer_handler


# -----------------------------------------------------------------------------
def _modified_files(handler):
    """
    Return a list of modified files from the specified event handler.

    """
    list_filepath  = list()
    list_tup_event = handler.get()
    for tup_event in list_tup_event:

        if tup_event.is_dir:
            continue

        if tup_event.path_dst is not None:
            list_filepath.append(tup_event.path_dst)
            continue

        if tup_event.path_src is not None:
            list_filepath.append(tup_event.path_src)
            continue

    return list_filepath


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