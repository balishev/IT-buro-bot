import sqlite3
import requests
from datetime import datetime

############################
# ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
############################

def init_db(db_name='events.db'):
    """
    Создает таблицу events, если она не существует.
    Будем хранить:
    - source (название источника)
    - event_id (идентификатор на стороне источника)
    - title
    - date
    - link
    - short_desc
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            event_id TEXT,
            title TEXT,
            date TEXT,
            link TEXT,
            short_desc TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_events_to_db(events, db_name='events.db'):
    """
    Сохраняет список словарей events в таблицу events.
    Каждый словарь должен содержать:
    {
      'source': str,
      'event_id': str,
      'title': str,
      'date': str,
      'link': str,
      'short_desc': str
    }
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for ev in events:
        cursor.execute("""
            INSERT INTO events (source, event_id, title, date, link, short_desc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ev.get('source', ''),
            ev.get('event_id', ''),
            ev.get('title', ''),
            ev.get('date', ''),
            ev.get('link', ''),
            ev.get('short_desc', '')
        ))
    conn.commit()
    conn.close()

############################
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
############################

def timestamp_to_str(ts):
    """
    Преобразование Unix timestamp в строку формата 'YYYY-MM-DD HH:MM'.
    """
    if not ts:
        return ''
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return ''

def iso_to_str(iso_str):
    """
    Преобразует ISO-дату '2025-02-11T12:00:00+03:00' к '2025-02-11 12:00'.
    Если iso_str=None, вернём пустую строку.
    """
    if not iso_str:
        return ''
    try:
        # Обрежем смещение, для простоты 16 символов: '2025-02-11T12:00'
        return iso_str[:16].replace('T', ' ')
    except:
        return iso_str

############################
# 1. KUDAGO
############################

def fetch_kudago_events(city='ekb'):
    """
    Пример запроса к KudaGo: https://kudago.com/public-api/
    Параметры: v1.4/events?location=<city>
    Возвращает список слотов, у каждого:
      - 'source' = 'kudago'
      - 'event_id'
      - 'title'
      - 'date'
      - 'link'
      - 'short_desc'
    """
    url = f"https://kudago.com/public-api/v1.4/events/?location={city}&page_size=20"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[KudaGo] Ошибка: {response.status_code}")
        return []

    data = response.json()
    results = data.get('results', [])
    events = []

    for item in results:
        ev = parse_kudago_event(item)
        if ev:
            events.append(ev)

    return events

def parse_kudago_event(item):
    """
    Приводит KudaGo-данные к формату:
    {
      'source': 'kudago',
      'event_id': ...,
      'title': ...,
      'date': ...,
      'link': ...,
      'short_desc': ...
    }
    """
    event_id = str(item.get('id', ''))
    title = item.get('title', 'Без названия')
    short_desc = item.get('short_title') or title

    # Даты KudaGo часто в массиве item['dates']
    # Возьмём первую
    dates_info = item.get('dates', [])
    start_ts = None
    if dates_info:
        start_ts = dates_info[0].get('start')  # Unix timestamp
    date_str = timestamp_to_str(start_ts)

    link = item.get('site_url', '')

    return {
        'source': 'kudago',
        'event_id': event_id,
        'title': title,
        'date': date_str,
        'link': link,
        'short_desc': short_desc
    }

############################
# 2. TIMEPAD
############################

def fetch_timepad_events(city='Екатеринбург'):
    """
    Пример запроса к TimePad API:
    https://timepad.github.io/api-doc/
    cities=<русское название>
    """
    # Для Екатеринбурга: cities=Екатеринбург (URL-encoded)
    url = "https://api.timepad.ru/v1/events"
    params = {
        'limit': 20,
        'cities': city
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"[TimePad] Ошибка: {response.status_code}")
        return []

    data = response.json()
    results = data.get('values', [])
    events = []

    for item in results:
        ev = parse_timepad_event(item)
        if ev:
            events.append(ev)

    return events

def parse_timepad_event(item):
    """
    Приводит TimePad-данные к формату:
    {
      'source': 'timepad',
      'event_id': ...,
      'title': ...,
      'date': ...,
      'link': ...,
      'short_desc': ...
    }
    """
    event_id = str(item.get('id', ''))
    title = item.get('name', 'Без названия')
    date_str = iso_to_str(item.get('starts_at', ''))
    link = item.get('url', '')
    short_desc = item.get('description_short', '') or title

    return {
        'source': 'timepad',
        'event_id': event_id,
        'title': title,
        'date': date_str,
        'link': link,
        'short_desc': short_desc
    }

############################
# 3. EVENTBRITE
############################

def fetch_eventbrite_events(city='Ekaterinburg'):
    """
    Пример запроса к Eventbrite API: https://www.eventbrite.com/platform/api
    Обычно нужен API Token.

    city='Ekaterinburg' для поиска по названию города.
    """
    token = "<YOUR_EVENTBRITE_TOKEN>"
    url = "https://www.eventbriteapi.com/v3/events/search/"
    params = {
        'q': city,
        'token': token,
        'expand': 'venue'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"[Eventbrite] Ошибка: {response.status_code}")
        return []

    data = response.json()
    items = data.get('events', [])
    events = []

    for item in items:
        ev = parse_eventbrite_event(item)
        if ev:
            events.append(ev)
    return events

def parse_eventbrite_event(item):
    """
    Приводит Eventbrite-данные к формату:
    {
      'source': 'eventbrite',
      'event_id': ...,
      'title': ...,
      'date': ...,
      'link': ...,
      'short_desc': ...
    }
    """
    event_id = str(item.get('id', ''))
    title = item.get('name', {}).get('text', 'Без названия')
    starts_at = item.get('start', {}).get('local')
    date_str = iso_to_str(starts_at)
    link = item.get('url', '')
    short_desc = (item.get('description', {}) or {}).get('text', '')
    if not short_desc:
        short_desc = title

    return {
        'source': 'eventbrite',
        'event_id': event_id,
        'title': title,
        'date': date_str,
        'link': link,
        'short_desc': short_desc
    }

############################
# ОСНОВНОЙ СКРИПТ
############################

def main():
    # Инициализируем БД
    init_db('events.db')

    all_events = []

    # 1. KudaGo
    kudago_list = fetch_kudago_events('ekb')  # Екатеринбург
    all_events.extend(kudago_list)

    # 2. TimePad
    timepad_list = fetch_timepad_events('ekaterinburg')
    all_events.extend(timepad_list)

    # 3. Eventbrite
    eventbrite_list = fetch_eventbrite_events('Ekaterinburg')
    all_events.extend(eventbrite_list)

    # Сохраняем всё в БД
    save_events_to_db(all_events, 'events.db')

    print(f"Собрали всего событий: {len(all_events)}")

if __name__ == '__main__':
    main()