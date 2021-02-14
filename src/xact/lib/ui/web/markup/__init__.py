# -*- coding: utf-8 -*-
"""
Markup generator library.

"""


import dominate
import dominate.dom_tag
import dominate.tags
import dominate.svg
import dominate.util


# -----------------------------------------------------------------------------
def html_tags():
    """
    Return a dict of html tag classes.

    """
    map_tags = dict(_iter_dom_tag(module     = dominate.tags,
                                  tup_ignore = ('dom_tag', 'html_tag')))
    map_tags['document'] = dominate.document
    map_tags['raw']      = dominate.util.raw
    return map_tags


# -----------------------------------------------------------------------------
def svg_tags():
    """
    Return a dict of svg tag classes.

    """
    return dict(_iter_dom_tag(module     = dominate.svg,
                              tup_ignore = ('dom_tag', 'html_tag', 'svg_tag')))


# -----------------------------------------------------------------------------
def _iter_dom_tag(module, tup_ignore):
    """
    Yield name_class, type_class for each dom_tag in the specified module.

    """
    for (key, value) in module.__dict__.items():
        if (     isinstance(value, type)
             and issubclass(value, dominate.dom_tag.dom_tag)
             and (key not in tup_ignore)):
            yield (key, value)


# -----------------------------------------------------------------------------
def _monkeypatch_dominate(dom_tag):
    """
    Monkeypatch the dom_tag class with a new clean_pair function.

    """
    # Prevent monkey patching twice.
    if hasattr(dom_tag, '_clean_pair_orig'):
        return

    # Keep a reference to the old clean_pair function.
    setattr(dom_tag, '_clean_pair_orig', dom_tag.clean_pair)

    # -------------------------------------------------------------------------
    def _clean_pair_patch(cls, attribute, value):
        """
        Return a clean attribute value pair.

        This is used to patch the dom_tag clean_pair
        function to add syntactic sugar for helping
        with class-based frameworks like tailwind.

        """
        (attribute, value) = cls._clean_pair_orig(attribute, value)
        if attribute in ('class', 'data-script'):
            if isinstance(value, tuple) or isinstance(value, list):
                value = ' '.join(value)
        return (attribute, value)

    # Patch in the new function.
    dom_tag.clean_pair = classmethod(_clean_pair_patch)


_monkeypatch_dominate(dom_tag = dominate.dom_tag.dom_tag)