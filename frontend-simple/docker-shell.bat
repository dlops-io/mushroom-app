REM Define some environment variables
SET IMAGE_NAME=frontend-app
SET BASE_DIR=%cd%

REM Build the image based on the Dockerfile
docker build -t %IMAGE_NAME% -f Dockerfile .

REM Run the container
REM --mount: Attach a filesystem mount to the container
REM -p: Publish a container's port(s) to the host (host_port: container_port) (source: https://dockerlabs.collabnix.com/intermediate/networking/ExposingContainerPort.html)
docker run  --rm --name %IMAGE_NAME% -ti --mount type=bind,source="%cd%",target=/app -p 8080:8080 %IMAGE_NAME%