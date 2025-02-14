import requests
import feedparser

from configs import YAPI, API_KEY

# YandexGPT API URL
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# Функция для генерации текста с помощью YandexGPT

async def generate_summary(prompt, max_length=300):
    try:
        payload = {
            "modelUri": YAPI,
            "completionOptions": {
                "stream": False,
                "temperature": 0.5,
                "maxTokens": max_length
            },
            "messages": [
                {"role": "system", "text": "Ты — помощник, который создает краткие выжимки новостей. Вот категории новостей, с которыми тебе придется работать: В мире 🌍, Политика 🏛️, Экономика 💰, Видеоигры 🎮, Спорт 🏀, Кухня/Готовка 🍳 ,Животные 🐾, Природа 🌳, Технологии 💻, Техника ⚙️, Музыка 🎵, Образование 📚, Кино/Фильмы 🎬, Искусство 🎨, Наука 🔬, Автомобили 🚗, Экология 🌿, Мода 👗"},
                {"role": "user", "text": prompt}
            ]
        }
        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(YANDEXGPT_API_URL, json=payload, headers=headers)
        result = response.json()
        if "result" in result:
            return result["result"]["alternatives"][0]["message"]["text"].strip()
        else:
            return "Не удалось создать выжимку."
    except Exception as e:
        print(f"Ошибка при запросе к YandexGPT: {e}")
        return "Не удалось создать выжимку."

# Функции для парсинга RSS-лент

async def get_lenta_news():
    url = "https://lenta.ru/rss"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:8]:
        news_list.append({"title": entry.title, "link": entry.link, "source": "Lenta.ru"})
    return news_list

async def get_rbc_news():
    url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:8]:
        news_list.append({"title": entry.title, "link": entry.link, "source": "РБК"})
    return news_list

async def get_gazeta_news():
    url = "https://www.gazeta.ru/export/rss/lenta.xml"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:8]:
        news_list.append({"title": entry.title, "link": entry.link, "source": "Газета.Ru"})
    return news_list

async def get_kommersant_news():
    url = "https://www.kommersant.ru/RSS/news.xml"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:8]:
        news_list.append({"title": entry.title, "link": entry.link, "source": "Коммерсантъ"})
    return news_list

async def get_all_news():
    news_list = []
    news_list.extend(await get_lenta_news())
    news_list.extend(await get_rbc_news())
    news_list.extend(await get_gazeta_news())
    news_list.extend(await get_kommersant_news())
    return news_list


