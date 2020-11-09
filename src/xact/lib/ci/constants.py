# -*- coding: utf-8 -*-
"""
Constants for conformance checking functionality.

...
"""

# There are 5 kind of message types :
#   * (C) convention, for programming standard violation
#   * (R) refactor, for bad code smell
#   * (W) warning, for python specific problems
#   * (E) error, for probable bugs in the code
#   * (F) fatal, if an error occurred which prevented pylint from doing further

# Base id of standard checkers (used in msg and report ids):
# 01: base
# 02: classes
# 03: format
# 04: import
# 05: misc
# 06: variables
# 07: exceptions
# 08: similar
# 09: design_analysis
# 10: newstyle
# 11: typecheck
# 12: logging
# 13: string_format
# 14: string_constant
# 15: stdlib
# 16: python3
# 17-50: not yet used: reserved for future internal checkers.
# 51-99: perhaps used: reserved for external checkers

DESIGN_FILE_READ_ERROR          = 'E7001'
DESIGN_FILE_DECODING_ERROR      = 'E7002'
DESIGN_FILE_SYNTAX_ERROR        = 'E7003'

GCC_UNKNOWN_ERROR               = 'E7101'

CLANG_UNKNOWN_ERROR             = 'E7201'

DEP_NO_CONFIG                   = 'E7301'
DEP_NO_DATA                     = 'E7302'
DEP_POLICY_CONFIG_MISMATCH      = 'E7303'
DEP_SCM_CONFIG_MISMATCH         = 'E7304'
DEP_REGISTER_FORMAT             = 'E7305'
DEP_REGISTER_MISSING_ENTRY      = 'E7306'
DEP_REGISTER_MISSING_FILES      = 'E7307'
DEP_REGISTER_CONFIG_MISMATCH    = 'E7308'
DEP_REGISTER_BUILD_MISMATCH     = 'E7309'


SCHEMA_MISSING                  = 'E7401'
SCHEMA_FAILURE_DATA_FILE        = 'E7402'
SCHEMA_FAILURE_EMBEDDED_DATA    = 'E7403'

MYPY_NONCONFORMITY              = 'E7451'

PYTEST_NO_SPEC                  = 'E7501'
PYTEST_NO_COVERAGE              = 'E7502'
PYTEST_NO_TEST_CLASS            = 'E7503'
PYTEST_BAD_TEST_CLASS           = 'E7504'
PYTEST_TEST_NOT_PASSED          = 'E7505'

ENGDOC_SCHEMA_FAILURE           = 'E7601'
SPHINX_BUILD_FAILURE            = 'E7602'
SPHINX_MISSING_DOC              = 'E7603'

DATA_NAME_ERR_IN_DATA_ROOT      = 'E7701'
DATA_NAME_ERR_IN_COUNTERPARTY   = 'E7702'
DATA_NAME_ERR_IN_YEAR           = 'E7703'
DATA_NAME_ERR_IN_PROJECT        = 'E7704'
DATA_NAME_ERR_IN_TIMEBOX        = 'E7705'
DATA_NAME_ERR_IN_MMDD_DATE      = 'E7706'
DATA_NAME_ERR_IN_PLATFORM       = 'E7707'
DATA_NAME_ERR_IN_RECORDING      = 'E7708'

DATA_FILE_LABELFILE_MISSING     = 'E7750'
DATA_FILE_CATALOG_MISSING       = 'E7751'

DATA_FMT_JSEQ                   = 'E7801'
DATA_FMT_YAML                   = 'E7802'
DATA_FMT_ASF                    = 'E7803'

DATA_FMT_BAD_CATALOG_FORMAT     = 'E7804'
DATA_FMT_BAD_CATALOG_CONTENT    = 'E7805'

DATA_CATALOG_NO_REC_DIR         = 'E7850'
DATA_CATALOG_NO_STREAM_FILE     = 'E7851'
DATA_CATALOG_BAD_UTC_START      = 'E7852'
DATA_CATALOG_BAD_UTC_END        = 'E7853'
DATA_CATALOG_UTC_CONSISTENCY    = 'E7854'
DATA_CATALOG_BAD_SHA256         = 'E7855'
DATA_CATALOG_BAD_SIZE_BYTES     = 'E7856'

DATA_META_BAD_FMT               = 'E7901'
