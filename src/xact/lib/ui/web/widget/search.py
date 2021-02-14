# -*- coding: utf-8 -*-
"""
Xact UI search bar widget.

"""


import functools

import xact.lib.ui.web.markup.html
import xact.lib.web.util

import dill
import fuzzywuzzy.process


# -----------------------------------------------------------------------------
def box(id_base, map_index):
    """
    Return resources for a search bar widget UI component.

    """
    map_res = xact.lib.web.util.ResMap()

    id_form      = id_base + '_search_form'
    id_input     = id_base + '_search_input'
    id_function  = id_base + '_search_function'
    cls_search   = id_base + '_search_component'
    curried_func = functools.partial(
                                search_function,
                                map_index   = map_index,
                                id_form     = id_form,
                                id_input    = id_input,
                                id_function = id_function,
                                cls_search  = cls_search)
    pickle_curry = dill.dumps(curried_func)
    map_res.async(**{id_function: pickle_curry})

    # pin flex items-center justify-center
    form_searchbox = xact.lib.ui.web.markup.html.form(
        id          = id_form,
        data_script = (
            'on keyup from document',
            'if event.altKey and event.key == "p"',
            'then toggle .hidden on .%s' % cls_search,
            'then call #%s.focus()' % id_input),
        _class = (
            '%s' % cls_search,
            'hidden',
            'absolute',
            'top-1/4',
            'left-1/4',
            'w-1/2',
            'border',
            'border-gray-400',
            'text-gray-400',
            'bg-gray-200',
            'p-0.5'))
    form_searchbox.add(
        search_results(
            id_form          = id_form,
            id_input         = id_input,
            id_function      = id_function,
            cls_search       = cls_search,
            str_command      = '',
            list_suggestions = [],
            idx_selection    = 0,
            is_hidden        = True))
    map_res.htm(**{id_form:  form_searchbox})

    list_subs = list()
    return (map_res, id_form, list_subs)


# -----------------------------------------------------------------------------
async def search_function(request,
                          map_index,
                          id_form,
                          id_input,
                          id_function,
                          cls_search):
    """
    Server side logic for the search.

    """
    formdata     = await request.form()
    str_query    = formdata['input']
    list_choices = list(map_index.keys())
    list_match   = []
    for (str_match, score) in fuzzywuzzy.process.extract(
                                                query   = str_query,
                                                choices = list_choices,
                                                limit   = 4):
        if score > 80:
            list_match.append(map_index[str_match])

    return ('text/html', search_results(id_form          = id_form,
                                        id_input         = id_input,
                                        id_function      = id_function,
                                        cls_search       = cls_search,
                                        str_command      = str_query,
                                        list_suggestions = list_match,
                                        idx_selection    = 0,
                                        is_hidden        = False).render())


# -----------------------------------------------------------------------------
def search_results(id_form,
                   id_input,
                   id_function,
                   cls_search,
                   str_command,
                   list_suggestions,
                   idx_selection,
                   is_hidden):
    """
    Reuturn a div for search results.

    """
    list_class = ['%s' % cls_search,
                  'w-full']
    if is_hidden:
      list_class.append('hidden')

    html    = xact.lib.ui.web.markup.html
    content = html.div()
    content.add(html._input(
        value           = str_command,
        autocomplete    = 'off',
        id              = id_input,
        name            = 'input',
        type            = 'text',
        data_hx_trigger = 'keyup changed delay:100ms',
        data_hx_post    = '/%s' % id_function,
        data_hx_target  = '#%s' % id_form,
        _class          = list_class))

    for (idx, str_suggestion) in enumerate(list_suggestions):
        if idx == idx_selection:
            content.add(html.div(str_suggestion,
                                 _class = list_class + ['bg-red-100']))
        else:
            content.add(html.div(str_suggestion,
                                 _class = list_class))
    return content
