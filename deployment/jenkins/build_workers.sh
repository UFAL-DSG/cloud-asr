#!/bin/bash

docker build -t ufaldsg/cloud-asr-worker-cs examples/worker_cs
docker build -t ufaldsg/cloud-asr-worker-cs-alex examples/worker_cs_alex
docker build -t ufaldsg/cloud-asr-worker-en-towninfo examples/worker_en_towninfo
docker build -t ufaldsg/cloud-asr-worker-en-voxforge examples/worker_en_voxforge_wiki
docker build -t ufaldsg/cloud-asr-worker-en-wiki examples/worker_en_wiki
docker build -t ufaldsg/cloud-asr-worker-dummy examples/worker_dummy
