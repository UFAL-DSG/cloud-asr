#!/bin/bash
set -e

# ./download_model.sh
# models_dir_local=$1; shift  # `pwd`/models
# out_dir_local=$1; shift  # `pwd`/output_hclg_dir
echo "FIXME: Using fixed directories for testing"
models_dir_local=`pwd`/models
out_dir_local=`pwd`/output_hclg_dir


models_dir=/app/data/models
out_dir=/app/data/output
pwd=`pwd`

mkdir -p $out_dir_local
echo; echo Running docker; echo
echo; echo "Current directory is mapped to dockerimage only for testing"; echo
id=$(docker run -v "$pwd":/app/cloud-asr-hclg -v $out_dir_local:$out_dir \
                -v $models_dir_local:$models_dir -d ufaldsg/cloud-asr-hclg \
  bash -c "cd /app/cloud-asr-hclg; \
      python run.py \
        --log-level DEBUG \
        --path-sh /app/kams_docker/kams/path.sh \
        --out-dir $out_dir \
        --lm $models_dir/final.bg.arpa \
        --am $models_dir/tri2b_bmmi.mdl \
        --am-dict $models_dir/lexicon.txt \
        --tree $models_dir/tri2b_bmmi.tree \
        --mat $models_dir/tri2b_bmmi.mat \
        --sil $models_dir/silence.csl \
        --conf $models_dir/mfcc.conf \
        build_dict --lang cs"
    )

echo Docker container id: $id; echo SEE THE DOCKER CONTAINER STDOUT/STDERR BELOW; echo
docker logs $id

exit_code=`docker wait $id`
echo; echo The building hclg inside docker finished with exit code $exit_code; echo
exit $exit_code
