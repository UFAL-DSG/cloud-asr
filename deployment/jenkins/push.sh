#!/bin/bash

docker login -u "$DOCKER_USER" -p "$DOCKER_PASSWORD" -e "$DOCKER_EMAIL" $DOCKER_REGISTRY

docker tag -f ufaldsg/cloud-asr-base $DOCKER_REGISTRY/ufaldsg/cloud-asr-base:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-master $DOCKER_REGISTRY/ufaldsg/cloud-asr-master:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-api $DOCKER_REGISTRY/ufaldsg/cloud-asr-api:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-web $DOCKER_REGISTRY/ufaldsg/cloud-asr-web:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-worker $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-monitor $DOCKER_REGISTRY/ufaldsg/cloud-asr-monitor:$BUILD_NUMBER
docker tag -f ufaldsg/cloud-asr-recordings $DOCKER_REGISTRY/ufaldsg/cloud-asr-recordings:$BUILD_NUMBER

docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-base:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-master:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-api:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-web:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-monitor:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-recordings:$BUILD_NUMBER
