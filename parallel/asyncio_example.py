import asyncio
import time

import httpx
from httpx import Limits

from testdata import get_ids, get_url


async def calculate(client, id):
    response = await client.get(url=get_url(id))
    return response.json()['name']


async def get_values(client, ids):
    async with client:
        tasks = []
        for id in ids:
            tasks.append(asyncio.ensure_future(calculate(client, id)))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    client = httpx.AsyncClient(limits=Limits(max_keepalive_connections=0,
                                             keepalive_expiry=0))
    start_time = time.time()
    asyncio.run(get_values(client, get_ids()))
    print("--- %s seconds ---" % (time.time() - start_time))
