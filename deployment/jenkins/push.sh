#!/bin/bash

docker login -u "$DOCKER_USER" -p "$DOCKER_PASSWORD" -e "$DOCKER_EMAIL" $DOCKER_REGISTRY

docker tag ufaldsg/cloud-asr-base $DOCKER_REGISTRY/ufaldsg/cloud-asr-base:$BUILD_NUMBER
docker tag ufaldsg/cloud-asr-master $DOCKER_REGISTRY/ufaldsg/cloud-asr-master:$BUILD_NUMBER
docker tag ufaldsg/cloud-asr-frontend $DOCKER_REGISTRY/ufaldsg/cloud-asr-frontend:$BUILD_NUMBER
docker tag ufaldsg/cloud-asr-worker $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker:$BUILD_NUMBER
docker tag ufaldsg/cloud-asr-monitor $DOCKER_REGISTRY/ufaldsg/cloud-asr-monitor:$BUILD_NUMBER
docker tag ufaldsg/cloud-asr-annotation-interface $DOCKER_REGISTRY/ufaldsg/cloud-asr-annotation-interface:$BUILD_NUMBER

docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-base:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-master:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-frontend:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-worker:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-monitor:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/cloud-asr-annotation-interface:$BUILD_NUMBER
