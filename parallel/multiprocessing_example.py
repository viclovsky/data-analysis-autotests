import multiprocessing
import time

import requests

from testdata import get_ids, get_url

session = None


def set_global_session():
    global session
    if not session:
        session = requests.Session()


def calculate(id):
    with session.get(url=get_url(id)) as response:
        name = multiprocessing.current_process().name
        return response.json()['name']


def get_values(ids):
    with multiprocessing.Pool(initializer=set_global_session) as pool:
        pool.map(calculate, ids)


if __name__ == "__main__":
    start_time = time.time()
    get_values(get_ids())
    duration = time.time() - start_time
    print("--- %s seconds ---" % (time.time() - start_time))
