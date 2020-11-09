# -*- coding: utf-8 -*-
"""
Python design documentation generator.

"""


import html
import os
import xml.etree.ElementTree
import xml.dom.minidom

import baron
import baron.utils
import dominate
import dominate.tags as tag

import xact.lib.web.util


TEMP_DELETEME = set()


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the design documentation generator component.

    """
    state['index'] = dict()


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the design documentation generator component.

    """
    if not inputs['content']['ena']:
        return

    map_res = xact.lib.web.util.ResMap()
    map_res.htm(default = 'DEFAULT')

    for map_content in inputs['content']['list']:
        filepath = map_content['filepath']
        key      = filepath.replace(os.sep, '.')
        html     = _render_document(map_content)
        if html is not None:
            map_res.htm(**{key: html})
            state['index'][filepath] = key
        else:
            # Nonconformity?
            pass

    html = _render_index(index = state['index'])
    map_res.htm(index = html)

    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def _render_index(index):
    """
    """
    css = dict()
    doc = dominate.document(title = 'Index')
    with doc.head:
        tag.meta(charset = 'utf-8')
        tag.link(rel     = 'stylesheet',
                 href    = 'https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;900&display=swap')
        tag.link(rel     = 'stylesheet',
                 type    = 'text/css',
                 href    = xact.lib.web.util.url('style'))
    with doc:
        with tag.div(cls = 'content') as tag_content:
            for (filepath, key) in index.items():
                tag_content.add(tag.a(filepath, href='/req/' + key))

    return doc


# -----------------------------------------------------------------------------
def _render_document(map_content):
    """
    """
    content = map_content['content']
    try:
        ast = baron.parse(content)
    except baron.utils.BaronError as err:
        return None

    xml_tree  = Walker().walk(ast)
    # xml.etree.ElementTree.indent(xml_tree,
    #                              space = " ",
    #                              level = 0)
    xml_text  = xml.etree.ElementTree.tostring(
                    xml_tree.xml_root,
                    encoding     = 'utf-8').decode('utf-8')

    dom = xml.dom.minidom.parseString(xml_text)
    xml_text = dom.toprettyxml()

    return xml_text


