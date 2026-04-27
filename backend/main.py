import asyncio
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth_routes import router as auth_router
from api.reports_routes import router as reports_router
from api.routes import router
from api.settings_routes import router as settings_router
from api.users_routes import router as users_router
from services.auth import UserService
from services.database import DatabaseService
from services.kafka_consumer import KafkaConsumerService

# Global services
kafka_consumer_service = None
db_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_consumer_service, db_service

    print("Starting ARCS Backend...")

    db_service = DatabaseService()
    app.state.db = db_service

    user_service = UserService(db_service)
    app.state.user_service = user_service

    kafka_consumer_service = KafkaConsumerService(db_service)
    consumer_task = asyncio.create_task(kafka_consumer_service.start())

    print("ARCS Backend started successfully")

    yield

    print("Shutting down ARCS Backend...")
    if kafka_consumer_service:
        await kafka_consumer_service.stop()
    consumer_task.cancel()
    print("ARCS Backend stopped")


app = FastAPI(
    title="ARCS API",
    description="AI-Driven Autonomous Ransomware Detection and Containment System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(users_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "ARCS Backend",
        "status": "running",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
