#!/bin/sh

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume ls | awk '{print$2}' | xargs docker volume rm || echo "Containers not found"
docker images -a | awk '{print$3}' | xargs docker rmi || echo "Images not found"
docker volume prune -f
docker-compose up --build -d --remove-orphans --force-recreate
