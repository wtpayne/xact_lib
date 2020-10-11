# -*- coding: utf-8 -*-
"""
Xact component to record data in dill format.

Writes newline-delimited text files where each
line in the file is a python dict which has been
pickled and then base64 encoded.

"""


import os
import os.path

import dill

import xact.lib.measurement


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the data recorder.

    """
    rootpath_rec = cfg['rootpath_rec']
    if not os.path.isdir(rootpath_rec):
        os.makedirs(rootpath_rec)

    cfg_ident    = runtime['id']
    dirname_sys  = cfg_ident['id_system']
    dirname_run  = '_'.join((cfg_ident['ts_run'],
                             cfg_ident['id_run'],
                             cfg_ident['id_cfg']))
    dirname_node = '_'.join((cfg_ident['id_host'],
                             cfg_ident['id_process'],
                             cfg_ident['id_node']))

    dirpath_rec = os.path.join(
                        rootpath_rec, dirname_sys, dirname_run, dirname_node)

    os.makedirs(dirpath_rec)

    # assert sorted(list(outputs.keys())) == sorted(list(inputs.keys()))

    state['dirpath_rec'] = dirpath_rec
    state['id_block']    = None
    state['file']        = None
    state['protocol']    = dill.HIGHEST_PROTOCOL
    state['size_block']  = 1000  # Frames
    state['format_name'] = '{{id_block:0{digits}d}}.b64dill{ver}.rec'.format(
                                        digits = len(str(state['size_block'])),
                                        ver    = state['protocol'])


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the data recorder.

    """
    assert inputs['clock']['ena']
    file = xact.lib.measurement.file_rec(idx   = inputs['clock']['idx'],
                                         state = state,
                                         mode  = 'wb')
    for key in outputs.keys():
        outputs[key].clear()
        outputs[key].update(inputs[key])
    xact.lib.measurement.write_frame(file, inputs, state['protocol'])
    file.flush(),
    os.fsync(file.fileno())