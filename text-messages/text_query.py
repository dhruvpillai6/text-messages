import sqlite3
import pandas
import os
from pathlib import Path

pandas.set_option('display.max_columns', None)
pandas.options.mode.chained_assignment = None

def connect_to_iMessage_database():
    user = os.path.expanduser('~')
    path_to_database = Path(f'{user}/Library/Messages/chat.db')
    return sqlite3.connect(path_to_database)

def text_query(WHERE='', LIMIT=''):
    conn = connect_to_iMessage_database()
    SELECT_string = 'SELECT ' + \
                    'datetime(message.date/1000000000 + strftime("%s", "2001-01-01"),' \
                    '"unixepoch", "localtime") AS local_date, handle.id, ' \
                    'message.handle_id, message.text, message.is_from_me AS sent '
    FROM_string = 'FROM ' + \
                  'message '
    INNER_JOIN_string = 'INNER JOIN '+ \
                        'handle ON message.handle_id = handle.ROWID '
    ORDER_BY_string = 'ORDER BY ' + \
                      'date DESC '
    if WHERE == ('' or None):
        WHERE_string = ''
    else:
        WHERE_string = 'WHERE ' + \
                        str(WHERE) + ' '
    if LIMIT == ('' or None):
        LIMIT_string = ''
    else:
        LIMIT_string = 'LIMIT ' + \
                        str(LIMIT) + ' '
    SQL_STRING = SELECT_string + FROM_string + INNER_JOIN_string + WHERE_string + \
                 ORDER_BY_string + LIMIT_string

    return pandas.read_sql_query(SQL_STRING, conn)

def generate_address_book():
    conn = connect_to_iMessage_database()
    dataframe = pandas.read_sql_query('SELECT ROWID, id FROM handle', conn)
    dataframe = dataframe.rename(columns={'ROWID': 'handle_id'})
    return dataframe.set_index('handle_id')

if __name__ == '__main__':
    # print(type(text_query(WHERE='handle_id = 1', LIMIT=10).loc[0, 'local_date']))
    print(generate_address_book())