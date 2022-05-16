MAX_ID = 150
MULTIPLICATOR = 1


def get_ids(count=MAX_ID):
    l = []
    for _ in range(0, MULTIPLICATOR):
        for i in range(1, count):
            l.append(i)
    return l


def get_url(id, url='https://pokeapi.co'):
    return f'{url}/api/v2/pokemon/{id}'
