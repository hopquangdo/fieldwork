"""Generic HTTP interface — runs any registered feature. ``pip install "graphrun[api]"``.

See ``graphrun.api.routes`` for the endpoint definitions.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graphrun.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="graphrun", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(router)
    return app


app = create_app()
