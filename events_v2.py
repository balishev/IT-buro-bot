import requests
from datetime import datetime, timedelta

def get_events(city):
    url = "https://kudago.com/public-api/v1.4/events/"
    params = {
        "location": "Екатеринбург",
        "actual_since": 1696100000,  # Пример: 1 октября 2023 года
        "actual_until": 1698692000,  # Пример: 30 октября 2023 года
        "fields": "id,title,dates,place,description,price",
        "page_size": 100,
        "lang": "ru",
        "expand": "place"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return []

# Пример использования
city = "Екатеринбург"
events = get_events(city)
for event in events:
    print(event["title"], event["dates"][0]["start"])