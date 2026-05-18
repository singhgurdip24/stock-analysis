import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes.stock_routes import router
from jobs.evaluate_predictions import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
