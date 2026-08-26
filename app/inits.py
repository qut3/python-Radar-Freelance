from fastapi import FastAPI

from app.api.routes import router

def include_r(app: FastAPI):

    app.include_router(router)

