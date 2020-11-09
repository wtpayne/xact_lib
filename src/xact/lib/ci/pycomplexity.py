# -*- coding: utf-8 -*-
"""
Continuous integration python complexity checker for xact.

"""

import json
import os.path

import bunch
import radon.raw
import radon.complexity
import radon.metrics

import xact.lib.ci.python_source


_NAME_TOOL = 'xact.lib.ci.pycomplexity'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration python complexity checker component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration python complexity checker component.

    """
    list_name_output = ('conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for content in inputs['content']['list']:

        filepath = content['filepath']

        # Gather nonconformity messages
        # and complexity metrics for each
        # function in the file.
        list_nonconformity = []
        complexity_log     = {}
        module_name        = xact.lib.ci.python_source.get_module_name(
                                                                    filepath)

        for function in xact.lib.ci.python_source.gen_functions_and_methods(
                                            module_name = module_name,
                                            source_text = content['content'],
                                            root_node   = content['ast']):

            (raw, mccabe, halstead, ratios) = _analyse(function)

            # Send metrics to nonconformity decision maker.
            setattr(function, 'da_raw',      raw)
            setattr(function, 'da_mccabe',   mccabe)
            setattr(function, 'da_halstead', halstead)
            setattr(function, 'da_ratios',   ratios)
            setattr(function, 'da_filepath', filepath)
            list_nonconformity.extend(_generate_nonconformities(function))

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
def _analyse(function):
    """
    Return complexity analysis for function.

    ---
    type:   function
    ...

    """
    # Raw metrics.
    raw = radon.raw.analyze(function.da_text)

    # McCabe cyclomatic complexity.
    mccabe_list = radon.complexity.cc_visit_ast(function)
    assert len(mccabe_list) == 1
    mccabe = mccabe_list[0]

    # Halstead maintainability index.
    halstead = radon.metrics.h_visit_ast(function)

    # Ratios.
    comment_number = float(raw.comments) + 1.0  # Add 1 to prevend div by zero
    ratios = bunch.Bunch({
        'lloc_pcl':   float(raw.lloc)              / comment_number,
        'mccabe_pcl': float(mccabe.complexity)     / comment_number,
        'effort_pcl': float(halstead.total.effort) / comment_number
    })

    return (raw, mccabe, halstead, ratios)


# -----------------------------------------------------------------------------
def _generate_nonconformities(fcn):
    """
    Report complexity nonconformities to the build_monitor.

    Raw metrics:
    ===========
    loc      - Number of lines including comments and whitespace.
    sloc     - Number of lines including comments but not whitespace.
    lloc     - Logical lines (including comments).
    comments - Comment lines
    multi    - lines taken up by multiline strings
    blank    - whitespace-only lines

    McCabe metrics:
    ===============
    name
    lineno
    col_offset
    is_method
    classname
    endline
    closures
    complexity

    Halstead metrics:
    =================
    h1                - Num distinct operators - operator vocabulary.
    h2                - Num distinct operands - operand vocabulary.
    vocabulary        - Operator vocabulary + operand vocabulary.
    N1                - Num operator occurrances - length in operators.
    N2                - Num operand occurrances - length operands.
    length            - Operator occurrances + operand occurrances.
    calculated_length - vocabulary * log(vocabulary).
    volume            - length * log(vocabulary).
    difficulty        - distinct operators * avg. uses of each operand.
    effort            - difficulty * volume.
    time              - scaled effort (seconds).
    bugs              - scaled volume.

    ---
    type:   function
    ...

    """
    # PyLint style msg_ig (in range not used by PyLint) R for Refactor: R####.
    for (msg_id, name, metric, limit) in (
            ('R0961', 'Logical lines',     fcn.da_raw.lloc,                    60),
            ('R0962', 'McCabe complexity', fcn.da_mccabe.complexity,           18),
            ('R0963', 'Halstead vocab.',   fcn.da_halstead.total.vocabulary,   50),
            ('R0964', 'Halstead length',   fcn.da_halstead.total.length,       50),
            ('R0965', 'Halstead effort',   fcn.da_halstead.total.effort,      800),
            ('R0965', 'Halstead time',     fcn.da_halstead.total.time,        100),
            ('R0966', 'Halstead bugs',     fcn.da_halstead.total.bugs,       0.08),
            ('R0967', 'lloc/comment',      fcn.da_ratios.lloc_pcl,           25.0),
            ('R0968', 'mmcabe/comment',    fcn.da_ratios.mccabe_pcl,          7.0),
            ('R0969', 'effort/comment',    fcn.da_ratios.effort_pcl,        300.0)):
        if metric > limit:

            msg = '{name} {metric} > {limit} in {fcn}'.format(
                                                      name   = name,
                                                      metric = metric,
                                                      limit  = limit,
                                                      fcn    = fcn.da_addr)

            yield dict(tool     = _NAME_TOOL,
                       msg_id   = msg_id,
                       msg      = msg,
                       filepath = fcn.da_filepath,
                       line     = fcn.lineno,
                       col      = 0)
