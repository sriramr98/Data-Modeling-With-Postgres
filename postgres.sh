#!/bin/bash

# This script helps you setup postgres locally using docker
# Make sure to setup docker before running the script

docker pull postgres

# Data folder for postgres
DATA_PATH='$HOME/postgres-data/'
if [! -d $DATA_PATH] then mkdir -p ${HOME}/postgres-data/ fi;

docker run -d --name dev-postgres -e POSTGRES_PASSWORD=student -v ${HOME}/postgres-data/:/var/lib/postgresql/data -p 5432:5432 postgres