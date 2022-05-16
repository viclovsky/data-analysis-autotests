import random
from copy import deepcopy

import allure
import numpy as np
import pandas as pd
import pytest

MIN_VALUE = 0
MAX_VALUE = 10000


def get_gamma(alfa=2.0, beta=2.0):
    result = []
    for number in range(10000):
        result.append((number, random.gammavariate(alfa, beta)))
    return result


def attach_describe(data):
    allure.attach(str(data['value'].describe()), "describe.txt", allure.attachment_type.TEXT)


def attach_data_csv(data):
    allure.attach(str(data.to_csv(sep='\t', encoding='utf-8', index=False)), "df.csv",
                  allure.attachment_type.TEXT)


def is_less_or_equal_delta(actual, expected, delta):
    # 1. на сколько одно значение изменилось относительно другого
    # (в процентном соотношении)
    # 2. либо модель разности < delta
    assert abs(actual - expected) <= float(delta)


def is_empty_df(df):
    with allure.step("Проверяем, что data frame пустой"):
        assert df.empty == bool(True)


@pytest.fixture(scope='class')
def df_data():
    df_expected = get_gamma(2.0, 2.1)
    df_actual = get_gamma(3.0, 2.0)

    df_actual = pd.DataFrame(df_actual, columns=['id', 'value']) \
        .set_index('id')
    df_expected = pd.DataFrame(df_expected, columns=['id', 'value']) \
        .set_index('id')

    attach_describe(df_actual)
    return df_expected, df_actual


@allure.description("0. Получаем пользователей\n"
                    "1. Делаем запросы к testing и stable\n"
                    "2. Проверяем, что среднее значение/среднеквадратичное отклонение и прочие метрики не меняются")
class TestValues:

    @allure.title("Сравниваем по значениям value")
    def test_compare_value(self, df_data):
        df_expected, df_actual = df_data

        df_compare = deepcopy(df_expected)
        df_compare['new_value'] = df_actual['value']
        df_compare['value_diff'] = \
            np.where(df_compare['new_value'] == df_compare['value'], 0,
                     df_compare['new_value'] - df_compare['value'])
        df_compare = df_compare[df_compare['value_diff'] != 0]
        attach_data_csv(df_compare)

        df = df_actual.compare(df_expected)
        assert df.empty == bool(True)

    @allure.title("Вычисляем и сравниваем квантиль {q}")
    @pytest.mark.parametrize('q', [0.25, 0.75, 0.95])
    def test_quantile(self, q, df_data):
        df_expected, df_actual = df_data

        actual = df_actual['value'].quantile(q)
        expected = df_expected['value'].quantile(q)

        is_less_or_equal_delta(actual=actual, expected=expected, delta=0.1)

    @allure.title("Проверяем, что медиана (0,5-квантиль) не изменилась")
    def test_median(self, df_data):
        df_expected, df_actual = df_data

        actual = df_actual['value'].median()
        expected = df_expected['value'].median()

        assert actual == expected

    @allure.title("Проверяем, что среднее значение не изменилось")
    def test_mean(self, df_data):
        df_expected, df_actual = df_data

        # delta = 0
        actual = df_actual['value'].mean()
        expected = df_expected['value'].mean()

        assert actual == expected

    @allure.title("Проверяем, что стандартное "
                  "или среднеквадратичное отклонение: не изменилась")
    def test_std(self, df_data):
        df_expected, df_actual = df_data

        # delta = 0
        # ddof=0 - вычисляем смещенное значение стандартного отклонения
        actual = df_actual['value'].std(ddof=0)
        expected = df_expected['value'].std(ddof=0)

        assert actual == expected

    @allure.title("Проверяем, что дисперсия («разброс» данных вокруг среднего значения) не изменилась")
    def test_var(self, df_data):
        df_expected, df_actual = df_data

        delta = 0
        actual = df_actual['value'].var()
        expected = df_expected['value'].var()

        assert actual == expected

    @allure.title(f"Проверяем, что максимальное значение "
                  f"не изменилось и равно limit = {MAX_VALUE}")
    def test_max_should_be_equal(self, df_data):
        df_expected, df_actual = df_data

        actual = df_actual['value'].max()
        expected = df_expected['value'].max()
        assert actual == expected == MAX_VALUE

    @allure.title(f"Проверяем, что минимальное значение "
                  f"не изменилось и равно value = {MIN_VALUE}")
    def test_min_should_be_equal(self, df_data):
        df_expected, df_actual = df_data

        actual = df_actual['value'].min()
        expected = df_expected['value'].min()
        assert actual == expected == MIN_VALUE

    @allure.title("Вычисляем коэффициент асимметрии (степень скошенности)")
    def test_skew(self, df_data):
        df_expected, df_actual = df_data

        actual = df_actual['value'].skew()
        expected = df_expected['value'].skew()
        assert actual == expected
