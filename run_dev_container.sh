#!/bin/bash

docker run --rm -p 8081:8080 -v $(pwd):/usr/src/app -w /usr/src/app partypi-dev
