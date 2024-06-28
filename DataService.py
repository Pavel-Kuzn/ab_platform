import pandas as pd

from datetime import datetime


class DataService:

    def __init__(self, table_name_2_table):
        """Класс, предоставляющий доступ к сырым данным.
        
        :param table_name_2_table (dict[str, pd.DataFrame]): словарь таблиц с данными.
            Пример, {
                'sales': pd.DataFrame({'sale_id': ['123', ...], ...}),
                ...
            }. 
        """
        self.table_name_2_table = table_name_2_table

    def get_data_subset(self, table_name, begin_date, end_date, user_ids=None, columns=None):
        """Возвращает подмножество данных.

        :param table_name (str): название таблицы с данными.
        :param begin_date (datetime.datetime): дата начала интервала с данными.
            Пример, df[df['date'] >= begin_date].
            Если None, то фильтровать не нужно.
        :param end_date (None, datetime.datetime): дата окончания интервала с данными.
            Пример, df[df['date'] < end_date].
            Если None, то фильтровать не нужно.
        :param user_ids (None, list[str]): список user_id, по которым нужно предоставить данные.
            Пример, df[df['user_id'].isin(user_ids)].
            Если None, то фильтровать по user_id не нужно.
        :param columns (None, list[str]): список названий столбцов, по которым нужно предоставить данные.
            Пример, df[columns].
            Если None, то фильтровать по columns не нужно.

        :return df (pd.DataFrame): датафрейм с подмножеством данных.
        """
        if begin_date:
            table = self.table_name_2_table[table_name][self.table_name_2_table[table_name]['date'] >= begin_date]
        else:
            table = self.table_name_2_table[table_name]

        if end_date:
            table = table[table['date'] <= end_date]

        if user_ids:
            table = table[table['user_id'].isin(user_ids)]

        if columns:
            table = table[columns]

        return table
    
    

