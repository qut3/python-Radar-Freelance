import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# ===================================================================================================

from fastapi import FastAPI

from app.database.db import init_db
from app.inits import include_r

app = FastAPI()

init_db()
include_r(app=app)

