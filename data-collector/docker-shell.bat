REM Define some environment variables
SET IMAGE_NAME="mushroom-app-data-collector"
SET GCP_PROJECT="ai5-project"
SET GCP_ZONE="us-central1-a"
REM Build the image based on the Dockerfile
docker build -t %IMAGE_NAME% -f Dockerfile .

REM Run the container
cd ..
docker run  --rm --name %IMAGE_NAME% -ti ^
            --mount type=bind,source="%cd%\data-collector",target=/app ^
            --mount type=bind,source="%cd%\persistent-folder",target=/persistent ^
            --mount type=bind,source="%cd%\secrets",target=/secrets^
            -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/bucket-reader.json" ^
            -e GCP_PROJECT="%GCP_PROJECT%" ^
            -e GCP_ZONE="%GCP_ZONE%" ^ %IMAGE_NAME% 
