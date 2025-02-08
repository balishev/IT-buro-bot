# states.py

from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    language = State()           # Выбор языка
    account_login = State()      # Ввод логина
    account_password = State()   # Ввод пароля
    city = State()               # Ввод города
    university = State()         # Выбор вуза

class AdditionalInfo(StatesGroup):
    activity = State()      # Оценка, насколько активный (выбор от 1 до 5)
    sociability = State()   # Оценка, насколько общительный (выбор от 1 до 5)
    interests = State()     # Текстовый ввод: что вам нравится

class EditingSchedule(StatesGroup):
    new_event = State()     # Ожидание ввода нового события
