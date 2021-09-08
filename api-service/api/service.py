import os
import asyncio
from fastapi import FastAPI, File
from starlette.middleware.cors import CORSMiddleware

from api.tracker import TrackerService
import dataaccess.session as database_session
from dataaccess import leaderboard

from tempfile import TemporaryDirectory
from api import model

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


@app.get("/best_model")
async def get_best_model():
    model.check_model_change()
    if model.best_model is None:
        return {"message": 'No model available to serve'}
    else:
        return {
            "message": 'Current model being served:'+model.best_model["model_name"],
            "model_details": model.best_model
        }


@app.post("/predict")
async def predict(
        file: bytes = File(...)
):
    print("predict file:", len(file), type(file))

    # Save the image
    with TemporaryDirectory() as image_dir:
        image_path = os.path.join(image_dir, "test.png")
        with open(image_path, "wb") as output:
            output.write(file)

        # Make prediction
        prediction_results = model.make_prediction(image_path)

    return prediction_results
