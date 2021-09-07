import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.tracker import TrackerService
import dataaccess.session as database_session
from dataaccess import leaderboard

# Initialize Tracker Service
tracker_service = TrackerService()

# Setup FastAPI app
app = FastAPI(
    title="API Server",
    description="API Server",
    version="v1"
)

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Startup tasks
    # Connect to database
    await database_session.connect()
    # Start the tracker service
    asyncio.create_task(tracker_service.track())


@app.on_event("shutdown")
async def shutdown():
    # Shutdown tasks
    # Disconnect from database
    await database_session.disconnect()

# Routes


@app.get("/")
async def get_index():
    return {
        "message": "Welcome to the API Service"
    }


@app.get("/leaderboard")
async def get_leaderboard():
    return await leaderboard.browse()
