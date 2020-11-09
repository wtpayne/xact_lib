# -*- coding: utf-8 -*-
"""
Continuous integration python pydocstyle checker for xact.

"""


import pydocstyle
import pydocstyle.checker


_NAME_TOOL = 'xact.lib.ci.pydocstyle'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration python pydocstyle checker component.

    """
    state['list_ignore'] = cfg['list_ignore']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration python pydocstyle checker component.

    """
    list_name_output = ('conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for content in inputs['content']['list']:

        filepath   = content['filepath']
        convention = pydocstyle.violations.conventions['pep257']
        list_all   = list(pydocstyle.checker.check(
                                            (filepath,),
                                            select            = convention,
                                            ignore_decorators = None))

        list_nonconformity = list()
        for item in list_all:
            try:
                code = item.code
            except AttributeError:
                continue
            else:
                if code not in state['list_ignore']:
                    list_nonconformity.append(item)


        if not list_nonconformity:
            outputs['conformity']['list'].append(dict(
                                            tool     = _NAME_TOOL,
                                            filepath = filepath))

        for item in list_nonconformity:
            message = '{short_desc}\n{explanation}'.format(
                                            short_desc  = item.short_desc,
                                            explanation = item.explanation)

            outputs['nonconformity']['list'].append(dict(
                                            tool     = _NAME_TOOL,
                                            msg_id   = item.code,
                                            msg      = message,
                                            filepath = filepath,
                                            line     = item.line,
                                            col      = 0))
                                            #   doc     = item.explanation
                                            #   lines   = item.lines
                                            #   def     = item.definition

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True
