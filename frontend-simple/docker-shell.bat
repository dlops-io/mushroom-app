SET IMAGE_NAME=mushroom-app-frontend-simple
SET BASE_DIR=%cd%

docker build -t %IMAGE_NAME% -f Dockerfile .
docker run  --rm --name %IMAGE_NAME% -ti --mount type=bind,source="%cd%",target=/app -p 8080:8080 %IMAGE_NAME%