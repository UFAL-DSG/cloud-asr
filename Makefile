IP=`ifconfig docker0 | sed -n 's/addr://g;s/.*inet \([^ ]*\) .*/\1/p'`
FRONTEND_HOST_PORT=8000
FRONTEND_GUEST_PORT=8000
WORKER_PORT=5678
WORKER_ADDR=tcp://${IP}:${WORKER_PORT}
MASTER_TO_WORKER_PORT=5679
MASTER_TO_WORKER_ADDR=tcp://${IP}:${MASTER_TO_WORKER_PORT}
MASTER_TO_FRONTEND_PORT=5680
MASTER_TO_FRONTEND_ADDR=tcp://${IP}:${MASTER_TO_FRONTEND_PORT}

SHARED_VOLUME=${CURDIR}/cloudasr/shared/cloudasr:/usr/local/lib/python2.7/dist-packages/cloudasr
MASTER_VOLUMES=-v ${CURDIR}/cloudasr/master:/opt/app -v ${SHARED_VOLUME}
MASTER_OPTS=--name master \
	-p ${MASTER_TO_WORKER_PORT}:${MASTER_TO_WORKER_PORT} \
	-p ${MASTER_TO_FRONTEND_PORT}:${MASTER_TO_FRONTEND_PORT} \
	-e WORKER_ADDR=tcp://0.0.0.0:${MASTER_TO_WORKER_PORT} \
	-e FRONTEND_ADDR=tcp://0.0.0.0:${MASTER_TO_FRONTEND_PORT} \
	${MASTER_VOLUMES}

WORKER_VOLUMES=-v ${CURDIR}/cloudasr/worker:/opt/app -v ${SHARED_VOLUME}
WORKER_OPTS=--name worker \
	-p ${WORKER_PORT}:${WORKER_PORT} \
	-e MY_ADDR=tcp://0.0.0.0:${WORKER_PORT} \
	-e PUBLIC_ADDR=${WORKER_ADDR} \
	-e MASTER_ADDR=${MASTER_TO_WORKER_ADDR} \
	-e MODEL=en-GB \
	${WORKER_VOLUMES}

FRONTEND_VOLUMES=-v ${CURDIR}/cloudasr/frontend:/opt/app -v ${SHARED_VOLUME}
FRONTEND_OPTS=--name frontend \
	-p ${FRONTEND_HOST_PORT}:${FRONTEND_GUEST_PORT} \
	-e MASTER_ADDR=${MASTER_TO_FRONTEND_ADDR} \
	${FRONTEND_VOLUMES}

build:
	cp -r cloudasr/shared/cloudasr cloudasr/frontend/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/worker/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/master/cloudasr
	docker build -t ufaldsg/cloud-asr-frontend cloudasr/frontend/
	docker build -t ufaldsg/cloud-asr-worker cloudasr/worker/
	docker build -t ufaldsg/cloud-asr-master cloudasr/master/
	rm -rf cloudasr/frontend/cloudasr
	rm -rf cloudasr/worker/cloudasr
	rm -rf cloudasr/master/cloudasr

pull:
	docker pull ufaldsg/cloud-asr-frontend
	docker pull ufaldsg/cloud-asr-worker
	docker pull ufaldsg/cloud-asr-master

run:
	docker run ${FRONTEND_OPTS} -d ufaldsg/cloud-asr-frontend
	docker run ${WORKER_OPTS} -d ufaldsg/cloud-asr-worker
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master

run_worker:
	docker run ${WORKER_OPTS} -i -t --rm ufaldsg/cloud-asr-worker

run_frontend:
	docker run ${FRONTEND_OPTS} -i -t --rm ufaldsg/cloud-asr-frontend

run_master:
	docker run ${MASTER_OPTS} -i -t --rm ufaldsg/cloud-asr-master

stop:
	docker kill frontend worker master
	docker rm frontend worker master

unit-test:
	nosetests cloudasr/shared
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/frontend
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/master
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/worker

integration-test:
	docker run ${FRONTEND_VOLUMES} --rm ufaldsg/cloud-asr-frontend nosetests /opt/app/test_factory.py
	docker run ${MASTER_VOLUMES} --rm ufaldsg/cloud-asr-master nosetests /opt/app/test_factory.py
	docker run ${WORKER_VOLUMES} --rm ufaldsg/cloud-asr-worker nosetests /opt/app/test_factory.py

test:
	nosetests tests/

compile-messages:
	protoc --python_out=. ./cloudasr/shared/cloudasr/messages/messages.proto
