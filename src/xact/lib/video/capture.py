# -*- coding: utf-8 -*-
"""
Video capture node.

"""


import cv2


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the video capture node.

    """
    try:
        connection = int(cfg['connection'])
    except ValueError:
        connection = cfg['connection']

    if connection == 'nvarguscamerasrc':
        state['cap'] = cv2.VideoCapture(
                                gstreamer_pipeline(
                                        capture_width  = cfg['capture_width'],
                                        capture_height = cfg['capture_height'],
                                        display_width  = cfg['display_width'],
                                        display_height = cfg['display_height'],
                                        framerate      = cfg['framerate'],
                                        flip_method    = cfg['flip_method']),
                                cv2.CAP_GSTREAMER)
    else:
        state['cap'] = cv2.VideoCapture(connection)


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Capture the next frame.

    """
    if not inputs['time']['ena']:
        return

    (is_ok, outputs['img']['buff']) = state['cap'].read()   # OpenCV |- BGR
    outputs['img']['ena'] = is_ok
    outputs['img']['ts']  = inputs['time']['ts']

    print('CAP: ' + str(is_ok))


# -----------------------------------------------------------------------------
def gstreamer_pipeline(capture_width  = 1280,
                       capture_height = 720,
                       display_width  = 1280,
                       display_height = 720,
                       framerate      = 60,
                       flip_method    = 0):

    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (capture_width,
           capture_height,
           framerate,
           flip_method,
           display_width,
           display_height))