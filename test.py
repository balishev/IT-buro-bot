import requests
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from dotenv import load_dotenv
import os

from datetime import datetime

def datetime_to_string(dt, format_str="%d.%m.%Y %H:%M:%S"):
    """
    Преобразует объект datetime в строку заданного формата.

    :param dt: объект datetime
    :param format_str: строка формата (по умолчанию "%d.%m.%Y %H:%M:%S")
    :return: строковое представление даты и времени
    """
    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    else:
        raise ValueError("Аргумент должен быть объектом datetime")

# Пример использования:



def get_upcoming_events(city, days_ahead=30, max_events=30):
    # Базовый URL API KudaGo
    base_url = "https://kudago.com/public-api/v1.4/events/"

    # Параметры запроса
    params = {
        'location': city,
        'actual_since': int(datetime.now().timestamp()),
        'actual_until': int((datetime.now() + timedelta(days=days_ahead)).timestamp()),
        'page_size': max_events,
        'lang': 'ru',
        'fields': 'id,title,dates,place,location,is_free,price,site_url',
        'expand': 'dates,place'
    }

    # Отправка GET-запроса
    response = requests.get(base_url, params=params)

    # Проверка успешности запроса
    if response.status_code == 200:
        events = response.json().get('results', [])
        return events
    else:
        print(f"Ошибка при запросе данных: {response.status_code}")
        return []


# Пример использования функции
city = "msk"  # Москва
events = get_upcoming_events(city)
ev_lst = []
for event in events:
    '''print(f"Название: {event['title']}")
    print(f"Дата: {event['dates'][0]['start']}")
    print(f"Место: {event['place']['title'] if event['place'] else 'Не указано'}")
    print(f"Стоимость: {'Бесплатно' if event['is_free'] else event.get('price', 'Не указана')}")
    print(f"Ссылка: {event['site_url']}")
    print("-" * 40)'''
    ev_lst.append(event['title'])


def suggest(interests, events):
    #print('start')
    load_dotenv()
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    # Авторизация в GigaChat
    model = GigaChat(
        credentials=credentials,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        # Отключает проверку наличия сертификатов НУЦ Минцифры
        verify_ssl_certs=False,
    )

    messages = [
        SystemMessage(
            content=f"Ты бот, который помогает иностранному студенту ассимилироваться в России, из предложеного списка мероприятий предложи студенту мероприятия на основе его интересов: {interests}:"
        )
    ]
    #print('1')
    messages.append(HumanMessage(content=str(events)))
    res = model.invoke(messages)
    messages.append(res)
    return res.content


print(suggest('музыка', ev_lst))
