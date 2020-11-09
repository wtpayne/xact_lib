# -*- coding: utf-8 -*-
"""
Filesystem walk component for xact.

"""


import os

import xact.lib.fs.search
import xact.sys.exception


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the filesystem walk component.

    """
    state['generator'] = _batch_filepath_generator(
                                dirpath_root = cfg['dirpath_root'],
                                size_batch   = cfg.get('size_batch', 10),
                                direxcl      = cfg.get('direxcl',    None),
                                pathincl     = cfg.get('pathincl',   None),
                                pathexcl     = cfg.get('pathexcl',   None),
                                do_repeat    = cfg.get('do_repeat',  False),
                                do_halt      = cfg.get('do_halt',    True))


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the filesystem walk component.

    """
    outputs['filepath'].clear()
    outputs['filepath']['ena'] = False

    outputs['filepath']['list'] = next(state['generator'])

    if outputs['filepath']['list']:
        outputs['filepath']['ena']  = True


# -----------------------------------------------------------------------------
def _batch_filepath_generator(dirpath_root,
                              size_batch,
                              direxcl,
                              pathincl,
                              pathexcl,
                              do_repeat,
                              do_halt):
    """
    Yield filepaths from the specified search criteria.

    """
    # For each repeat pass over the filesystem tree.
    while True:

        generator = xact.lib.fs.search.filtered_filepath_generator(
                                                        dirpath_root,
                                                        direxcl  = direxcl,
                                                        pathincl = pathincl,
                                                        pathexcl = pathexcl)
        # For each batch to be returned.
        while True:
            batch = list()
            try:
                for idx in range(size_batch):
                    batch.append(next(generator))
                yield batch
            except StopIteration:
                if batch:
                    yield batch
                break

        if do_repeat:
            continue
        elif do_halt:
            raise xact.sys.exception.RunComplete(return_code = 0)
        else:
            while True:
                yield list()
