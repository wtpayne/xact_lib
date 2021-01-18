# -*- coding: utf-8 -*-
"""
Web UI utility library.

"""


import dominate

import xact.lib.ui.web.markup.html



# -----------------------------------------------------------------------------
def page(title, id_topic, list_id_ui):
    """
    Return a default HTML page.

    """
    html = xact.lib.ui.web.markup.html
    page = html.document(title = title)
    with page.head:

        html.meta(charset = 'utf-8')

        html.meta(name    = 'viewport',
                  content = 'width=device-width, initial-scale=1.0')

        html.link(rel     = 'stylesheet',
                  href    = ('https://fonts.googleapis.com/css2'
                             '?family=Roboto:wght@100;300;900&display=swap'))

        # TAILWIND
        html.link(rel     = 'stylesheet',
                  href    = ('https://unpkg.com/tailwindcss'
                             '@^2/dist/tailwind.min.css'))

        # VEGA LITE
        html.script(type = 'text/javascript',
                    src  = 'https://cdn.jsdelivr.net/npm/vega@5')
        html.script(type = 'text/javascript',
                    src  = 'https://cdn.jsdelivr.net/npm/vega-lite@4')
        html.script(type = 'text/javascript',
                    src  = 'https://cdn.jsdelivr.net/npm/vega-embed@6')

        # html.script(type  = 'text/javascript',
        #             src   = "https://d3js.org/d3.v6.min.js")

        # html.script(type  = 'text/javascript',
        #             src   = 'https://unpkg.com/htmx.org@1.0.1')
        html.script(type  = 'text/javascript',
                    src   = '/htmx')
        # html.script(type  = 'text/javascript',
        #             src   = 'https://unpkg.com/hyperscript.org@0.0.2')

        html.script(type  = 'text/javascript',
                    src   = '/xact_htmx_extension')

        # html.link(rel     = 'stylesheet',
        #           type    = 'text/css',
        #           href    = '/style')

    with page:
        connect = 'connect:/{id_topic}'.format(id_topic = id_topic)
        with html.div(data_hx_sse = connect,
                      _class      = ('bg-gray-100', 'h-screen')) as parent:
            for id_ui in list_id_ui:
                html.div(data_hx_ext     = 'xact',
                         data_hx_sse     = 'swap:{id}'.format(id = id_ui),
                         data_hx_trigger = 'load',
                         data_hx_get     = '/{id}'.format(id = id_ui))
    return page


# -----------------------------------------------------------------------------
def xact_htmx_extension():
    """
    Return javascript for the xact htmx extension.

    """
    return """
          htmx.defineExtension('xact', {
            onEvent : function(name_evt_src, evt_src) {

                // New logic is either swapped in or sent via SSE.
                is_swap   = (name_evt_src === 'htmx:afterSwap');
                is_sse    = name_evt_src.startsWith('htmx:sse:');
                is_update = (is_swap || is_sse);
                if (!is_update) {
                    return;
                }

                // Event handling logic is stored in the window.xact global.
                if (!('xact' in window)) {
                    window.xact = {};
                }

                // Ignore events where handling logic already exists.
                if (name_evt_src in window.xact) {
                    return;
                }

                // Update the callbacks where we have new ones provided.
                elt_target = evt_src.target;
                list_found = htmx.findAll(elt_target, '[xact], [data-xact]');
                for (var idx = 0; idx < list_found.length; idx++) {

                    elt_found    = list_found[idx];
                    name_evt_tgt = 'htmx:sse:' + elt_found.id;

                    if (!(name_evt_tgt in window.xact)) {
                        window.xact[name_evt_tgt] = {};
                    }

                    node_new = eval(elt_found.dataset.xact);
                    node_old = window.xact[name_evt_tgt];

                    if ('step' in node_old) {
                        elt_target.removeEventListener(name_evt_tgt,
                                                       node_old.step);
                    }
                    if ('step' in node_new) {
                        elt_target.addEventListener(name_evt_tgt,
                                                    node_new.step);
                    }

                    window.xact[name_evt_tgt] = node_new;
                    window.xact[name_evt_tgt].reset(name_evt_tgt);

                }
            }
          })"""


# -----------------------------------------------------------------------------
def sse_swapping_streamer(list_id_ui, **kwargs):
    """
    Return a list of divs that display a 'live view' of the given resources.

    Requires the containing branch
    in the DOM to be subscribed to
    SSE (Server Side Event) updates
    for the specified resource.

    """
    list_tag = []
    for id_ui in list_id_ui:
        tag_div = xact.lib.ui.web.markup.html.div(
                            data_hx_ext     = 'xact',
                            data_hx_sse     = 'swap:{id}'.format(id = id_ui),
                            data_hx_trigger = 'load',
                            data_hx_get     = '/{id}'.format(id = id_ui),
                            **kwargs)
        list_tag.append(tag_div)
    return list_tag


