# -*- coding: utf-8 -*-
"""
PDF renderer component.

Read PDF files and output a list of images.

"""


import os
import itertools

import pdf2image
import pytesseract

import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the PDF renderer component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the pdf renderer component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('image',),
                    list_field_to_clear = ('list', ))

    if not inputs['filepath']['ena']:
        return

    for filepath_pdf in inputs['filepath']['list']:
        for (idx_image, image) in enumerate(
                                    pdf2image.convert_from_path(filepath_pdf)):
            outputs['image']['list'].append({'filepath':  filepath_pdf,
                                             'idx_image': idx_image,
                                             'image':     image})

    if outputs['image']['list']:
        outputs['image']['ena'] = True
