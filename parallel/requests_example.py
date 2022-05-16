import time

import requests

from testdata import get_ids, get_url


def calculate(id, session):
    with session.get(url=get_url(id)) as response:
        return (id, response.json()['name'])


def get_values(ids):
    with requests.Session() as session:
        for id in ids:
            calculate(id, session)


if __name__ == "__main__":
    start_time = time.time()
    get_values(get_ids())
    duration = time.time() - start_time
    print("--- %s seconds ---" % (time.time() - start_time))
