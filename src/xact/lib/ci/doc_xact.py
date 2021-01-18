# -*- coding: utf-8 -*-
"""
Documentation generator for xact design documents.

"""


import xact.cfg
import xact.cfg.load


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the continuous integration distributor component.

    """
    pass


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the continuous integration distributor component.

    """
    if not inputs['content']['ena']:
        return

    for map_content in inputs['content']['list']:
        filepath = map_content['filepath']
        cfg = xact.cfg.load.from_yaml_string(map_content['content'])
        cfg = xact.cfg.denormalize(cfg)
        xml = _svg_dot_graph(cfg)
        # print(xml)


# -----------------------------------------------------------------------------
def _svg_dot_graph(cfg):
    """
    Return the svg dot graph of the specified cfg data.

    """
    fg_color = '#959bbd'
    fontname = 'tecnico.fino.ttf'
    fontsize = '10'
    import graphviz
    dot = graphviz.Digraph(
            'Process flow network',
            format     = 'svg',
            graph_attr = {
                'bgcolor':    'transparent',
                'pad':        '1.0',
                'splines':    'ortho',
                'rankdir':    'LR',
                'nodesep':    '1.20',
                'ranksep':    '0.90',
                'fontname':   fontname,
                'fontsize':   fontsize,
                'fontcolor':  fg_color
            },
            node_attr  = {
                'shape':      'Mrecord',
                'style':      'rounded',
                'fixedsize':  'true',
                'width':      '1.9',
                'height':     '0.7',
                'color':      fg_color,
                'labelloc':   'b',
                'imagescale': 'true',
                'fontname':   fontname,
                'fontsize':   fontsize,
                'fontcolor':  fg_color
            },
            edge_attr  = {
                'color': fg_color,
            })

    for (id_host, cfg_host) in cfg['host'].items():

        with dot.subgraph(
                name       = 'cluster_' + id_host,
                graph_attr = { 'style': 'rounded',
                               'color': fg_color,
                               'label': id_host}) as host:

            for (id_proc, cfg_proc) in cfg['process'].items():

                if cfg_proc['host'] != id_host:
                    continue

                with host.subgraph(
                        name       = 'cluster_' + id_proc,
                        graph_attr = { 'style': 'rounded',
                                       'color': fg_color,
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

    str_svg = dot.pipe().decode('utf-8')
    content = str_svg[str_svg.find('<svg'):str_svg.rfind('</svg>')+6]
    return content
