# -*- coding: utf-8 -*-
"""
Image resize node.

"""


import cv2
import numpy
import torch


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the video capture node.

    """
    outputs['img'].clear()
    outputs['img']['ena'] = True

    state['output_height'] = cfg['output_height']
    state['output_width']  = cfg['output_width']
    state['out_keys']      = sorted([key for key in outputs.keys()
                                                    if key.startswith('img')])
    for key in state['out_keys']:
        outputs[key]['ena'] = False


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Capture the next frame.

    """
    if not inputs['img']['ena']:
        for key in state['out_keys']:
            outputs[key]['ena'] = False
        return

    # input_scale = base_height / frame.shape[0]
    # scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
    # scaled_img = scaled_img[:, 0:scaled_img.shape[1] - (scaled_img.shape[1] % stride)]  # better to pad, but cut out for demo
    # if fx < 0:  # Focal length is unknown
    #     fx = np.float32(0.8 * frame.shape[1])

    output_size = (state['output_height'], state['output_width'])
    img         = cv2.resize(inputs['img']['buff'], dsize = output_size)
    img         = img.astype(numpy.float16)
    img         = _rescale(img)
    img         = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)

    # img = _nhwc_to_nchw_transpose(_img_norm(img))
    # img = torch.from_numpy(img).float()

    for key in state['out_keys']:
        outputs[key]['ena']  = True
        outputs[key]['ts']   = inputs['img']['ts']
        outputs[key]['buff'] = img


# -----------------------------------------------------------------------------
def _rescale(img):
    """
    Rescale the image values to the range [-0.5, 0.5]

    """
    midrange = numpy.array([128, 128, 128], dtype = numpy.float32)
    scale    = numpy.float32(1/255)
    return (img.astype(numpy.float32) - midrange) * scale


# -----------------------------------------------------------------------------
def _img_norm(img):
    """
    Normalize the image range.

    """
    value_scale = 255
    mean        = [0.406, 0.456, 0.485]
    stdev       = [0.225, 0.224, 0.229]
    mean        = [item * value_scale for item in mean]
    stdev       = [item * value_scale for item in stdev]
    img         = (img - mean) / stdev
    return img


# -----------------------------------------------------------------------------
def _nhwc_to_nchw_transpose(img):
    """
    Transpose the image from NHWC to NCHW

    """
    img = img.transpose(2, 0, 1)
    img = numpy.expand_dims(img, 0)
    return img