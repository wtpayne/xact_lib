# -*- coding: utf-8 -*-
"""
Xact UI title block widget.

"""


import xact.lib.ui.web.markup.html
import xact.lib.web.util


# -----------------------------------------------------------------------------
def box(id_base, list_systems, list_diagrams, id_div_target):
    """
    Return resources for a titleblock UI component.

    """
    id_div_titleblock    = id_base + '_titleblock'
    id_div_systemid      = id_base + '_titleblock_systemid_div'
    id_div_author        = id_base + '_titleblock_author_div'
    id_div_date          = id_base + '_titleblock_date_div'
    cls_sys_menu         = id_base + '_titleblock_system_selection'
    cls_type_menu        = id_base + '_titleblock_diagram_type_selection'
    list_titleblock_subs = list()
    html                 = xact.lib.ui.web.markup.html
    div_titleblock       = html.div(id     = id_div_titleblock,
                                    _class = ('absolute',
                                              'bottom-2',
                                              'right-2',
                                              'grid',
                                              'grid-cols-2'))

    # System selection.
    div_titleblock.add(html.div(
        '<SYSTEM ID>',
        id          = id_div_systemid,
        data_script = 'on click toggle .hidden on .{cls}'.format(
                                                   cls = cls_sys_menu),
        _class      = ('col-span-2',
                       'p-0.5',
                       'border',
                       'border-gray-400',
                       'text-gray-300',
                       'bg-white')))

    for sys in list_systems:
        list_titleblock_subs.append(sys['id_diagram'])
        str_title         = sys['str_title']
        str_title_quoted  = '"{str_title}"'.format(str_title = str_title)
        str_author_quoted = '"Author TBD"'
        str_date_quoted   = '"Date TBD"'
        div_titleblock.add(html.div(
            str_title,
            data_script = (
                'on click toggle .hidden on .%s' % cls_sys_menu,
                'then remove .text-gray-300 from #%s' % id_div_systemid,
                'then add .text-gray-600 to #%s' % id_div_systemid,
                'then put', str_title_quoted,
                'into #%s.innerHTML' % id_div_systemid,
                'then put', str_author_quoted,
                'into #%s.innerHTML' % id_div_author,
                'then put', str_date_quoted,
                'into #%s.innerHTML' % id_div_date),
            _class = (
                cls_sys_menu,
                'hidden',
                'col-span-2',
                'p-0.5',
                'border-l',
                'border-r',
                'border-b',
                'border-gray-400',
                'text-gray-400',
                'bg-gray-200'),
            data_hx_trigger = 'click',
            data_hx_get     = '/%s' % sys['id_div_content'],
            data_hx_target  = '#%s' % id_div_target,
            data_hx_swap    = 'innerHTML'))

    # Diagram selection.
    div_titleblock.add(html.div(
        list_diagrams[0]['str_title'],
        data_script = (
            'on click toggle .hidden on .%s' % cls_type_menu,),
        _class = (
            'col-span-2',
            'p-0.5',
            'border-l',
            'border-r',
            'border-b',
            'border-gray-400',
            'text-gray-600',
            'bg-white')))

    for diag in list_diagrams:
        div_titleblock.add(html.div(
            diag['str_title'],
            data_script = (
                'on click toggle .hidden on .%s' % cls_type_menu,),
            _class = (
                cls_type_menu,
                'hidden',
                'col-span-2',
                'p-0.5',
                'border-l',
                'border-r',
                'border-b',
                'border-gray-400',
                'text-gray-400',
                'bg-gray-200'),
            data_hx_trigger = 'click',
            data_hx_get     = '/{id}'.format(id = diag['id_div_content']),
            data_hx_target  = '#{id}'.format(id = id_div_target),
            data_hx_swap    = 'innerHTML'))

    div_titleblock.add(html.div(
        '<AUTHOR>',
        id = id_div_author,
        _class = (
            'p-0.5',
            'border-l',
            'border-r',
            'border-b',
            'border-gray-400',
            'text-gray-300',
            'bg-white')))

    div_titleblock.add(html.div(
        '<DATE>',
        id = id_div_date,
        _class = (
            'p-0.5',
            'border-r',
            'border-b',
            'border-gray-400',
            'text-gray-300',
            'bg-white')))

    map_res_titleblock = xact.lib.web.util.ResMap()
    map_res_titleblock.htm(**{id_div_titleblock: div_titleblock})
    return (map_res_titleblock, id_div_titleblock, list_titleblock_subs)
