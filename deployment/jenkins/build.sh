#!/bin/bash

virtualenv env
source ./env/bin/activate
pip install -r requirements-pip.txt -b pip_build

make build
make run_locally && sleep 10
make unit-test || exit 1
make integration-test || exit 1
make test || exit 1
make stop

deactivate
