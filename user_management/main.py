from fastapi import FastAPI
from database import engine, Base
from routers.users import router as users_router

# creates all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="0.2.0")

app.include_router(users_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
