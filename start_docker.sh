#!/bin/bash

docker run -it --rm --network server_network  -v $(pwd)/config:/app/config --name home_lab_expose jairf/home_lab_expose:latest

