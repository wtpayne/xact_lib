# -*- coding: utf-8 -*-
"""
Tesseract OCR component.

"""


import collections
import itertools
import os
import sys
import copy

import pdf2image
import pytesseract

import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the Tesseract OCR component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the Tesseract OCR component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('chunk',),
                    list_field_to_clear = ('list', ))

    if not inputs['image']['ena']:
        return

    for map_image in inputs['image']['list']:
        outputs['chunk']['list'].extend(
            _process_image(filepath  = map_image['filepath'],
                           idx_image = map_image['idx_image'],
                           image     = map_image['image']))

    if outputs['chunk']['list']:
        outputs['chunk']['ena'] = True


# -----------------------------------------------------------------------------
def _process_image(filepath, idx_image, image):
    """
    Process a single image.

    """
    map_ocr = pytesseract.image_to_data(image,
                                        config      = '-psm 1',
                                        output_type = pytesseract.Output.DICT)

    # -------------------------------------------------------------------------
    def makechunk():
        return {
            'filepath':  filepath,
            'idx_image': idx_image,
            'words':     list(),
            'text':      None,
            'min_x':     sys.maxsize,
            'max_x':     -(sys.maxsize-1),
            'min_y':     sys.maxsize,
            'max_y':     -(sys.maxsize-1)
        }

    map_chunk = collections.defaultdict(makechunk)

    # level page_num block_num par_num
    # line_num word_num
    # left top width height
    # conf
    # text
    for (idx, str_text) in enumerate(map_ocr['text']):
        uid = (filepath,
               idx_image,
               map_ocr['level'][idx],
               map_ocr['page_num'][idx],
               map_ocr['block_num'][idx],
               map_ocr['par_num'][idx])

        map_chunk[uid]['uid'] = uid

        left   = map_ocr['left'][idx]
        top    = map_ocr['top'][idx]
        width  = map_ocr['width'][idx]
        height = map_ocr['height'][idx]
        right  = left + width
        bottom = top + height

        if map_chunk[uid]['min_x'] < left:
            map_chunk[uid]['min_x'] = left

        if map_chunk[uid]['max_x'] < right:
            map_chunk[uid]['max_x'] = right

        if map_chunk[uid]['min_y'] < top:
            map_chunk[uid]['min_y'] = top

        if map_chunk[uid]['max_y'] < bottom:
            map_chunk[uid]['max_y'] = bottom

        map_chunk[uid]['words'].append(str_text)

    list_chunk = list()
    for uid in sorted(map_chunk.keys()):
        map_chunk[uid]['text'] = ' '.join(map_chunk[uid]['words'])
        list_chunk.append(map_chunk[uid])

    return list_chunk