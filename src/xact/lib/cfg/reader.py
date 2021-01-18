# -*- coding: utf-8 -*-
"""
Xact component for reading configuration.

"""

import xact.cfg

# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the filesystem walk component.

    """
    pass

# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the filesystem walk component.

    """
    outputs['cfg'].clear()
    outputs['cfg']['ena'] = False

    if inputs['filepath']['ena']:

        outputs['cfg']['ena']  = True
        outputs['cfg']['map']  = dict()

        for filepath in inputs['filepath']['list']:
            cfg       = xact.cfg.prepare(filepath)
            id_system = cfg['system']['id_system']
            outputs['cfg']['map'][id_system] = cfg