# -----------------------------------------------------------------------------
def dashboard(list_id_ui, **kwargs):
    """
    Return a responsive dashboard div.

    The dashboard contains a number
    of resources, each of which is
    treated as a 'live view', updated
    whenever the corresponding SSE
    event is received.

    """
    tag_dashboard = xact.lib.ui.web.markup.html.div(
                                _class = ('grid',
                                          'grid-cols-1',
                                          'sm:grid-cols-2',
                                          'md:grid-cols-3',
                                          'w-30',
                                          'h-30',
                                          'gap-5',
                                          'p-12'),
                                **kwargs)
    for tag in sse_swapping_streamer(list_id_ui):
        tag_dashboard.add(tag)
    return tag_dashboard


# -----------------------------------------------------------------------------
def foldable(data):
    """
    A foldable widget for displaying hierarchical data.

    """
    root_element   = tag.ul(id = 'foldable')
    map_tag_parent = {_id(tuple()): root_element}
    depth_first    = xact.util.gen_path_value_pairs_depth_first(dict(data))

    for (path, value) in depth_first:

        path_parent = path[:-1]
        id_parent   = _id(path_parent)
        tag_parent  = map_tag_parent[id_parent]

        is_leaf = not xact.util.is_container(value)
        if is_leaf:
            li_class = 'foldable tree-leaf'
        else:
            li_class = 'foldable tree-branch'

        # The <li> tag holds the content for each leaf/branch.
        id_li  = _id(path)
        tag_li = tag.li(cls = li_class)
        tag_li.add(tag.input_(id = id_li, type = 'checkbox'))
        tag_parent.add(tag_li)

        # Indent the label as appropriate.
        name_li       = str(path[-1]).strip()
        depth_in_tree = len(path)
        indent_size   = depth_in_tree - 1
        inline_style  = 'padding-inline-start: {n}em'.format(n = indent_size)
        tag_li.add(tag.label(name_li, fr = id_li, style = inline_style))

        # Leaves and branches are handled differently.
        if is_leaf:
            tag_li.add(
                tag.div(
                    dominate.util.raw(value),
                    cls = 'tree-leaf-content'))
        else:
            tag_child_list = tag.ul()
            tag_li.add(tag_child_list)
            map_tag_parent[id_li] = tag_child_list

    css = {
        '#foldable':       {'margin':                0,
                            'padding':               0,
                            'max-width':             '100%',
                            'font-size':             '0.85rem'},
        '#foldable, li':   {'list-style':            'none',
                            'padding':               '0em',
                            'border':                0},
                            #'border-bottom':         '1px solid var(--rgb-fg-0)'},
        '#foldable li:last-child': {
                            'border':                0},
        '#foldable label': {'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'cursor':                'pointer'},
        '#foldable div':   {'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'cursor':                'text'},
        '#foldable input[type=text]': {
                            'padding':               '0.5em',
                            'position':              'relative',
                            'display':               'block',
                            'width':                 '100%',
                            'border':                'none',
                            'outline':               'none',
                            'cursor':                'text',
                            'background-color':      'var(--rgb-bg-0)', # 'transparent',
                            'color':                 'var(--rgb-fg-0)'},
        '#foldable input[type=checkbox]': {
                            'display':               'none'},             # Hide checkbox }
        'li.foldable ul':  {'visibility':            'hidden',            # Fold (hide) by default
                            'opacity':               0,
                            'max-height':            0,                   # CSS bug. Height animation
                            'transition':            'all 0.25s',
                            'padding-inline-start':  0},                  # Depth-dependent indent }
        'li.foldable input:checked ~ ul': {
                            'visibility':            'visible',           # Unfold (shiw) when checked
                            'opacity':               1,
                            'max-height':            '999px',             # Enough height for animation
                            'padding-inline-start':  0},                  # Depth-dependent indent }
        '.foldable':       {'border-bottom':         0}, # '1px solid white'},
        '.tree-leaf':      {'display':               'grid',
                            'grid-template-rows':    '1fr',
                            'grid-template-columns': '14em 30em'},
        '.tree-leaf-content': {
                            'text-align':            'justify'},
    }
    return (root_element, css)


# -----------------------------------------------------------------------------
def _id(data):
    """
    Return a content-based ID for the specified data structure.

    """
    sha = hashlib.sha256()
    sha.update(json.dumps(data).encode('utf-8'))
    return 'ID' + sha.hexdigest()[0:8]


