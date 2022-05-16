import io
import random
from copy import deepcopy

import allure
import numpy as np
import pandas as pd
import pytest
import seaborn
from seaborn import FacetGrid


def get_gamma(alfa=2.0, beta=2.0):
    result = []
    for number in range(10000):
        result.append((number, random.gammavariate(alfa, beta)))
    return result


def attach_describe(data):
    allure.attach(str(data['value'].describe()), "describe.txt", allure.attachment_type.TEXT)


@pytest.fixture(scope='class')
def df_data():
    df_expected = get_gamma(2.0, 2.1)
    df_actual = get_gamma(3.0, 2.0)

    df_actual = pd.DataFrame(df_actual, columns=['id', 'value'])
    df_expected = pd.DataFrame(df_expected, columns=['id', 'value'])

    attach_describe(df_actual)
    return df_expected, df_actual


@pytest.mark.skip
@allure.title("Строим гистограмму гамма распределения")
def test_searborn_graph_example(df_data):
    df_expected, df_actual = df_data
    sns_plot = seaborn.histplot(df_expected['value'], kde=True)
    buf = io.BytesIO()
    fig = sns_plot.get_figure()
    # A4 * 2
    fig.set_size_inches(23.4, 16.54)
    fig.savefig(buf)
    allure.attach(buf.getvalue(), "hist.png", allure.attachment_type.PNG)


@allure.title("Строим две гистограммы на одном графике")
def test_searborn_graph_diff_example(df_data):
    df_expected, df_actual = deepcopy(df_data)
    result = df_actual.merge(df_expected,
                             on='id',
                             suffixes=('_actual', '_expected'))
    sns_plot = seaborn.histplot(result[['value_actual', 'value_expected']],
                                kde=True)
    buf = io.BytesIO()
    fig = sns_plot.get_figure()
    # A4 * 2
    fig.set_size_inches(23.4, 16.54)
    fig.savefig(buf)
    allure.attach(buf.getvalue(), "hist_diff.png", allure.attachment_type.PNG)


@pytest.mark.skip
@allure.title("Строим гистограмму разницы двух выборок")
def test_searborn_graph_compare_example(df_data):
    df_expected, df_actual = df_data
    # df_actual.compare(df_expected)

    df = deepcopy(df_expected)
    df['new_value'] = df_actual['value']
    df['value_diff'] = \
        np.where(df['new_value'] == df['value'], 0,
                 df['new_value'] - df['value'])

    sns_plot = seaborn.histplot(df['value_diff'], kde=True)
    buf = io.BytesIO()
    fig = sns_plot.get_figure()
    # A4 * 2
    fig.set_size_inches(23.4, 16.54)
    fig.savefig(buf)
    allure.attach(buf.getvalue(), "hist.png", allure.attachment_type.PNG)


@allure.title("Строим q/q графики")
def test_searborn_graph_qq_quantile(df_data):
    df_expected, df_actual = df_data
    percs = np.linspace(0, 100, 600)
    qn_expected = np.percentile(df_expected['value'], percs)
    qn_actual = np.percentile(df_actual['value'], percs)
    df = pd.DataFrame({'expected': qn_expected, 'actual': qn_actual})

    sns_plot: FacetGrid = seaborn.lmplot(x="expected", y="actual", data=df)

    buf = io.BytesIO()
    fig = sns_plot.figure
    # A4 * 2
    fig.set_size_inches(23.4, 16.54)
    fig.savefig(buf)
    allure.attach(buf.getvalue(), "qq.png", allure.attachment_type.PNG)


@allure.title("Строим графики для перцентилей")
def test_searborn_graph_compare_quantile(df_data):
    df_expected, df_actual = df_data
    percs = np.linspace(0, 100, 100)
    qn_expected = np.percentile(df_expected['value'], percs)
    qn_actual = np.percentile(df_actual['value'], percs)
    persentiles = np.concatenate([percs, percs])
    qns = np.concatenate([qn_expected, qn_actual])
    types = ["expected"] * percs.size + ["actual"] * percs.size
    df = pd.DataFrame({'persentile': persentiles, 'persentile_value': qns, 'values': types})
    g = FacetGrid(df, row="values")
    g.map(seaborn.scatterplot, "persentile", "persentile_value")

    buf = io.BytesIO()
    fig = g.figure
    # A4 * 2
    fig.set_size_inches(23.4, 16.54)
    fig.savefig(buf)
    allure.attach(buf.getvalue(), "quantile.png", allure.attachment_type.PNG)
