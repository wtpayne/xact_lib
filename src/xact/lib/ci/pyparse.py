# -*- coding: utf-8 -*-
"""
Continuous integration design document renderer for xact.

"""


import ast
import os

import xact.lib.ci.constants
import xact.lib.ci.exceptions


_NAME_TOOL = 'xact.lib.ci.pyparse'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration design document renderer component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration design document renderer component.

    """
    list_name_output = ('content', 'conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for content in inputs['content']['list']:
        filepath = content['filepath']
        (dirpath, filename) = os.path.split(filepath)
        try:
            content['ast'] = ast.parse(content['content'],
                                       filename = filename,
                                       mode     = 'exec')
            outputs['content']['list'].append(content)
        except SyntaxError as err:

            # Draw a caret under the error location
            # so it is easy for the user to spot
            # where the error is.
            #
            idx_newline = str(err.text)[0:int(err.offset)].rfind('\n')
            col = err.offset - (idx_newline + 1)
            location_indicator = (' ' * col) + '^'
            msg = 'Syntax error:\n{msg}\n{loc}'.format(
                                                    msg = err.text,
                                                    loc = location_indicator)

            msg_id = xact.lib.ci.constants.DESIGN_FILE_SYNTAX_ERROR
            outputs['nonconformity']['list'].append(dict(
                                                    tool     = _NAME_TOOL,
                                                    msg_id   = msg_id,
                                                    msg      = msg,
                                                    filepath = filepath,
                                                    line     = 0,
                                                    col      = col))

        else:
            outputs['conformity']['list'].append(dict(
                                                    tool     = _NAME_TOOL,
                                                    filepath = filepath))

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True
