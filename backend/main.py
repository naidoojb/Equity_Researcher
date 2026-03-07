import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import stock, signals, news, technicals, fundamentals, research, competitors, search

app = FastAPI(
    title="Equity Researcher API",
    description="AI-powered equity research with real-time signals",
    version="1.0.0",
)

# CORS — allow Expo web dev server, localhost, and production domains
cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8081,http://localhost:19006,http://localhost:3000,https://tiiny.host",
)
cors_origins = [o.strip() for o in cors_origins_raw.split(",")]

# allow_origin_regex handles wildcard subdomains (e.g. https://abc123.tiiny.host)
# allow_origins only does exact matching, so subdomains must go here
cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://[^.]+\.tiiny\.host")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(stock.router, prefix="/api/stock", tags=["stock"])
app.include_router(signals.router, prefix="/api/stock", tags=["signals"])
app.include_router(news.router, prefix="/api/stock", tags=["news"])
app.include_router(technicals.router, prefix="/api/stock", tags=["technicals"])
app.include_router(fundamentals.router, prefix="/api/stock", tags=["fundamentals"])
app.include_router(research.router, prefix="/api/stock", tags=["research"])
app.include_router(competitors.router, prefix="/api/stock", tags=["competitors"])


@app.get("/health")
async def health():
    return {"status": "ok"}
