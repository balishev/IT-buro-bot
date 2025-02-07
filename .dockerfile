# Используем официальный образ Python 3.10
FROM python:3.10

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем файлы вашего проекта в контейнер
COPY . /app

# Установим необходимые зависимости
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# По желанию, если у вас есть отдельный скрипт для загрузки/инициализации чего-то — можно выполнить здесь

# Запускаем ваш main.py
CMD ["python", "main.py"]