# =============================================================================
class Walker(baron.render.RenderWalker):
    """
    Walk the AST building a HTML representation.

    """

    BLOCK_NODES = ('def', 'class')
    FLOW_NODES  = ('assignment',
                   'associative_parenthesis',
                   'atomtrailers',
                   'binary_operator',
                   'call',
                   'call_argument',
                   'comma',
                   'comment',
                   'comparison',
                   'comparison_operator',
                   'continue',
                   'decorator',
                   'def_argument',
                   'dict',
                   'dict_argument',
                   'dictitem',
                   'dot',
                   'dotted_as_name',
                   'dotted_name',
                   'elif',
                   'else',
                   'endl',
                   'for'
                   'getitem',
                   'if',
                   'ifelseblock',
                   'import',
                   'int',
                   'list',
                   'name',
                   'print',
                   'return',
                   'space',
                   'string',
                   'tuple',
                   'unitary_operator',
                   'while',
                   'with',
                   'with_context_item',
                   'yield_atom')

    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Walker ctor.

        ---
        type:   constructor
        ...

        """
        super(Walker, self).__init__(strict=True)

        self.xml_root     = None
        self.xml_element  = None
        self.xml_path     = None
        self.fst_path     = None
        self.prev_element = None
        self.iline        = None

    # -------------------------------------------------------------------------
    def walk(self, tree):
        """
        Walk over the python FST tree building an XML tree.

        ---
        type: method
        ...

        """
        # Root of the XML tree
        #
        self.xml_root = xml.etree.ElementTree.Element('div')

        # Pointer to the current element in the tree.
        #
        self.xml_element = self.xml_root

        # Path from the root of the xml tree to the current element.
        #
        self.xml_path = [self.xml_root]

        # Path from the root of the FST tree to the current element.
        #
        self.fst_path = [(None, None, tree)]

        # Previous sibling in the current node or None.
        #
        self.prev_element = None

        # Current line order.
        # This relies on walk performing a depth-first
        # traversal so that line numbers increment
        # monotonically.
        #
        self.iline = 0

        super(Walker, self).walk(tree)
        return self

    # -------------------------------------------------------------------------
    def before(self, key_type, item, render_key):
        """
        Render starting tag and content before each FST node is visited.

        ---
        type: method

        args:
            self:
                An object of type Walker.
            key_type:
                "key_type is a string argument that
                indicates the type of the node and
                thus the data type of the item
                argument. It can take one of five
                values:- 'constant', 'node', 'key',
                'list', or 'formatting'. A 'constant'
                key_type indicates that item is a
                string. A 'node' key_type indicates
                that item is a dict. A 'key'
                key_type indicates that item is an
                element of a dict. A 'list' key_type
                indicates that item is a list, and
                a 'formatting' key_type indicates
                that the item is a list specialised
                in formatting."
            item:
                "The item argument represents a node
                in the FST. It can take the form of
                a string, a dict, or a list."
            render_key:
                "The render_key argument represents
                    the key used to access this child
                node from its parent. It is represented
                by a string if the parent node was
                a dict or by an integer if the
                parent node was a list."

        returns:
            None
        ...

        """
        is_dict     = key_type in ('node',   'key')
        is_string   = key_type in ('string', 'constant')
        # is_list     = key_type in ('list',)

        block_tag   = 'div'
        flow_tag    = 'span'

        if is_dict:
            # is_whitespace = fst_type in ('endl', 'space')
            fst_type = item['type']

            TEMP_DELETEME.add(fst_type)

            if fst_type in Walker.FLOW_NODES:
                self._add_child(flow_tag, **{
                    'class': html.escape(fst_type, quote = True)
                })
            if fst_type in Walker.BLOCK_NODES:
                self._add_child(block_tag, **{
                    'class': html.escape(fst_type, quote = True)
                })
        elif is_string:
            self._add_content(item)

        self.fst_path.append((key_type, render_key, item))
        super(Walker, self).before(key_type, item, render_key)

    # -------------------------------------------------------------------------
    def after(self, key_type, item, render_key):
        """
        Render ending tag after each FST node is visited.

        ---
        type: method

        args:
            self:
                An object of type Walker.
            key_type:
                "key_type is a string argument that
                indicates the type of the node and
                thus the data type of the item
                argument. It can take one of five
                values:- 'constant', 'node', 'key',
                'list', or 'formatting'. A 'constant'
                key_type indicates that item is a
                string. A 'node' key_type indicates
                that item is a dict. A 'key'
                key_type indicates that item is an
                element of a dict. A 'list' key_type
                indicates that item is a list, and
                a 'formatting' key_type indicates
                that the item is a list specialised
                in formatting."
            item:
                "The item argument represents a node
                in the FST. It can take the form of
                a string, a dict, or a list."
            render_key:
                "The render_key argument represents
                the key used to access this child
                node from its parent. It is represented
                by a string if the parent node was
                a dict or by an integer if the
                parent node was a list."

        returns:
            None
        ...

        """
        stop = super(Walker, self).after(key_type, item, render_key)
        self.fst_path.pop()
        if key_type in ('node', 'key'):
            if item['type'] in Walker.FLOW_NODES:
                self._pop_xml()
            if item['type'] in Walker.BLOCK_NODES:
                self._pop_xml()
        return stop

    # -------------------------------------------------------------------------
    def _pop_xml(self):
        """
        Pop the stack.

        ---
        type:   method
        ...

        """
        self.prev_element = self.xml_path.pop()
        self.xml_element  = self.xml_path[-1]

    # -------------------------------------------------------------------------
    def _add_sibling(self, tag, **attrib):
        """
        Create a sibling XML element.

        ---
        type:   method
        ...

        """
        self._pop_xml()
        self._add_child(tag, **attrib)

    # -------------------------------------------------------------------------
    def _add_child(self, tag, **attrib):
        """
        Create a child XML element.

        ---
        type:   method
        ...

        """
        self.xml_element = xml.etree.ElementTree.SubElement(
                                                        self.xml_element, tag)
        self.xml_path.append(self.xml_element)
        self.prev_element = None

        for (key, value) in attrib.items():
            self.xml_element.attrib[key] = value

    # -------------------------------------------------------------------------
    def _add_empty_child(self, tag, **attrib):
        """
        Add an empty (self-closing) XML element.

        ---
        type:   method
        ...

        """
        self._add_child(tag, **attrib)
        self._pop_xml()

    # -------------------------------------------------------------------------
    def _add_content(self, content):
        """
        Add content to the current XML element.

        Content is either added to the text field
        of the current element or to the tail field
        of the previous element.

        ---
        type:   method
        ...

        """
        for fragment in _split(content.replace(' ', '\u00A0')):

            if fragment is None:
                continue

            elif _is_newline(fragment):
                self.iline += 1
                self._add_empty_child('br')

            elif self.prev_element is not None:
                self._add_tail(fragment)

            else:
                self._add_text(fragment)

    # -------------------------------------------------------------------------
    def _add_tail(self, fragment):
        """
        Add a fragment of content to the tail field of the previous element.

        ---
        type:   method
        ...

        """
        if self.prev_element.tail is None:
            self.prev_element.tail = fragment
        else:
            self.prev_element.tail += fragment

    # -------------------------------------------------------------------------
    def _add_text(self, fragment):
        """
        Add a fragment of content to the text field of the current element.

        ---
        type:   method
        ...

        """
        if self.xml_element.text is None:
            self.xml_element.text = fragment
        else:
            self.xml_element.text += fragment


# -----------------------------------------------------------------------------
def _split(text):
    """
    Return an iterator over the lines and line-endings in a piece of text.

    ---
    type:   function
    ...

    """
    return baron.utils.split_on_newlines(text)


# -----------------------------------------------------------------------------
def _is_newline(text):
    """
    Return true if text is a newline, false otherwise.

    ---
    type:   function
    ...

    """
    return baron.utils.is_newline(text)
