#!/bin/bash -xue
# Builds the Airflow Docker container

cd $(dirname $0)

docker build -t crawler-airflow:latest .