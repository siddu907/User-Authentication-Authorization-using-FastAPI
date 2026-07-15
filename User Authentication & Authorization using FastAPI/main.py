from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from slowapi.errors import RateLimitExceeded

from database import Base, engine
from rate_limiter import limiter
from routers import auth, admin, task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API",description="""
## Task Manager API 

This API allows users to manage their daily tasks...

Thank you for using it and have a nice day from Stackly India

""", version="1.0.0")
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(exc), status_code=429)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(task.router)