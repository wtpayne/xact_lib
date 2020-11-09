# -*- coding: utf-8 -*-
"""
Continuous integration pylint runner for xact.

"""


import os

import pylint.lint
import pylint.reporters


_NAME_TOOL = 'xact.lib.ci.pylint'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration unit loader component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration unit loader component.

    """
    list_name_output = ('conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for content in inputs['content']['list']:
        filepath           = content['filepath']
        list_nonconformity = _lint(filepath)
        if list_nonconformity:
            outputs['nonconformity']['list'].extend(list_nonconformity)
        else:
            outputs['conformity']['list'].append(dict(
                                            tool     = _NAME_TOOL,
                                            filepath = filepath))

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True


# -----------------------------------------------------------------------------
def _lint(filepath):
    """
    Run pylint.

    """
    dirpath_check = '/media/wtp/Data/dev/xact_lib/src/xact/lib/ci/'
    if '_meta' in filepath:
        return _run_lint(filepath, _args_for_specifications(dirpath_check))
    else:
        return _run_lint(filepath, _args_for_design_docs(dirpath_check))


# -----------------------------------------------------------------------------
def _run_lint(filepath, pylint_args):
    """
    Run pylint.

    """
    pylint_args.append(filepath)
    reporter = pylint.reporters.CollectingReporter()
    setattr(reporter, '_display', _no_op)
    pylint.lint.Run(pylint_args, reporter = reporter, exit = False)

    list_nonconformity = list()
    for msg in reporter.messages:
        list_nonconformity.append(dict(tool     = _NAME_TOOL,
                                       msg_id   = msg.msg_id,
                                       msg      = msg.msg,
                                       filepath = filepath,
                                       line     = msg.line,
                                       col      = msg.column))

    return list_nonconformity

    # TODO: Consider additional fields for customised reporting
    #       for each tool
    # html.escape(msg.msg or '')
    # msg.category,
    # msg.module,
    # msg.obj,
    # msg.path,
    # msg.symbol,


# -----------------------------------------------------------------------------
def _no_op(*args):
    """
    Do nothing.

    """
    pass


# -----------------------------------------------------------------------------
def _args_for_specifications(dirpath_check):
    """
    Return pylint args suitable for linting product specification documents.

    Several whitespace related rules (C0326, C0330,
    W0311) are disabled to permit the vertical
    alignment of operators and operands on consecutive
    lines. This allows us to visually group related
    statements and to readily identify discrepanices.

    Rules I0011, I0012, I0020 and W0511 are disabled
    pending a decision about how to integrate violations
    of these rules into the development process.

    Rules E1129, E0401 and W0622 are disabled because
    of false or inappropriate alarms.

    ---
    type:   function
    ...

    """
    filepath_pylintrc = os.path.join(dirpath_check, 'specification.pylintrc')
    return [
        '--rcfile={file}'.format(file = filepath_pylintrc),
        '--reports=no',
        '--ignore=a0_env'
        '--enable=all',

        # Specification tests for the same function
        # are grouped together in class blocks. This
        # is done to facilitate traceability rather
        # than to make use of object-oriented development
        # techniques. Many class and object oriented
        # design rules are therefore not applicable
        # to specification documents.
        #
        '--disable=R0201',  # no-self-use
        '--disable=R0903',  # too-few-public-methods

        # Test fixtures are bound to the test function
        # by giving an argument the same name as the
        # fixture function. When the fixture function
        # sits in the same file as the test function
        # then it will redefine the outer name (the
        # fixture function) in the course of its normal
        # (and exoected) operation.
        #
        '--disable=W0621',  # redefined-outer-name

        # Tests are clearer if we can use assert
        # function() == True
        #
        '--disable=C0121',  # singleton-comparison

        # Test fixtures need to access protected
        # methods.
        #
        '--disable=W0212',  # protected-access


        '--disable=C0103',  # invalid-name        - TBD
        '--disable=C0111',  # missing-docstring   - TBD

        '--disable=C0326',  # bad-whitespace      - Vertical alignment.
        '--disable=C0330',  # bad-continuation    - Vertical alignment.
        '--disable=W0311',  # bad-indentation     - Vertical alignment.
        '--disable=I0011',  # locally-disabled    - TBD
        '--disable=I0012',  # locally-enabled     - TBD
        '--disable=I0020',  # suppressed-message  - TBD
        '--disable=W0511',  # fixme               - TBD
        '--disable=E1129',  # not-context-manager - False alarms?
        '--disable=E0401',  # import-error        - False alarms?
        '--disable=W0622']  # redefined-builtin   - False alarms?


# -----------------------------------------------------------------------------
def _args_for_design_docs(dirpath_check):
    """
    Return pylint args suitable for linting product design documents.

    Several whitespace related rules (C0326, C0330,
    W0311) are disabled to permit the vertical
    alignment of operators and operands on consecutive
    lines. This allows us to visually group related
    statements and to readily identify discrepanices.

    Rules I0011, I0012, I0020 and W0511 are disabled
    pending a decision about how to integrate violations
    of these rules into the development process.

    Rules E1129, E0401 and W0622 are disabled because
    of false or inappropriate alarms.

    ---
    type:   function
    ...

    """
    filepath_pylintrc = os.path.join(dirpath_check, 'design.pylintrc')
    return [
        '--rcfile={file}'.format(file = filepath_pylintrc),
        '--reports=no',
        '--ignore=a0_env'
        '--enable=all',
        '--disable=C0326',  # bad-whitespace      - Vertical alignment.
        '--disable=C0330',  # bad-continuation    - Vertical alignment.
        '--disable=W0311',  # bad-indentation     - Vertical alignment.
        '--disable=I0011',  # locally-disabled    - TBD
        '--disable=I0012',  # locally-enabled     - TBD
        '--disable=I0020',  # suppressed-message  - TBD
        '--disable=W0511',  # fixme               - TBD
        '--disable=E1129',  # not-context-manager - False alarms?
        '--disable=E0401',  # import-error        - False alarms?
        '--disable=W0622']  # redefined-builtin   - False alarms?
