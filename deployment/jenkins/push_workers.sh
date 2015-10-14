#!/bin/bash

docker login -u "$DOCKER_USER" -p "$DOCKER_PASSWORD" -e "$DOCKER_EMAIL" $DOCKER_REGISTRY

docker tag -f ufaldsg/cloud-asr-worker-cs $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-cs:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-cs-alex $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-cs-alex:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-en-towninfo $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-towninfo:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-en-voxforge $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-voxforge:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-en-wiki $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-wiki:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-dummy $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-dummy:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker-downloader $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-downloader:$BUILD_NUMBER

docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-cs:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-cs-alex:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-towninfo:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-voxforge:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-en-wiki:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-dummy:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker-downloader:$BUILD_NUMBER
