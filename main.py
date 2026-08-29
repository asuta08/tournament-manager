from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions import TournamentError
from routers import router

app = FastAPI()

app.include_router(router)

@app.exception_handler(TournamentError)
def tournament_error_handler(request: Request, exc: TournamentError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

@app.get("/")
def root():
    return {"message": "Tournament Manager API", "docs": "/docs"}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}