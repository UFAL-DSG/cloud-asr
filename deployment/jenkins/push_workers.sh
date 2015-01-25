#!/bin/bash

docker login -u "$DOCKER_USER" -p "$DOCKER_PASSWORD" -e "$DOCKER_EMAIL" $DOCKER_REGISTRY

docker tag ufaldsg/worker_cs $DOCKER_REGISTRY/ufaldsg/worker_cs:$BUILD_NUMBER
docker tag ufaldsg/worker_cs_alex $DOCKER_REGISTRY/ufaldsg/worker_cs_alex:$BUILD_NUMBER
docker tag ufaldsg/worker_en_towninfo $DOCKER_REGISTRY/ufaldsg/worker_en_towninfo:$BUILD_NUMBER
docker tag ufaldsg/worker_en_voxforge_wiki $DOCKER_REGISTRY/ufaldsg/worker_en_voxforge_wiki:$BUILD_NUMBER
docker tag ufaldsg/worker_en_wiki $DOCKER_REGISTRY/ufaldsg/worker_en_wiki:$BUILD_NUMBER

docker push $DOCKER_REGISTRY/ufaldsg/worker_cs:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/worker_cs_alex:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/worker_en_towninfo:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/worker_en_voxforge_wiki:$BUILD_NUMBER
docker push $DOCKER_REGISTRY/ufaldsg/worker_en_wiki:$BUILD_NUMBER
