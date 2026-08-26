# from playwright.async_api import async_playwright  
# from pathlib import Path

# import asyncio

# SESSION_FILE = Path(__file__).parent / "profi_session.json"
# LOGIN_URL = "https://profi.ru/backoffice/"

# async def login_and_save_session() :

#     async with async_playwright() as plw :
#         browser = await plw.chromium.launch(headless=False)

#         context = await browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
#             viewport={"width": 1280, "height": 900},
#             locale="ru-RU",
#         )
#         page = await context.new_page()

#         await page.goto(LOGIN_URL, wait_until='domcontentloaded')

#         print("Открылось окно браузера.")
#         print("Войдите вручную: телефон/логин, пароль или SMS-код — как обычно.")
#         print("Дождитесь полной загрузки личного кабинета (список заказов/дашборд).")
#         input("Когда точно залогинены — нажмите Enter здесь в консоли...")

#         await context.storage_state(path=SESSION_FILE)
#         print(f"Сессия сохранена в {SESSION_FILE}")

#         await browser.close()

# ==================================================================================================


# ==================================================================================================

# async def debug_profi():
#     html = await get_profi_html("https://profi.ru/backoffice/n.php")

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import asyncio
import re

# ==================================================================================================
# НАСТРОЙКИ
# ==================================================================================================

SESSION_FILE = Path(__file__).parent / "profi_session.json"
LOGIN_URL = "https://profi.ru/backoffice/"
ORDERS_URL = "https://profi.ru/backoffice/n.php"

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


# ==================================================================================================
# ЛОГИН
# ==================================================================================================

async def login_and_save_session():
    async with async_playwright() as plw:
        browser = await plw.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 900},
            locale="ru-RU",
        )
        page = await context.new_page()
        await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

        print("Войдите вручную в открывшемся окне.")
        input("Когда залогинены — нажмите Enter здесь...")

        await context.storage_state(path=str(SESSION_FILE))
        print(f"Сессия сохранена в {SESSION_FILE}")

        await browser.close()


# ==================================================================================================
# ПОЛУЧЕНИЕ HTML
# ==================================================================================================

async def get_profi_html(url: str) -> str:
    if not SESSION_FILE.exists():
        raise RuntimeError("Сессия не найдена — сначала запустите login_and_save_session()")

    async with async_playwright() as plw:
        browser = await plw.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=str(SESSION_FILE),
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 900},
            locale="ru-RU",
        )
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        html = await page.content()
        current_url = page.url

        await browser.close()

    if "backoffice/n.php" not in current_url:
        raise RuntimeError(
            f"Похоже, сессия истекла — попали на {current_url}. "
            "Запустите login_and_save_session() заново."
        )

    return html


# ==================================================================================================
# ПАРСИНГ (синхронный)
# ==================================================================================================

def find_order_cards(soup: BeautifulSoup):
    return soup.find_all("a", attrs={"data-testid": re.compile(r'^\d+_order[-_]snippet$')})


def clean_description(text: str) -> str:
    return re.split(r'\s*context=', text)[0].strip()


def extract_profi_card(card) -> dict:
    order_id = card.get("id")
    href = card.get("href", "")
    full_url = f"https://profi.ru{href}" if href.startswith("/") else href

    h3_tag = card.select_one("h3")
    title = h3_tag.get_text(strip=True) if h3_tag else (card.get("aria-label") or "")

    desc_tag = card.select_one("p")
    desc_text = clean_description(desc_tag.get_text(" ", strip=True)) if desc_tag else ""

    price_wrap = card.select_one("span[aria-hidden='true']")
    price_text = price_wrap.get_text(" ", strip=True) if price_wrap else ""

    tags = []
    tags_list = card.select_one("ul[role='list']")
    if tags_list:
        for li in tags_list.select("li"):
            label = li.get("aria-label", "").rstrip(":")
            value = li.get_text(" ", strip=True)
            tags.append({"label": label, "value": value})

    author_tag = card.select_one("div.sc-fwxbQo span")
    author = author_tag.get_text(strip=True) if author_tag else ""

    return {
        "id": order_id,
        "platform": "profi.ru",
        "title": title,
        "url": full_url,
        "price": price_text,
        "description": desc_text,
        "tags": tags,
        "author": author,
    }


def extract_profi_data(html: str, limit: int = 10) -> list[dict]:
    soup = BeautifulSoup(html, 'lxml')
    cards = find_order_cards(soup)[:limit]
    return [extract_profi_card(c) for c in cards]



        

