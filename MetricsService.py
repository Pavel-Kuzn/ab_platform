import pandas as pd

class MetricsService:

    def __init__(self, data_service):
        """Класс для вычисления метрик.

        :param data_service (DataService): объект класса, предоставляющий доступ к данным.
        """
        self.data_service = data_service

    def _get_data_subset(self, table_name, begin_date, end_date, user_ids=None, columns=None):
        """Возвращает часть таблицы с данными."""
        return self.data_service.get_data_subset(table_name, begin_date, end_date, user_ids, columns)

    def _calculate_response_time(self, begin_date, end_date, user_ids):
        """Вычисляет значения времени обработки запроса сервером.
        
        Нужно вернуть значения user_id и load_time из таблицы 'web-logs', отфильтрованные по date и user_id.
        Считаем, что каждый запрос независим, поэтому группировать по user_id не нужно.

        :param begin_date, end_date (datetime): период времени, за который нужно считать значения.
        :param user_id (None, list[str]): id пользователей, по которым нужно отфильтровать полученные значения.
        
        :return (pd.DataFrame): датафрейм с двумя столбцами ['user_id', 'metric']
        """
        df = self._get_data_subset(table_name='web-logs', begin_date=begin_date, end_date=end_date, user_ids=user_ids) \
                    .rename(columns={'load_time': 'metric'})
        return df[['user_id', 'metric']]

    def _calculate_revenue_web(self, begin_date, end_date, user_ids):
        """Вычисляет значения выручки с пользователя за указанный период
        для заходивших на сайт в указанный период.

        Эти данные нужны для экспериментов на сайте, когда в эксперимент попадают только те, кто заходил на сайт.
        
        Нужно вернуть значения user_id и выручки (sum(price)).
        Данные о ценах в таблице 'sales'. Данные о заходивших на сайт в таблице 'web-logs'.
        Если пользователь зашёл на сайт и ничего не купил, его суммарная стоимость покупок равна нулю.
        Для каждого user_id должно быть ровно одно значение.

        :param begin_date, end_date (datetime): период времени, за который нужно считать значения.
            Также за этот период времени нужно выбирать пользователей, которые заходили на сайт.
        :param user_id (None, list[str]): id пользователей, по которым нужно отфильтровать полученные значения.
        
        :return (pd.DataFrame): датафрейм с двумя столбцами ['user_id', 'metric']
        """
        ids = self._get_data_subset(table_name='web-logs', begin_date=begin_date, end_date=end_date, user_ids=user_ids)['user_id']
        df_sales = self._get_data_subset(table_name='sales', begin_date=begin_date, end_date=end_date, user_ids=user_ids)[['user_id', 'price']]
        # Группируем по user_id и суммируем значения цен
        df_revenue = df_sales.groupby('user_id', as_index=False)['price'].sum()
        # Оставляем только те записи, которые есть в таблице web-logs
        df_revenue = df_revenue[df_revenue['user_id'].isin(ids)]
        # Переименовываем столбец
        df_revenue = df_revenue.rename(columns={'price': 'metric'})
        all_users = set(ids)
        purchased_users = set(df_revenue['user_id'])
        non_purchased_users = all_users - purchased_users

        # Создаем датафрейм для пользователей, которые не совершили покупок и присваиваем им метрику 0
        df_no_purchase = pd.DataFrame({'user_id': list(non_purchased_users), 'metric': 0})

        # Объединяем два датафрейма
        result_df = pd.concat([df_revenue, df_no_purchase], ignore_index=True)
        return result_df


    def _calculate_revenue_all(self, begin_date, end_date, user_ids):
        """Вычисляет значения выручки с пользователя за указанный период
        для заходивших на сайт до end_date.

        Эти данные нужны, например, для экспериментов с рассылкой по email,
        когда в эксперимент попадают те, кто когда-либо оставил нам свои данные.
        
        Нужно вернуть значения user_id и выручки (sum(price)).
        Данные о ценах в таблице 'sales'. Данные о заходивших на сайт в таблице 'web-logs'.
        Если пользователь ничего не купил за указанный период, его суммарная стоимость покупок равна нулю.
        Для каждого user_id должно быть ровно одно значение.

        :param begin_date, end_date (datetime): период времени, за который нужно считать значения.
            Нужно выбирать пользователей, которые хотя бы раз заходили на сайт до end_date.
        :param user_id (None, list[str]): id пользователей, по которым нужно отфильтровать полученные значения.
        
        :return (pd.DataFrame): датафрейм с двумя столбцами ['user_id', 'metric']
        """
        ids = self._get_data_subset(table_name='web-logs', begin_date=None, end_date=end_date, user_ids=user_ids)['user_id']
        df_sales = self._get_data_subset(table_name='sales', begin_date=begin_date, end_date=end_date, user_ids=user_ids)[['user_id', 'price']]
        # Группируем по user_id и суммируем значения цен
        df_revenue = df_sales.groupby('user_id', as_index=False)['price'].sum()
        # Оставляем только те записи, которые есть в таблице web-logs
        df_revenue = df_revenue[df_revenue['user_id'].isin(ids)]
        # Переименовываем столбец
        df_revenue = df_revenue.rename(columns={'price': 'metric'})

        # Создаем список пользователей, которые заходили на сайт, но ничего не купили
        all_users = set(ids)
        purchased_users = set(df_revenue['user_id'])
        non_purchased_users = all_users - purchased_users

        # Создаем датафрейм для пользователей, которые не совершили покупок и присваиваем им метрику 0
        df_no_purchase = pd.DataFrame({'user_id': list(non_purchased_users), 'metric': 0})

        # Объединяем два датафрейма
        result_df = pd.concat([df_revenue, df_no_purchase], ignore_index=True)
        return result_df
        

    def calculate_metric(self, metric_name, begin_date, end_date, user_ids=None):
        """Считает значения для вычисления метрик.

        :param metric_name (str): название метрики
        :param begin_date (datetime): дата начала периода (включая границу)
        :param end_date (datetime): дата окончания периода (не включая границу)
        :param user_ids (list[str], None): список пользователей.
            Если None, то вычисляет значения для всех пользователей.
        :return df: columns=['user_id', 'metric']
        """
        if metric_name == 'response time':
            return self._calculate_response_time(begin_date, end_date, user_ids)
        elif metric_name == 'revenue (web)':
            return self._calculate_revenue_web(begin_date, end_date, user_ids)
        elif metric_name == 'revenue (all)':
            return self._calculate_revenue_all(begin_date, end_date, user_ids)
        else:
            raise ValueError('Wrong metric name')
        
    def process_outliers(self, metrics, design):
        """Возвращает новый датафрейм с обработанными выбросами в измерениях метрики.

        :param metrics (pd.DataFrame): таблица со значениями метрики, columns=['user_id', 'metric'].
        :param design (Design): объект с данными, описывающий параметры эксперимента.
        :return df: columns=['user_id', 'metric']
        """
        # YOUR_CODE_HERE

        if design.metric_outlier_process_type == 'drop':
            metrics = metrics[(metrics['metric'] >= design.metric_outlier_lower_bound) &
                              (metrics['metric'] <= design.metric_outlier_upper_bound)]
            
        if design.metric_outlier_process_type == 'clip':
            metrics['metric'].clip(lower=design.metric_outlier_lower_bound, upper=design.metric_outlier_upper_bound, inplace=True)

        return metrics