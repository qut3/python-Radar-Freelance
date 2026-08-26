from playwright.async_api import async_playwright, TimeoutError as PLWtimeout
from bs4 import BeautifulSoup
import re

import asyncio

from fake_useragent import UserAgent

# ==================================================================================================
# ПОЛУЧЕНИЕ ХТМЛ СТРАНИЦЫ
# ====================================================================================================

async def get_kwork_html(url) :

    """
    Получем целиком хтмл код с подгруженным JavaScript контентом. В контекст передаем хэдерс из
    from fake_useragent import UserAgent
    """

    async with async_playwright() as plw:
        browser = await plw.chromium.launch(headless=False)
        us = UserAgent()
        context = await browser.new_context(user_agent=us.chrome)

        page = await context.new_page()

        await page.goto(url, wait_until='networkidle')

        html = await page.content()

        await browser.close()
        return html

# ==================================================================================================
# БЕРЕМ ПОЛНОЕ ОПИСАНИЕ
# ====================================================================================================

def extract_description(card) :

    """
    Получаем описание. Если "none" есть в стилях, то значит оно длинное и показываем полную версию,
    если нет - то оно короткое и показываем также версию доступную.
    """

    container = card.select_one("div.wants-card__description-text")

    hidden_div = container.find("div", style=lambda s: s and "none" in s)

    if hidden_div: text = hidden_div.get_text(" ", strip=True)
    else: text = container.get_text(" ", strip=True)

    return text.replace("Показать полностью", "").replace("Скрыть", "").strip()

# ==================================================================================================
# ДОСТАЕМ ВСЮ ИНФОРМАЦИЮ
# ====================================================================================================

def extract_data(html: str) :

    """
    Берет хтмл код страницы из get_kwork_html() и возвращает данные:
    1. Айди
    2. Название
    3. Юрл
    4. Цена
    4. Покупатель
    5. Описание ( берет его из функции extract_description() )
    """

    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_='want-card')

    results = []
    for card in cards:
        title_tag = card.select_one("h1.wants-card__header-title a")
        if not title_tag: continue

        href = title_tag.get("href", "")
        id_match = re.search(r"/projects/(\d+)", href)

        desc_text = extract_description(card)

        price_tag = card.select_one("div.wants-card__price")
        price_text = price_tag.get_text(" ", strip=True) if price_tag else ""

        buyer_tag = card.select_one("div.want-card__statistic-item a")
        buyer_name = buyer_tag.get_text(strip=True) if buyer_tag else ""

        results.append({
            "id": id_match.group(1) if id_match else None,
            "title": title_tag.get_text(strip=True),
            "url": f"https://kwork.ru{href}" if href.startswith("/") else href,
            "price": price_text,
            "buyer": buyer_name,
            "description": desc_text,
        })

    return results

# ==================================================================================================
# СТРОИМ ЮРЛ
# ====================================================================================================

def build_kwork_url(category: int | None) :
    """
    Делает фильтрацию по категориям. Передаем туда целое число
    """

    if category: return f'https://kwork.ru/projects?c={category}'
    else: return f'https://kwork.ru/projects?c=all'

# ==================================================================================================
# ДЕЛАЕМ ПАГИНАЦИЮ
# ====================================================================================================

async def fetch_kwork_paginated(category: str | None, limit: int) :
    max_cards_page = 12
    all_results = []
    page_num = 1

    base = build_kwork_url(category)
    separator = '&' if '?' in base else '?'

    while len(all_results) < limit :

        url = f'{base}{separator}page={page_num}'
        page = await get_kwork_html(url)

        page_results = extract_data(page)

        if not page_results: break

        all_results.extend(page_results)

        if len(page_results) < max_cards_page: break

        page_num += 1
        await asyncio.sleep(5)

    return all_results[:limit]


# ==================================================================================================

KWORK_CATEGORIES = {
    "design": 15,
    "programming": 11,
    "writing": 5,
    "seo": 17,
    "marketing": 45,
    "audio_video": 7,
    "business": 83,
}

# async def main():
#     projects = await fetch_kwork_paginated(category='15', limit=30)
#     print(f"Найдено: {len(projects)}")
#     for i, p in enumerate(projects, start=1):
#         print(f"[{i}] {p['title']} — {p['price']}")
#         print(f"    {p['url']}")
#         print("-" * 60)

# if __name__ == '__main__' :
#     asyncio.run(main())








