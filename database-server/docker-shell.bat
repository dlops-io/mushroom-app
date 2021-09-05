# Create the network if we don't have it yet
# sources: https://dockerlabs.collabnix.com/networking/A1-network-basics.html#docker_network; in terminal, run "docker network inspect"
# The docker network command is the main command for configuring and managing container networks.
# what this is saying here is to inspect the network (Display detailed information on one or more networks) if the network exists; if it does not exist, then create the network
docker network inspect mushroomappnetwork >NUL || docker network create mushroomappnetwork

# Run Postgres DB and DBMate
# sources: https://dockerlabs.collabnix.com/intermediate/workshop/; in Terminal, run "docker-compose run"; https://dockerlabs.collabnix.com/intermediate/workshop/DockerCompose/Difference_between_dockerfile_and_docker_compose.html
# Docker compose is a tool built by docker to ease the task of creating and configuring multiple containers in a development environment; the counter-part of docker-compose for production environments is docker-swarm. Docker compose takes as input a YAML configuration file (docker-compose.yml) and creates the resources (containers, networks, volumes etc.) by communicating with the docker daemon through docker api.
# A Dockerfile is a text document that contains all the commands/Instruction a user could call on the command line to assemble an image. On the other hand, Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration. By default, docker-compose expects the name of the Compose file as docker-compose.yml or docker-compose.yaml. If the compose file have different name we can specify it with -f flag.

# "docker-compose run" means to Run a one-off command on a service
# "--rm" means to Remove container after run. Ignored in detached mode.
# "--service-ports" means to Run command with the service's ports enabled and mapped to the host
docker-compose run --rm --service-ports --name database-client mushroomappdb-client