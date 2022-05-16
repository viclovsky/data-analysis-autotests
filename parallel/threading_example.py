import concurrent.futures
import threading
import time

import requests

from testdata import get_ids, get_url

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def calculate(id):
    session = get_session()
    with session.get(get_url(id)) as response:
        return response.json()['name']


def get_values(ids):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.map(calculate, ids)


if __name__ == "__main__":
    start_time = time.time()
    get_values(get_ids())
    duration = time.time() - start_time
    print("--- %s seconds ---" % (time.time() - start_time))
