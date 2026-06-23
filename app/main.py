import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import connect_db, disconnect_db, db
from app.routers import admin, auth, challenges, scoreboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


app = FastAPI(title="Operation: IronCurtain", lifespan=lifespan)

origins = [
    "http://localhost:3000",                       # React/Next.js local development
    "http://127.0.0.1:5173",                       # Vite local development
    "http://localhost:8080",                       # Nginx Reverse Proxy if using dockerized frontend
    "https://ironcurtain.sabihinmolang.eu.org",    # Production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allowed domains
    allow_credentials=True,         # Allow cookies and auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all request headers
)

os.makedirs("uploads/questions", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(challenges.router)
app.include_router(scoreboard.router)


@app.get("/health")
async def health_check():
    try:
        await db.query_raw("SELECT 1")
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
    return {"status": "ok"}
