"""Пример обращения к GigaChat с помощью GigaChain"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from dotenv import load_dotenv
import os


def gigachat_translate(text: str, target_language: str = "ru") -> str:
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
            content=f"Ты бот-переводчик, переведи текст на язык {target_language}:"
        )
    ]

    messages.append(HumanMessage(content=text))
    res = model.invoke(messages)
    messages.append(res)
    return res.content


user_input = input()
print(gigachat_translate(user_input))
