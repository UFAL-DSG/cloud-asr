#!/bin/bash

mkdir -p /model

cd /model
wget "${MODEL_URL}" -O model.zip
unzip model.zip
