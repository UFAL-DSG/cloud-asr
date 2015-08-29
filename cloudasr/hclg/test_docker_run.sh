#!/bin/bash

./download_model.sh
models_dir=/app/data/models
out_dir_local=test_output
out_dir=/app/data/output
pwd=`pwd`

mkdir $out_dir
echo; echo Running docker; echo
id=$(docker run -v "$pwd":/app/cloud-asr-hclg -v $out_dir_local:$out_dir -v "$pwd"/models:$models_dir -d ufaldsg/cloud-asr-hclg bash -c "cd /app/cloud-asr-hclg; python run.py --out-dir $out_dir --lm $models_dir/build2 --am $models_dir/tri2b_bmmi.mdl --tree $models_dir/tri2b_bmmi.tree --mat $models_dir/tri2b_bmmi.mat --sil $models_dir/silence.csl --lang en")
echo Docker container id: $id; echo SEE THE DOCKER CONTAINER STDOUT/STDERR BELOW; echo
docker logs $id

echo; echo The building hclg inside docker finished with exit code `docker wait $id`
