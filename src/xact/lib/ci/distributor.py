# -*- coding: utf-8 -*-
"""
Continuous integration distributor for xact.

"""


import os.path


META_DIR_NAME      = '_meta'
TEMPLATE_DIR_NAME  = '_template'
SPEC_FILE_PREFIX   = 'spec_'
TEST_DATA_DIR_NAME = 'data'


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
    list_name_output = ('all', 'python', 'xact')
    for name in list_name_output:
        outputs[name].clear()
        outputs[name]['ena']  = False
        outputs[name]['list'] = []

    if not inputs['content']['ena']:
        return

    for content in inputs['content']['list']:
        filepath = content['filepath']

        outputs['all']['list'].append(content)

        if _is_python_file(filepath):
            outputs['python']['list'].append(content)

        elif _is_xact_cfg_file(filepath):
            outputs['xact']['list'].append(content)

    for name in list_name_output:
        if outputs[name]['list']:
            outputs[name]['ena'] = True


# -----------------------------------------------------------------------------
def _design_filepath_for(filepath_spec):
    """
    Return the design doc filepath corresponding to the specification provided.

    """
    (dirpath_spec,   filename_spec)  = os.path.split(filepath_spec)
    (rootname_spec,  fileext_spec)   = os.path.splitext(filename_spec)
    (dirpath_module, dirname_spec)   = os.path.split(dirpath_spec)
    (_,              dirname_module) = os.path.split(dirpath_module)

    assert dirname_spec == META_DIR_NAME
    assert filename_spec.startswith(SPEC_FILE_PREFIX)

    # Tests for packages are named after the package
    # name, not the module name.
    #
    design_name = rootname_spec.replace(SPEC_FILE_PREFIX, '')
    if design_name == dirname_module:
        filename_module = '__init__.py'
    else:
        filename_module = '{name}{ext}'.format(name = design_name,
                                               ext  = fileext_spec)

    filepath_module = os.path.join(dirpath_module, filename_module)
    return filepath_module


# -----------------------------------------------------------------------------
def _specification_filepath_for(filepath_design):
    """
    Return the filepath of the specification for the specified design document.

    """
    (dirpath_design, filename_design) = os.path.split(filepath_design)
    (rootname_design, fileext_design) = os.path.splitext(filename_design)
    dirpath_spec                      = os.path.join(
                                                dirpath_design, META_DIR_NAME)

    # Tests for packages are named after the package
    # name, not the module name.
    #
    if (fileext_design == '.py') and (rootname_design == '__init__'):
        name = os.path.basename(dirpath_design)
    else:
        name = rootname_design

    filename_spec = '{prefix}{name}{ext}'.format(prefix = SPEC_FILE_PREFIX,
                                                 name   = name,
                                                 ext    = fileext_design)
    filepath_spec = os.path.join(dirpath_spec, filename_spec)
    return filepath_spec


# -----------------------------------------------------------------------------
def _is_design_document(filepath):
    """
    Return True if filepath is a design document.

    Software source files are either used to specify
    behavior (in the form of unit tests, component
    tests etc...) or to specify design.

    """
    if _is_specification_file(filepath):
        return False

    if not _is_source_file(filepath):
        return False

    return True


# -----------------------------------------------------------------------------
def _is_specification_file(filepath):
    """
    Return True if filepath is for a specification file.

    Specification files contain the requirements
    specifications and unit tests that together
    document the behaviour of design elements
    contained within a corresponding design
    document.

    """
    (dirpath, filename) = os.path.split(filepath)
    (_, dirname)        = os.path.split(dirpath)
    return (     _is_source_file(filepath)
             and (dirname == META_DIR_NAME)
             and filename.startswith(SPEC_FILE_PREFIX))


# -----------------------------------------------------------------------------
def _is_source_file(filepath):
    """
    Return True if filepath iswritten in a recognised programming language.

    """
    return _is_python_file(filepath) or _is_cpp_file(filepath)


# -----------------------------------------------------------------------------
def _is_xact_cfg_file(filepath):
    """
    Return True if filepath is an xact config file.

    """
    return filepath.endswith('.cfg.yaml')


# -----------------------------------------------------------------------------
def _is_python_file(filepath):
    """
    Return True if filepath is a document written in the Python language.

    """
    return filepath.endswith('.py')


# -----------------------------------------------------------------------------
def _is_cpp_file(filepath):
    """
    Return True if filepath is a document written in the C++ language.

    """
    return filepath.endswith('.cpp') or filepath.endswith('.hpp')


# -----------------------------------------------------------------------------
def _is_test_data(filepath):
    """
    Return true if filepath lies within a test data directory.

    """
    testdata_pattern = (   os.sep + META_DIR_NAME
                         + os.sep + TEST_DATA_DIR_NAME
                         + os.sep)
    return testdata_pattern in filepath


# -----------------------------------------------------------------------------
def _is_test_config(filepath):
    """
    Return true if filepath is for a test configuration file.

    """
    (dirpath, filename) = os.path.split(filepath)
    (_, dirname)        = os.path.split(dirpath)
    return (     (dirname == META_DIR_NAME)
             and (filename == 'conftest.py'))


# -----------------------------------------------------------------------------
def _is_test_related(filepath):
    """
    Return true if filepath is a test or test related file. False otherwise.

    """
    return (    _is_specification_file(filepath)
             or _is_test_data(filepath)
             or _is_test_config(filepath))


# -----------------------------------------------------------------------------
def _is_tool_config(filepath):
    """
    Return true if filepath is a tool configuration file.

    """
    (_, filename) = os.path.split(filepath)
    return filename in ('.coveragerc',
                        '.gitignore',
                        'pytest.ini',
                        'specification.pylintrc',
                        'design.pylintrc')


# -----------------------------------------------------------------------------
def _is_experimental(filepath):
    """
    Return true if filepath is an experimental design document.

    """
    return True if 'h50_research' in filepath else False
