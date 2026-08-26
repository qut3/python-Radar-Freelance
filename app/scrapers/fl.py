# from playwright.async_api import async_playwright, TimeoutError as PLWtimeout | сайт не динамический
from bs4 import BeautifulSoup
import requests

import re
from fake_useragent import UserAgent

import time

us = UserAgent()

HEADERS = {
    "User-Agent": us, 
    "Accept-Language": "ru-RU,ru;q=0.9",
}

# ==================================================================================================
# ПАРСИМ ХТМЛ СТРАНИЦУ
# ====================================================================================================

def get_flru_html(url = 'https://www.fl.ru/projects/?kind=1') :

    """
    Возвращает хтмл страницу через requests , передается юрл
    """

    response = requests.get(url=url, headers=HEADERS)

    if response.status_code == 200: return response.text
    else: raise RuntimeError(f"NOT 200 STATUS: {response.status_code}")


# ==================================================================================================
# ОТДЕЛЬНАЯ СТРАНИЦА КАЖДОГО ТОВАРА + ПОЛНОЕ ОПИСАНИЕ
# ====================================================================================================

def get_order_page(url: str) :

    """
    Возвращает хтмл ОТДЕЛЬНОЙ СТРАНИЦЫ КАЖДОГО ТОВАРА !!!
    """

    response = requests.get(url=url, headers=HEADERS)

    if response.status_code == 200: return response.text
    else: raise RuntimeError(f"NOT 200 STATUS: {response.status_code}")


def extract_full_desc(html: str) :

    """
    Возвращает полное описание после перехода на отдельную страницу get_order_page
    """

    soup = BeautifulSoup(html, 'lxml')

    full_description = soup.select_one('.fl-project-content__description-text')

    return full_description.get_text(" ", strip=True) if full_description else ""

# ==================================================================================================
# БЕРЕМ ВСЮ ИНФОРМАЦИЮ
# ====================================================================================================

def extract_data(html: str) :

    """
    Возвращает всю доступную информацию
    1. Айди
    2. Название
    3. Юрл
    4. Цена
    5. Описание ( берет его из функции extract_full_desc() )
    """

    soup = BeautifulSoup(html, 'lxml')

    cards = soup.select("div[id^='project-item']")

    results = []

    for card in cards :

        # -- НАЗВАНИЕ -- 
        title_tag = card.select_one('h2.b-post__title a')
        project_id = title_tag.get('data-disposable-project-id')

        # -- ЮРЛ -- 
        href = title_tag.get('href')
        full_url = f'https://www.fl.ru{href}'

        # -- ЦЕНА -- 
        price_tag = card.select_one("div.b-post__price")
        price_text = price_tag.get_text(" ", strip=True) if price_tag else ""

        # -- ОПИСАНИЕ -- 
        html_order = get_order_page(full_url)
        full_description = extract_full_desc(html_order)

        results.append({
            "id": project_id,
            "platform": "fl.ru",
            "title": title_tag.get_text(strip=True),
            "url": full_url,
            "price": price_text,
            "description": full_description,
        })

    return results

# ==================================================================================================

FLRU_CATEGORIES = {
    "sites": "saity",
    "seo": "prodvizhenie-saitov-seo",
    "design": "dizajn",
    "marketing": "reklama-marketing",
    "programming": "programmirovanie",
    "ai": "ai-iskusstvenniy-intellekt",
    "writing": "teksty",
    "consulting": "konsalting",
    "illustration": "risunki-i-illustracii",
    "engineering": "inzhiniring",
    "audio_video_photo": "audio-video-photo",
    "3d": "3d-grafika",
    "mobile": "mobile",
    "messengers": "messengers",
    "branding": "firmennyi-stil",
    "animation": "animaciya",
    "automation": "avtomatizaciya-biznesa",
    "marketplace": "marketplace-management",
    "crypto": "crypto-i-blockchain",
    "games": "games",
    "social": "socialnye-seti",
    "browsers": "brauzery",
    "ecommerce": "internet-magaziny",
}

# ==================================================================================================
# СТРОИМ ЮРЛ
# ====================================================================================================

def build_flru_url(category: str | None, page: int = 1):
    if category:
        slug = FLRU_CATEGORIES.get(category)
        if not slug:
            raise ValueError(f'неизвестная категория {category}')
        base = f'https://www.fl.ru/projects/category/{slug}/'
    else:
        base = f'https://www.fl.ru/projects/'
    if page > 1:
        base += f'page-{page}/'
    base += '?kind=1/'

    return base

# ==================================================================================================
# ПАГИНАЦИЯ
# ====================================================================================================

def fetch_flru_paginated(category: str | None, limit: int) :

    max_cards_page = 30
    all_results = []
    page_num = 1

    while len(all_results) < limit : 

        url = build_flru_url(category=category, page=page_num)
        html = get_flru_html(url)

        page_results = extract_data(html)

        if not page_results: break

        all_results.extend(page_results)
        
        if len(page_results) < max_cards_page: break
        
        page_num += 1

        time.sleep(1)

    return all_results[:limit]

# ==================================================================================================

# projects = fetch_flru_paginated(category='design', limit=5)

# print(f"Найдено: {len(projects)}")
# for i, p in enumerate(projects, start=1):
#     print(f"[{i}] {p['title']} — {p['price']}")
#     print(f"    {p['url']}")
#     print("-" * 60)