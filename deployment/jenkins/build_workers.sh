#!/bin/bash

docker build -t ufaldsg/worker_cs examples/worker_cs
docker build -t ufaldsg/worker_cs_alex examples/worker_cs_alex
docker build -t ufaldsg/worker_en_towninfo examples/worker_en_towninfo
docker build -t ufaldsg/worker_en_voxforge_wiki examples/worker_en_voxforge_wiki
docker build -t ufaldsg/worker_en_wiki examples/worker_en_wiki
