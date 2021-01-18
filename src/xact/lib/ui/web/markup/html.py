# -*- coding: utf-8 -*-
"""
HTML markup tag classes.

"""


import textwrap

import xact.lib.ui.web.markup


globals().update(xact.lib.ui.web.markup.html_tags())


# -----------------------------------------------------------------------------
def tag(_params = dict(), _type = 'div', _class = tuple()):
    """
    Return a tag of the specified type.

    """
    # Add content as a string or as a tuple
    if '_content' not in _params:
        iter_content = tuple()
    elif isinstance(_params['_content'], tuple):
        iter_content = _params['_content']
    else:
        iter_content = (_params['_content'],)

    # Extend class definitions
    if '_class' not in _params:
        _params['_class'] = ()
    if isinstance(_class, tuple):
        _params['_class'] += _class
    else:
        _params['_class'] += (_class,)

    tag_type = _params.pop('_type', _type)

    return globals()[tag_type](*iter_content, **_params)


# -----------------------------------------------------------------------------
def inline_script(text, **kwargs):
    """
    Return a script tag without escaping the content.

    """
    return script(raw(textwrap.dedent(text)), **kwargs)

