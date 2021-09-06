
import os
import asyncio
from glob import glob
import json
import pandas as pd

import tensorflow as tf
from google.cloud import storage

from dataaccess.session import database

gcp_project = os.environ["GCP_PROJECT"]
bucket_name = "ai5-mushroom-app-models"
local_experiments_path = "/persistent/experiments"

# Setup experiments folder
if not os.path.exists(local_experiments_path):
    os.mkdir(local_experiments_path)


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    storage_client = storage.Client(project=gcp_project)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def download_experiment_metrics():
    # Get all model metrics
    models_metrics_list = tf.io.gfile.glob(
        "gs://ai5-mushroom-app-models/*/*/*_model_metrics.json")

    timestamp = 0

    for metrics_file in models_metrics_list:
        path_splits = metrics_file.split("/")
        user_email = path_splits[3]
        experiment = path_splits[4]
        local_metrics_file = path_splits[-1]

        local_metrics_file = os.path.join(
            local_experiments_path, user_email, experiment, local_metrics_file)

        if not os.path.exists(local_metrics_file):
            print("Copying:", metrics_file, local_metrics_file)

            # Ensure user directory exists
            os.makedirs(os.path.join(
                local_experiments_path, user_email), exist_ok=True)
            os.makedirs(os.path.join(
                local_experiments_path, user_email, experiment), exist_ok=True)

            metrics_file = metrics_file.replace(
                "gs://ai5-mushroom-app-models/", "")
            # Download the metric json file
            download_blob(bucket_name, metrics_file,
                          local_metrics_file)

            file_timestamp = os.path.getmtime(local_metrics_file)
            if file_timestamp > timestamp:
                timestamp = file_timestamp

    return timestamp


def agg_experiments():
    print("Aggregate all experiments across users")

    # Get Experiments accross users
    models_metrics_list = glob(
        local_experiments_path+"/*/*/*_model_metrics.json")

    all_models_metrics = []
    for mm_file in models_metrics_list:
        path_splits = mm_file.split("/")

        with open(mm_file) as json_file:
            model_metrics = json.load(json_file)
            model_metrics["user"] = path_splits[-3]
            model_metrics["experiment"] = path_splits[-2]
            model_metrics["model_name"] = path_splits[-1].replace(
                "_model_metrics.json", "")
            all_models_metrics.append(model_metrics)

    # Convert to dataframe and save as csv
    df = pd.DataFrame(all_models_metrics)
    df.to_csv(local_experiments_path+"/all_models_metrics.csv", index=False)


def compute_leaderboard():
    print("Compute Leaderboard and find best model")
    df = pd.read_csv(local_experiments_path+"/all_models_metrics.csv")
    print("Shape:", df.shape)
    print(df.head())

    # Group by users
    # Find best model for user (by accuracy)
    leaderboard = df.sort_values(
        by=['accuracy'], ascending=False).groupby('user').head(1).reset_index(drop=True)
    print("Shape:", leaderboard.shape)
    print(leaderboard.head())

    # Save a csv with leaderboard.csv
    leaderboard.to_csv(local_experiments_path+"/leaderboard.csv", index=False)

    # Find the overall best model across users
    best_model = leaderboard.iloc[0].to_dict()
    # Create a json file best_model.json
    with open(os.path.join(local_experiments_path, "best_model.json"), "w") as json_file:
        json_file.write(json.dumps(best_model))


def download_best_models():
    print("Download leaderboard models and artifacts")
    try:

        df = pd.read_csv(local_experiments_path+"/leaderboard.csv")
        print("Shape:", df.shape)
        print(df.head())

        for index, row in df.iterrows():
            print(row["user"], row["experiment"], row["model_name"])

            download_file = os.path.join(
                row["user"], row["experiment"], row["model_name"]+".hdf5")
            download_blob(bucket_name, download_file,
                          os.path.join(local_experiments_path, download_file))

            download_file = os.path.join(
                row["user"], row["experiment"], row["model_name"]+"_train_history.json")
            download_blob(bucket_name, download_file,
                          os.path.join(local_experiments_path, download_file))

            # Data details
            download_file = os.path.join(
                row["user"], row["experiment"], "data_details.json")
            download_blob(bucket_name, download_file,
                          os.path.join(local_experiments_path, download_file))
    except:
        print("Error in download_best_models")


async def save_leaderboard_db():
    # read leaderboard
    df = pd.read_csv(local_experiments_path+"/leaderboard.csv")
    print("Shape:", df.shape)
    print(df.head())

    # Delete current data in table
    query = "delete from leaderboard;"
    print("query:", query)
    await database.execute(query)

    # Insert rows
    query = f"""
        INSERT INTO leaderboard (
                trainable_parameters ,
                execution_time ,
                loss ,
                accuracy ,
                model_size ,
                learning_rate ,
                batch_size ,
                epochs ,
                optimizer ,
                email ,
                experiment ,
                model_name 
            ) VALUES (
                :trainable_parameters ,
                :execution_time ,
                :loss ,
                :accuracy ,
                :model_size ,
                :learning_rate ,
                :batch_size ,
                :epochs ,
                :optimizer ,
                :email ,
                :experiment ,
                :model_name 
            );
       """
    for index, row in df.iterrows():
        await database.execute(query, {
            "trainable_parameters": row["trainable_parameters"],
            "execution_time": row["execution_time"],
            "loss": row["loss"],
            "accuracy": row["accuracy"],
            "model_size": row["model_size"],
            "learning_rate": row["learning_rate"],
            "batch_size": row["batch_size"],
            "epochs": row["epochs"],
            "optimizer": row["optimizer"],
            "email": row["user"],
            "experiment": row["experiment"],
            "model_name": row["model_name"]
        })


class TrackerService:
    def __init__(self):
        self.timestamp = 0

    async def track(self):
        while True:
            await asyncio.sleep(60)
            print("Tracking experiments...")

            # Download new model metrics
            timestamp = download_experiment_metrics()

            if timestamp > self.timestamp:
                # Aggregate all experiments across users
                agg_experiments()

                # Compute Leaderboard and find best model
                compute_leaderboard()

                # Saving leaderboard
                await save_leaderboard_db()

                # Set the timestamp of the last file processed
                self.timestamp = timestamp

                # Download leaderboard models and artifacts
                download_best_models()
