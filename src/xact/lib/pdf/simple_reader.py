# -*- coding: utf-8 -*-
"""
PDF reader component.

Read PDF files and output text.

"""


import os
import itertools

import pdftotext

import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the PDF reader component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the pdf reader component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('chunk',),
                    list_field_to_clear = ('list', ))

    if not inputs['filepath']['ena']:
        return

    for filepath_pdf in inputs['filepath']['list']:
        outputs['chunk']['list'].extend(_iter_chunk(filepath_pdf))

    if outputs['chunk']['list']:
        outputs['chunk']['ena'] = True


# -----------------------------------------------------------------------------
def _iter_chunk(filepath_pdf, len_chunk_max = 1000, len_window = 300):
    """
    Yield each text chunk in the specified pdf

    """
    for tup_page in _iter_page(filepath_pdf):

        (filepath_pdf, idx_page, str_page, str_error) = tup_page
        len_page = len(str_page)

        if len_page <= len_chunk_max:
            yield (filepath_pdf, idx_page, 0, str_page, str_error)
        else:
            iter_idx_min = range(0, len_page, len_chunk_max)
            for (idx_chunk, idx_min) in enumerate(iter_idx_min):
                # TODO: Search for a natural break, e.g. space or newline.
                idx_end   = len_page - 1
                idx_max   = min(idx_end, (idx_min + len_chunk_max))
                str_chunk = str_page[idx_min:idx_max]
                yield (filepath_pdf, idx_page, idx_chunk, str_chunk, str_error)


# -----------------------------------------------------------------------------
def _iter_page(filepath_pdf, max_errors = 10):
    """
    Yield all the pages from the specified pdf, skipping those with errors.

    If more than max_errors are encountered,
    then the rest of the PDF will be skipped.

    """
    assert os.path.exists(filepath_pdf)
    with open(filepath_pdf, 'rb') as file_pdf:

        try:
            iter_str_page = iter(pdftotext.PDF(file_pdf))
        except pdftotext.Error:
            yield (filepath_pdf, 0, '', str(pdftotext.Error))
            return

        num_errors = 0

        for idx_page in itertools.count():

            str_page = ''
            error    = ''

            try:
                str_page = next(iter_str_page)
            except pdftotext.Error:
                error       = str(pdftotext.Error)
                num_errors += 1
            except StopIteration:
                return

            yield (filepath_pdf, idx_page, str_page, error)

            if num_errors >= max_errors:
                return