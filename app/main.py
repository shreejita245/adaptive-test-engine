from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import questions, students, attempts, analytics, sessions

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(students.router)
app.include_router(attempts.router)
app.include_router(analytics.router)
app.include_router(sessions.router)

@app.get("/")
def root():
    return {"message": "Adaptive Test Engine running"}