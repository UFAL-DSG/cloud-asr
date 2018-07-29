#!/bin/bash

mkdir -p /model

cd /model
[ ! -f model.zip ] && [ "$MODEL_URL" != "" ] && wget "${MODEL_URL}" -O model.zip
[ -f model.zip ] && unzip -n model.zip

# Backward compatibility with old models
find . -name "*cmvn*" | xargs -I {} sed -i "s/--norm-mean=/--norm-means=/" {}
