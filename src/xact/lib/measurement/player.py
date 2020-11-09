# -*- coding: utf-8 -*-
"""
Xact component to play back prerecorded data in dill format.

Expects newline-delimited text files where each
line in the file is a python dict which has been
pickled and then base64 encoded.

"""


import base64
import os
import os.path
import pathlib

import dill


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data recorder.

    """
    dirpath_rec = cfg['dirpath_rec']
    assert os.path.isdir(dirpath_rec)

    if dirpath_rec[-1] != os.sep:
        dirpath_rec += os.sep

    glob_rec                   = pathlib.Path(dirpath_rec).rglob('*.rec')
    tup_filepath_rec           = tuple((str(obj_path) for obj_path in glob_rec))
    iter_filepath_rec          = iter(tup_filepath_rec)
    state['iter_filepath_rec'] = iter_filepath_rec
    state['file']              = None


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data recorder.

    """
    assert inputs['clock']['ena']

    if state['file'] is None:
        try:
            filepath_next = next(state['iter_filepath_rec'])
        except StopIteration as err:
            raise xact.sys.exception.RunComplete(0)
        state['file'] = open(filepath_next, 'rb')

    try:
        line = next(state['file']).strip()
    except StopIteration:
        state['file'].close()
        state['file'] = None
        return

    pickle = base64.b64decode(line)
    frame  = dill.loads(pickle)

    for key in outputs.keys():
        outputs[key].update(frame[key])


