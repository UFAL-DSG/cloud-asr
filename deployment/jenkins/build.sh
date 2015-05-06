#!/bin/bash

virtualenv env
source ./env/bin/activate
pip install -r requirements-pip.txt -b pip_build

make build || exit 1
make unit-test || exit 1
make integration-test || exit 1
make run && echo "Waiting for platform to start" && sleep 90
make test || { make stop; exit 1; }
make stop


deactivate
