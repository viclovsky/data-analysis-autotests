import asyncio
import functools

import aiometer
import httpx
import pytest
from httpx import Limits

from testdata import get_url, get_ids


async def calculate(client, base_uri, id):
    response = await client.get(url=get_url(id=id, url=base_uri))
    return (id, response.json()['name'])


async def get_value(ids, base_uri):
    async with httpx.AsyncClient(limits=Limits(max_keepalive_connections=0, keepalive_expiry=0),
                                 timeout=30.0) as client:
        tasks = [functools.partial(calculate, client, base_uri, id) for id in ids]
        data = await aiometer.run_all(tasks, max_per_second=100)
        return data


async def get_values(ids, first_uri, second_uri):
    return await asyncio.gather(
        *[get_value(ids=ids, base_uri=first_uri),
          get_value(ids=ids, base_uri=second_uri)])


@pytest.fixture(scope='class')
def df_data():
    count = 150
    expected_uri = 'https://pokeapi.co'
    actual_uri = 'https://pokeapi.co'

    ids = get_ids(count)
    data_expected, data_actual = asyncio.run(get_values(ids=ids,
                                                        first_uri=expected_uri,
                                                        second_uri=actual_uri))
    return data_expected, data_actual


def test_aiometer(df_data):
    data_expected, data_actual = df_data
    print(data_actual)
    print(data_expected)
