import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import router
from api.auth_routes import router as auth_router
from services.kafka_consumer import KafkaConsumerService
from services.database import DatabaseService
from services.auth import UserService
from config import config

# Global services
kafka_consumer_service = None
db_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global kafka_consumer_service, db_service
    
    print("🚀 Starting ARCS Backend...")
    
    # Initialize database
    db_service = DatabaseService()
    app.state.db = db_service
    
    # Initialize user service and create default admin
    user_service = UserService(db_service)
    app.state.user_service = user_service
    
    # Initialize and start Kafka consumer
    kafka_consumer_service = KafkaConsumerService(db_service)
    consumer_task = asyncio.create_task(kafka_consumer_service.start())
    
    print("✅ ARCS Backend started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down ARCS Backend...")
    if kafka_consumer_service:
        await kafka_consumer_service.stop()
    consumer_task.cancel()
    print("✅ ARCS Backend stopped")

app = FastAPI(
    title="ARCS API",
    description="AI-Driven Autonomous Ransomware Detection and Containment System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "service": "ARCS Backend",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
