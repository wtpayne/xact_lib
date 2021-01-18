# -*- coding: utf-8 -*-
"""
Xact component for rendering configuration as SVG.

"""


import copy

import graphviz

import xact.cfg


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the filesystem walk component.

    """
    state['font_color']    = cfg.get('font_color',    '#000000')
    state['font_name']     = cfg.get('font_name',     'tecnico.fino.ttf')
    state['font_size']     = cfg.get('font_size',     '8')

    state['graph_pad']     = cfg.get('graph_pad',     '0.5')
    state['graph_nodesep'] = cfg.get('graph_nodesep', '0.2')
    state['graph_ranksep'] = cfg.get('graph_ranksep', '0.3')

    state['node_color']    = cfg.get('node_color',    '#000000')
    state['node_width']    = cfg.get('node_width',    '1.5')
    state['node_height']   = cfg.get('node_height',   '0.5')

    state['edge_color']    = cfg.get('node_color',    '#000000')


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the filesystem walk component.

    """
    outputs['svg'].clear()
    outputs['svg']['ena'] = False

    if not inputs['cfg']['ena']:
        return

    outputs['svg']['ena'] = True
    outputs['svg']['map'] = dict()
    for (id_system, cfg) in inputs['cfg']['map'].items():
        outputs['svg']['map'][id_system] = _svg_dot_graph(cfg, state)


# -----------------------------------------------------------------------------
def _svg_dot_graph(cfg, state):
    """
    Return the svg dot graph of the specified cfg data.

    """
    cfg = xact.cfg.denormalize(copy.deepcopy(cfg))
    dot = graphviz.Digraph(
            'Process flow network',
            format     = 'svg',
            graph_attr = {
                'bgcolor':    'transparent',
                'pad':        state['graph_pad'],
                'splines':    'ortho',
                'rankdir':    'LR',
                'nodesep':    state['graph_nodesep'],
                'ranksep':    state['graph_ranksep'],
                'fontname':   state['font_name'],
                'fontsize':   state['font_size'],
                'fontcolor':  state['font_color']
            },
            node_attr  = {
                'shape':      'Mrecord',
                'style':      'rounded',
                'fixedsize':  'true',
                'width':      state['node_width'],
                'height':     state['node_height'],
                'color':      state['node_color'],
                'labelloc':   'b',
                'imagescale': 'true',
                'fontname':   state['font_name'],
                'fontsize':   state['font_size'],
                'fontcolor':  state['font_color']
            },
            edge_attr  = {
                'color': state['edge_color'],
            })

    for (id_host, cfg_host) in cfg['host'].items():

        with dot.subgraph(
                name       = 'cluster_' + id_host,
                graph_attr = { 'style': 'rounded',
                               'color': state['node_color'],
                               'label': id_host}) as host:

            for (id_proc, cfg_proc) in cfg['process'].items():

                if cfg_proc['host'] != id_host:
                    continue

                with host.subgraph(
                        name       = 'cluster_' + id_proc,
                        graph_attr = { 'style': 'rounded',
                                       'color': state['node_color'],
                                       'label': id_proc}) as process:

                    for (id_node, cfg_node) in cfg['node'].items():
                        if cfg_node['process'] != id_proc:
                            continue

                        process.node(id_node, label = id_node)

                    for cfg_edge in cfg['edge']:
                        is_intra_process    = cfg_edge['ipc_type'] == 'intra_process'
                        is_on_this_process  = cfg_edge['list_id_process'][0] == id_proc
                        if is_intra_process and is_on_this_process:
                            process.edge(cfg_edge['id_node_src'], cfg_edge['id_node_dst'])

            for cfg_edge in cfg['edge']:
                is_inter_process = cfg_edge['ipc_type'] == 'inter_process'
                is_on_this_host  = cfg_edge['list_id_host'][0] == id_host
                if is_inter_process and is_on_this_host:
                    host.edge(cfg_edge['id_node_src'], cfg_edge['id_node_dst'])

    for cfg_edge in cfg['edge']:
        is_inter_host = cfg_edge['ipc_type'] == 'inter_host'
        if is_inter_host:
            dot.edge(cfg_edge['id_node_src'], cfg_edge['id_node_dst'])

    str_all = dot.pipe().decode('utf-8')
    str_svg = str_all[str_all.find('<svg'):str_all.rfind('</svg>')+6]
    return str_svg
