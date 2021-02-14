# -*- coding: utf-8 -*-
"""
Xact component for reading VCS metadata.

"""

import xact.cfg

# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset

    """
    pass

# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step

    """
    outputs['metadata'].clear()
    outputs['metadata']['ena'] = False

    if inputs['filepath']['ena']:

        outputs['metadata']['ena']  = True
        outputs['metadata']['map']  = dict()

        # for filepath in inputs['filepath']['list']:
        #     cfg       = xact.cfg.prepare(filepath)
        #     id_system = cfg['system']['id_system']
        #     outputs['cfg']['map'][id_system] = cfg