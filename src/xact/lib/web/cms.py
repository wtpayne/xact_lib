# -*- coding: utf-8 -*-
"""
Simple content management system component.

"""


import collections
import string
import textwrap

import dominate
import dominate.dom_tag
import dominate.svg as svg
import dominate.tags as tag
import dominate.util
import yaml

import xact.util
import xact.lib.web.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the CMS.

    """
    state['default'] = {
        'title':    'xplain.systems',
        'logo':     'DANUBE 𝑥',
        'sections': [
            ('As the world becomes more automated, we are losing control '
             'to systems whose complexity defies understanding and whose '
             'bias impacts us in unexpected and unwanted ways.'),
            ('We make tools to help govern complex systems using simple '
             'rules, taming unwanted complexity, and delivering the '
             'clarity and understanding that we need to protect our '
             'safety and our security.'),
            ('Leveraging cutting edge research from the University of '
             'Cambridge, we are working with our industrial partners to '
             'pioneer new approaches to explainable AI and systems '
             'engineering.'),
            ('If you want to learn more about our unique approach to '
             'explainable AI, please contact {contact_link}')],
        'contact_email': 'enquiries@xplain.systems',
        'contact_link':  '<a href="mailto:{contact_email}">{contact_email}</a>'}

    state['style'] = {
        ':root':       {'--rgb-fg-0':       '#FFFFFF',
                        '--rgb-fg-1':       '#CCC7E2',
                        '--rgb-bg-0':       '#0C0238',
                        '--rgb-bg-1':       '#07031A' },
        '::selection': {'background':       'var(--rgb-fg-1)'},
        'html, body':  {'width':            '100%',
                        'height':           '100%',
                        'display':          'grid',
                        'border':           0,
                        'margin':           0,
                        'padding':          0,
                        'color':            'var(--rgb-fg-0)',
                        'background-color': 'var(--rgb-bg-0)',
                        'font-family':      '"Roboto", sans-serif',
                        'font-size':        '100%',
                        'font-weight':      '100'},
        '.content':    {'margin':           'auto',
                        'width':            '36em'},
        '.logo':       {'text-align':       'center',
                        'font-size':        '700%'},
        '.name':       {'text-align':       'center',
                        'font-size':        '500%',
                        'margin':           '0.2em'},
        'p':           {'text-align':       'justify',
                        'margin':           '1.5em'},
        'a':           {'color':            'var(--rgb-fg-1)',
                        'font-weight':      '300',
                        'text-decoration':  'none'}}



# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the CMS.

    """
    outputs['resources']['ena'] = False
    if not inputs['time']['ena']:
        return

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(default = _info_page(state['default']))
    map_res.css(style   = state['style'])

    outputs['resources']['ena'] = True
    outputs['resources'].update(dict(map_res))


# -----------------------------------------------------------------------------
def _info_page(content):
    """
    Return informational page HTML

    """
    content = xact.util.format_all_strings(map_data = content)
    doc     = dominate.document(title = content['title'])
    with doc.head:
        tag.meta(charset = 'utf-8')
        tag.link(rel     = 'stylesheet',
                 href    = 'https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;900&display=swap')
        tag.link(rel     = 'stylesheet',
                 type    = 'text/css',
                 href    = xact.lib.web.util.url('style'))
    with doc:
        with tag.div(cls = 'content'):
            tag.header(content['logo'],  cls = 'logo')
            tag.header(content['title'], cls = 'name')
            for section in content['sections']:
                with tag.p():
                    dominate.util.raw(section)
    return doc