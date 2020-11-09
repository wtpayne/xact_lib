# -*- coding: utf-8 -*-
"""
Continuous integration file loader for xact.

"""


import os

import xact.lib.ci.constants
import xact.lib.ci.exceptions


_NAME_TOOL = 'xact.lib.ci.loader'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration file loader component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration file loader component.

    """
    list_name_output = ('content', 'conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if inputs['filepath']['ena']:
        for filepath in inputs['filepath']['list']:
            try:
                content = _read_file(filepath)
            except xact.lib.ci.exceptions.Nonconformity as err:
                outputs['nonconformity']['list'].append(err.asdict())
            else:
                outputs['conformity']['list'].append(dict(
                                                    tool     = _NAME_TOOL,
                                                    filepath = filepath))
                outputs['content']['list'].append(dict(
                                                    filepath = filepath,
                                                    content  = content))

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True


# -----------------------------------------------------------------------------
def _read_file(filepath):
    """
    Return the content of the specified filepath.

    Throws xact.lib.ci.exceptions.Nonconformity on error.

    """
    with open(filepath, 'rb') as file:

        try:
            encoded_content = file.read()
        except (IOError, OSError) as err:
            msg_id = xact.lib.ci.constants.DESIGN_FILE_READ_ERROR
            raise xact.lib.ci.exceptions.Nonconformity(
                                                tool     = _NAME_TOOL,
                                                msg_id   = msg_id,
                                                msg      = str(err),
                                                filepath = filepath,
                                                line     = 0,
                                                col      = 0)

        try:
            content = encoded_content.decode('utf-8')
        except ValueError as err:
            msg_id = xact.lib.ci.constants.DESIGN_FILE_DECODING_ERROR
            raise xact.lib.ci.exceptions.Nonconformity(
                                                tool     = _NAME_TOOL,
                                                msg_id   = msg_id,
                                                msg      = str(err),
                                                filepath = filepath,
                                                line     = 0,
                                                col      = 0)

    return content