# python-Radar-Freelance
Radar freelance (kwork, fl.ru, profi.ru)

stack: FastAPI (async + sync), Playwright, requests, sqlite3, sqlalchemy.

Анализирует три биржи (кворк, фл.ру, профи ( профи парсер сделан, не доделана ручка ) ), отправляет джсон всей информации о заказе
ллмка получает джсон и анализирует ее согласно вашим навыкам

Навыки пишите в SYSTEM_PROMPTS ( app/llm/prompts ) в конец добавляете
"ФОРМАТИРУЙ ЗАКАЗЫ СОГЛАСНО НАВЫКАМ ПОЛЬЗОВАТЕЛЯ = []" (в скобках пишите ваши навыки)

для запуска:
uv app.main:app 
переходите на локальных хост и запускаете ручку analyze

СДЕЛАН НА ОСНОВЕ ( вдохновился ) - https://freelance-radar.com/
