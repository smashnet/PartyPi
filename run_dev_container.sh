#!/bin/bash

# Only create container if no container with this name is already there
if [ ! "$(docker ps -q -f name=partypi-docker-dev)" ]; then
  docker run --rm -d --name partypi-docker-dev -p 8081:8080 -v $(pwd):/usr/src/app -w /usr/src/app partypi-dev
fi

# Install node modules if they are not already there
if [ ! -d "node_modules" ]; then
  docker exec -ti partypi-docker-dev npm install
fi

# npm start
docker exec -ti partypi-docker-dev npm start
