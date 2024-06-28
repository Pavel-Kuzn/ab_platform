from pydantic import BaseModel


class Design(BaseModel):
    """Дата-класс с описание параметров эксперимента.

    statistical_test - тип статтеста. ['ttest', 'bootstrap']
    effect - размер эффекта в процентах
    alpha - уровень значимости
    beta - допустимая вероятность ошибки II рода
    bootstrap_iter - количество итераций бутстрепа
    bootstrap_ci_type - способ построения доверительного интервала. ['normal', 'percentile', 'pivotal']
    bootstrap_agg_func - метрика эксперимента. ['mean', 'quantile 95']
    metric_name - название целевой метрики эксперимента
    metric_outlier_lower_bound - нижняя допустимая граница метрики, всё что ниже считаем выбросами
    metric_outlier_upper_bound - верхняя допустимая граница метрики, всё что выше считаем выбросами
    metric_outlier_process_type - способ обработки выбросов. ['drop', 'clip'].
        'drop' - удаляем измерение, 'clip' - заменяем выброс на значение ближайшей границы (lower_bound, upper_bound).
    """
    statistical_test: str = 'ttest'
    effect: float = 3.
    alpha: float = 0.05
    beta: float = 0.1
    bootstrap_iter: int = 1000
    bootstrap_ci_type: str = 'normal'
    bootstrap_agg_func: str = 'mean'
    metric_name: str
    metric_outlier_lower_bound: float
    metric_outlier_upper_bound: float
    metric_outlier_process_type: str