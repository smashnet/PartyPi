#!/bin/bash

sudo docker run --rm --network=host -v $(pwd):/usr/src/app -w /usr/src/app partypi-dev
