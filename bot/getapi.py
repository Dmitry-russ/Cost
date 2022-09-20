import requests


def get_token(USER_ENDPOINT, USER, PASSWORD) -> str:
    """Функция получения токена для доступа к api."""

    response = requests.post(
        url=USER_ENDPOINT,
        data={'username': USER, 'password': PASSWORD}
    ).json()
    return f'Bearer {response.get("access")}'


def post_api(ENDPOINT, API_TOKEN, chat_id, cost, group_id):
    """Запись нового расхода в базу данных api."""

    requests.post(
        url=ENDPOINT,
        headers={'Authorization': API_TOKEN},
        data={'chat_id': chat_id, 'cost': cost, 'group': group_id}
    ).json()


def group_load(GROUP_ENDPOINT, API_TOKEN) -> list:
    """Запрос списка действующих групп расходов."""

    response = requests.get(
        url=GROUP_ENDPOINT,
        headers={'Authorization': API_TOKEN},
    )
    return [r.get("title") for r in response.json()]


def group_id_title(GROUP_ENDPOINT, API_TOKEN) -> dict:
    """Запрос словаря id=группа для соответствия имен при выводе."""

    response = requests.get(
        url=GROUP_ENDPOINT,
        headers={'Authorization': API_TOKEN},
    )
    group_id_title_dict: dict = {}
    for r in response.json():
        group_id_title_dict[r.get("id")] = r.get("title")
    return group_id_title_dict


def get_all_costs(ENDPOINT, chat_id, API_TOKEN) -> requests:
    """Запрос данных о всех сохраненных расходах пользователя."""

    response = requests.get(
        url=ENDPOINT+str(chat_id),
        headers={'Authorization': API_TOKEN},
        )
    return response
