from fastapi import FastAPI, Request
from database import engine, Base
from routers.users import router as users_router
from routers.auth import router as auth_router
from fastapi.responses import JSONResponse
from utils.logger import logger

# creates all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="0.2.0")

app.include_router(users_router)
app.include_router(auth_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    logger.warning(f"404 on {request.url}")
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.get("/health")
def health_check():
    return {"status": "ok"}
