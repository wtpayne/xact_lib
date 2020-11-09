# -*- coding: utf-8 -*-
"""
Sqlite writer node.

"""


import re
import sqlite3


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the sqlite writer node.

    """
    state['connection'] = sqlite3.connect(cfg['filepath_db'])
    state['cursor']     = state['connection'].cursor()
    state['reo_key']    = _compile_regex_list(cfg['list_re_key'])


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the sqlite writer node.

    """
    for dict_output in outputs.values():
        dict_output['ena'] = False

    for (id_input, dict_input) in inputs.items():

        if not dict_input['ena']:
            continue

        if 'query' in dict_input:
            _query(state, outputs, id_input, dict_input['query'])
        else:
            _insert(cursor     = state['cursor'],
                    name_table = id_input,
                    dict_data  = dict_input,
                    reo_key    = state['reo_key'])

    state['connection'].commit()


# -----------------------------------------------------------------------------
def _query(state, outputs, id_output, query_string):
    """
    Execute the specified sql query.

    """
    try:
        state['cursor'].execute(query_string)
    except sqlite3.OperationalError as err:
        if 'no such table' in str(err):
            return
        else:
            raise
    list_name_col      = [desc[0] for desc in state['cursor'].description]
    list_row           = state['cursor'].fetchall()
    outputs[id_output]['ena'] = True
    for (icol, name_col) in enumerate(list_name_col):
        outputs[id_output][name_col] = [row[icol] for row in list_row]



# -----------------------------------------------------------------------------
def _insert(cursor, name_table, dict_data, reo_key):
    """
    Insert data into the specified table.

    """
    tup_name_column  = tuple(key for key in dict_data.keys() if key != 'ena')
    num_rows         = _count_rows_ensure_equal(tup_name_column, dict_data)
    cursor.execute(_create_table(
                            name_table, dict_data, reo_key, tup_name_column))
    for irow in range(num_rows):
        sql = _insert_row(name_table, dict_data, tup_name_column, irow)
        cursor.execute(sql)

    # outputs['clock']['ts'] =


# -----------------------------------------------------------------------------
def _insert_row(name_table, dict_data, tup_name_column, irow):
    """
    Return a string containing an sql statement to insert the specified row.

    """
    row            = (dict_data[name][irow] for name in tup_name_column)
    list_item_spec = []

    for item in row:

        if isinstance(item, str):
            item_spec = '"{item}"'.format(item = item)
        elif isinstance(item, int):
            item_spec = '{item}'.format(item = item)
        else:
            item_spec = '{item}'.format(item = item)

        list_item_spec.append(item_spec)

    value_spec = ', '.join(list_item_spec)
    return 'INSERT OR REPLACE INTO {name} VALUES ({values})'.format(
                                                        name   = name_table,
                                                        values = value_spec)

# -----------------------------------------------------------------------------
def _compile_regex_list(regex_list):
    """
    Compile a list of regex strings into a single regular expression object.

    """
    return re.compile('(' + ')|('.join(regex_list) + ')')


# -----------------------------------------------------------------------------
def _count_rows_ensure_equal(tup_name_column, dict_data):
    """
    Return the row count, ensuring it is the same for all columns.

    """
    num_rows = 0
    for name in tup_name_column:
        col = dict_data[name]
        if num_rows == 0:
            num_rows = len(col)
        else:
            assert len(col) == num_rows
    return num_rows


# -----------------------------------------------------------------------------
def _create_table(name_table, dict_data, reo_key, tup_name_column):
    """
    Return a string containing an sql statement to create the specified table.

    """
    list_name_key   = [name for name in tup_name_column
                                        if reo_key.fullmatch(name) is not None]

    map_types = {
        'int':   'INTEGER',
        'float': 'REAL',
        'str':   'TEXT',
        'bytes': 'BLOB'
    }
    list_def_column = []
    for name in tup_name_column:
        item_first       = next(iter(dict_data[name]))
        name_type_py     = type(item_first).__name__
        name_type_sqlite = map_types[name_type_py]
        def_column       = '{name} {name_type}'.format(
                                                name      = name,
                                                name_type = name_type_sqlite)
        if name in list_name_key:
            def_column += ' NOT NULL'
            if len(list_name_key) == 1:
                def_column += ' PRIMARY KEY'

        list_def_column.append(def_column)
    def_column_all = ', '.join(list_def_column)

    if len(list_name_key) > 1:
        keys = ', PRIMARY KEY ({keys})'.format(keys = ', '.join(list_name_key))
    else:
        keys = ''

    return 'CREATE TABLE IF NOT EXISTS {name} ({col}{keys})'.format(
                                                        name = name_table,
                                                        col  = def_column_all,
                                                        keys = keys)


