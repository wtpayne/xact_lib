# -*- coding: utf-8 -*-
"""
Continuous integration python pycodestyle checker for xact.

"""


import pycodestyle


_NAME_TOOL = 'xact.lib.ci.pycodestyle'


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration python pycodestyle checker component.

    """
    state['list_ignore'] = cfg['list_ignore']


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration python pycodestyle checker component.

    """
    list_name_output = ('conformity', 'nonconformity')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    list_nonconformity_reports = list()

    # =========================================================================
    class ReportAdapter(pycodestyle.StandardReport):
        """
        Reporting Adapter class for pycodestyle (pep8) checks.

        """

        def get_file_results(self):
            """
            Redirect error messages to the build_monitor coroutine.

            """
            for (line, col, msg_id, msg, doc) in self._deferred_print:
                doc = '    ' + doc.strip()  # Fixup indentation
                list_nonconformity_reports.append(dict(
                                                tool     = _NAME_TOOL,
                                                msg_id   = msg_id,
                                                msg      = msg + '\n\n' + doc,
                                                filepath = filepath,
                                                line     = line,
                                                col      = col))

    style = pycodestyle.StyleGuide(quiet  = False,
                                   ignore = state['list_ignore'])

    style.init_report(reporter = ReportAdapter)  # Inject custom reporting.

    for content in inputs['content']['list']:
        filepath = content['filepath']
        list_nonconformity_reports.clear()
        style.check_files((filepath,))
        if list_nonconformity_reports:
            outputs['nonconformity']['list'].extend(
                                                list_nonconformity_reports)
        else:
            outputs['conformity']['list'].append(dict(tool     = _NAME_TOOL,
                                                      filepath = filepath))

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True
