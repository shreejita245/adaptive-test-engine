from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import questions, students, attempts, analytics, sessions, insights

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://adaptive-test-engine.vercel.app",
        "https://adaptive-test-engine-git-main.vercel.app",
    ],
    allow_origin_regex=r"https://adaptive-test-engine.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(students.router)
app.include_router(attempts.router)
app.include_router(analytics.router)
app.include_router(sessions.router)
app.include_router(insights.router)

@app.get("/")
def root():
    return {"message": "Adaptive Test Engine running"}