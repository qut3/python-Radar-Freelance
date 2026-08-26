from fastapi import FastAPI, APIRouter
from fastapi.concurrency import run_in_threadpool

from app.scrapers.fl import fetch_flru_paginated
from app.scrapers.kwork import fetch_kwork_paginated
from app.scrapers.profi import extract_profi_data

from app.database.dedup import filter_new
from app.database.db import SessionDep
from app.llm.api_llm import analyze
import json

router = APIRouter()

# =====================================================================================================
# ЭНДПОИНТ КВОРК
# =====================================================================================================

@router.post('/scrape/kwork')
async def kwork_analyze(category: str | None, limit: int, db: SessionDep ) :
    """
    Анализ кворка
    """

    projects = await fetch_kwork_paginated(category=category, limit=limit)

    new_projects = await run_in_threadpool(filter_new, projects, 'kwork.ru', db)

    if not new_projects:
        return {"found": 0, "items": []}

    projects_json = json.dumps(new_projects, ensure_ascii=False)
    analysis = await run_in_threadpool(analyze, projects_json)

    return {"found": len(new_projects), "items": analysis}

# =====================================================================================================
# ЭНДПОИНТ ФЛРУ
# =====================================================================================================

@router.post("/scrape/flru")
async def flru_analyze(category: str | None, limit: int, db: SessionDep):
    """
    Анализ флру
    """

    projects = await run_in_threadpool(fetch_flru_paginated, category, limit)

    new_projects = await run_in_threadpool(filter_new, projects, "fl.ru", db)

    if not new_projects:
        return {"found": 0, "items": []}

    projects_json = json.dumps(new_projects, ensure_ascii=False)
    analysis = await run_in_threadpool(analyze, projects_json)

    return {"found": len(new_projects), "items": analysis}

# =====================================================================================================
# ЭНДПОИНТ ПРОФИРУ
# =====================================================================================================

pass