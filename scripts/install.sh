#!/bin/bash
docker stop garage && docker rm garage
docker run --dns 8.8.8.8 --dns 8.8.4.4 --name garage --restart=always -p 8088:8088 -d garage
