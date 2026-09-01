from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions import AppError
from routers import router

app = FastAPI()

app.include_router(router)

@app.exception_handler(AppError)
def tournament_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

@app.get("/", tags=["System"])
def root():
    return {"message": "Tournament Manager API", "docs": "/docs"}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}