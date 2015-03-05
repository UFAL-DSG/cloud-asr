SHELL=/bin/bash
IP=`ip addr show docker0 | grep -Po 'inet \K[\d.]+'`
MESOS_SLAVE_IP=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' mesos-slave`
API_HOST_PORT=8000
MONITOR_HOST_PORT=8001
RECORDINGS_HOST_PORT=8002
MONITOR_STATUS_PORT=5681
MONITOR_STATUS_ADDR=tcp://${IP}:${MONITOR_STATUS_PORT}
WORKER_PORT=5678
WORKER_ADDR=tcp://${IP}:${WORKER_PORT}
MASTER_TO_WORKER_PORT=5679
MASTER_TO_WORKER_ADDR=tcp://${IP}:${MASTER_TO_WORKER_PORT}
MASTER_TO_API_PORT=5680
MASTER_TO_API_ADDR=tcp://${IP}:${MASTER_TO_API_PORT}
RECORDINGS_SAVER_HOST_PORT=5682
RECORDINGS_SAVER_GUEST_PORT=5682
RECORDINGS_SAVER_ADDR=tcp://${IP}:${RECORDINGS_SAVER_HOST_PORT}
MYSQL_ROOT_PASSWORD=123456
MYSQL_USER=cloudasr
MYSQL_PASSWORD=cloudasr
MYSQL_DATABASE=cloudasr
MYSQL_IP=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' mysql`
MYSQL_CONNECTION_STRING="mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_IP}/${MYSQL_DATABASE}?charset=utf8"

SHARED_VOLUME=${CURDIR}/cloudasr/shared/cloudasr:/usr/local/lib/python2.7/dist-packages/cloudasr
MASTER_VOLUMES=-v ${CURDIR}/cloudasr/master:/opt/app -v ${SHARED_VOLUME}
MASTER_OPTS=--name master \
	-p ${MASTER_TO_WORKER_PORT}:${MASTER_TO_WORKER_PORT} \
	-p ${MASTER_TO_API_PORT}:${MASTER_TO_API_PORT} \
	-e WORKER_ADDR=tcp://0.0.0.0:${MASTER_TO_WORKER_PORT} \
	-e API_ADDR=tcp://0.0.0.0:${MASTER_TO_API_PORT} \
	-e MONITOR_ADDR=${MONITOR_STATUS_ADDR} \
	${MASTER_VOLUMES}

WORKER_VOLUMES=-v ${CURDIR}/cloudasr/worker:/opt/app -v ${SHARED_VOLUME} -v ${CURDIR}/resources/:/opt/resources/
WORKER_OPTS=--name worker \
	-p ${WORKER_PORT}:${WORKER_PORT} \
	-e HOST=${IP} \
	-e PORT0=${WORKER_PORT} \
	-e MASTER_ADDR=${MASTER_TO_WORKER_ADDR} \
	-e RECORDINGS_SAVER_ADDR=${RECORDINGS_SAVER_ADDR} \
	-e MODEL=en-towninfo \
	-v ${CURDIR}/data:/tmp/data \
	${WORKER_VOLUMES}

WEB_VOLUMES=-v ${CURDIR}/cloudasr/web:/opt/app -v ${SHARED_VOLUME}
WEB_OPTS=--name web \
	-p 8004:80 \
	-e CONNECTION_STRING=${MYSQL_CONNECTION_STRING} \
	-e GOOGLE_LOGIN_CLIENT_ID=${CLOUDASR_GOOGLE_LOGIN_CLIENT_ID} \
	-e GOOGLE_LOGIN_CLIENT_SECRET=${CLOUDASR_GOOGLE_LOGIN_CLIENT_SECRET} \
	-e GA_TRACKING_ID='' \
	-e API_URL=http://${IP}:${API_HOST_PORT} \
	-e DEBUG=1 \
	${WEB_VOLUMES}

API_VOLUMES=-v ${CURDIR}/cloudasr/api:/opt/app -v ${SHARED_VOLUME}
API_OPTS=--name api \
	-p ${API_HOST_PORT}:80 \
	-e MASTER_ADDR=${MASTER_TO_API_ADDR} \
	${API_VOLUMES}

MONITOR_VOLUMES=-v ${CURDIR}/cloudasr/monitor:/opt/app -v ${SHARED_VOLUME}
MONITOR_OPTS=--name monitor \
	-p ${MONITOR_HOST_PORT}:80 \
	-p ${MONITOR_STATUS_PORT}:${MONITOR_STATUS_PORT} \
	-e MONITOR_ADDR=tcp://0.0.0.0:${MONITOR_STATUS_PORT} \
	${MONITOR_VOLUMES}

MYSQL_OPTS=--name mysql \
	-e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
	-e MYSQL_USER=${MYSQL_USER} \
	-e MYSQL_PASSWORD=${MYSQL_PASSWORD} \
	-e MYSQL_DATABASE=${MYSQL_DATABASE} \
	-v ${CURDIR}/mysql_data:/var/lib/mysql \
	-v ${CURDIR}/resources/mysql_utf8.cnf:/etc/mysql/conf.d/mysql_utf8.cnf

RECORDINGS_VOLUMES=-v ${CURDIR}/cloudasr/recordings:/opt/app \
	-v ${CURDIR}/cloudasr/recordings/static/data:/opt/app/static/data \
	-v ${SHARED_VOLUME}
RECORDINGS_OPTS=--name recordings \
	--link mysql:mysql \
	-p ${RECORDINGS_SAVER_HOST_PORT}:${RECORDINGS_SAVER_GUEST_PORT} \
	-p ${RECORDINGS_HOST_PORT}:80 \
	-e CONNECTION_STRING=${MYSQL_CONNECTION_STRING} \
	-e STORAGE_PATH=/opt/app/static/data \
	-e DOMAIN=http://localhost:8002 \
	${RECORDINGS_VOLUMES}

build:
	docker build -t ufaldsg/cloud-asr-base cloudasr/shared
	docker build -t ufaldsg/cloud-asr-web cloudasr/web
	docker build -t ufaldsg/cloud-asr-api cloudasr/api/
	docker build -t ufaldsg/cloud-asr-worker cloudasr/worker/
	docker build -t ufaldsg/cloud-asr-master cloudasr/master/
	docker build -t ufaldsg/cloud-asr-monitor cloudasr/monitor/
	docker build -t ufaldsg/cloud-asr-recordings cloudasr/recordings/

build_local:
	cp -r cloudasr/shared/cloudasr cloudasr/api/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/worker/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/master/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/monitor/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/recordings/cloudasr
	docker build -t ufaldsg/cloud-asr-api cloudasr/api/
	docker build -t ufaldsg/cloud-asr-worker cloudasr/worker/
	docker build -t ufaldsg/cloud-asr-master cloudasr/master/
	docker build -t ufaldsg/cloud-asr-monitor cloudasr/monitor/
	docker build -t ufaldsg/cloud-asr-recordings cloudasr/recordings/
	rm -rf cloudasr/api/cloudasr
	rm -rf cloudasr/worker/cloudasr
	rm -rf cloudasr/master/cloudasr
	rm -rf cloudasr/monitor/cloudasr
	rm -rf cloudasr/recordings/cloudasr

pull:
	docker pull mysql
	docker pull ufaldsg/cloud-asr-api
	docker pull ufaldsg/cloud-asr-worker
	docker pull ufaldsg/cloud-asr-master
	docker pull ufaldsg/cloud-asr-monitor
	docker pull ufaldsg/cloud-asr-recordings

mysql_data:
	echo "PREPARING MySQL DATABASE"
	docker run ${MYSQL_OPTS} -d mysql
	docker stop mysql && docker rm mysql

run_locally: mysql_data
	docker run ${MYSQL_OPTS} -d mysql
	docker run ${WEB_OPTS} -d ufaldsg/cloud-asr-web
	docker run ${API_OPTS} -d ufaldsg/cloud-asr-api
	docker run ${WORKER_OPTS} -d ufaldsg/cloud-asr-worker
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master
	docker run ${MONITOR_OPTS} -d ufaldsg/cloud-asr-monitor
	docker run ${RECORDINGS_OPTS} -d ufaldsg/cloud-asr-recordings

run_mesos:
	python ${CURDIR}/deployment/run_on_mesos.py ${CURDIR}/deployment/mesos.json

run_worker:
	docker run ${WORKER_OPTS} -i -t --rm ufaldsg/cloud-asr-worker

run_web:
	docker run ${WEB_OPTS} -i -t --rm ufaldsg/cloud-asr-web python run.py

run_api:
	docker run ${API_OPTS} -i -t --rm ufaldsg/cloud-asr-api

run_master:
	docker run ${MASTER_OPTS} -i -t --rm ufaldsg/cloud-asr-master

run_monitor:
	docker run ${MONITOR_OPTS} -i -t --rm ufaldsg/cloud-asr-monitor

run_recordings:
	docker run ${RECORDINGS_OPTS} -i -t --rm ufaldsg/cloud-asr-recordings

stop:
	docker kill api worker master monitor recordings mysql web
	docker rm api worker master monitor recordings mysql web

unit-test:
	nosetests cloudasr/shared/cloudasr
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/api
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/master
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory -e vad cloudasr/worker
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/monitor
	PYTHONPATH=${CURDIR}/cloudasr/shared nosetests -e test_factory cloudasr/recordings

integration-test:
	docker run ${API_VOLUMES} --rm ufaldsg/cloud-asr-api nosetests /opt/app/test_factory.py
	docker run ${MASTER_VOLUMES} --rm ufaldsg/cloud-asr-master nosetests /opt/app/test_factory.py
	docker run ${MONITOR_VOLUMES} --rm ufaldsg/cloud-asr-monitor nosetests /opt/app/test_factory.py
	docker run ${RECORDINGS_VOLUMES} --rm ufaldsg/cloud-asr-recordings nosetests /opt/app/test_factory.py
	docker run ${WORKER_VOLUMES} --rm ufaldsg/cloud-asr-worker nosetests /opt/app/test_factory.py /opt/app/vad/test.py

test:
	nosetests tests/

compile-messages:
	protoc --python_out=. ./cloudasr/shared/cloudasr/messages/messages.proto

mysql-console:
	mysql --host=${MYSQL_IP} --user=${MYSQL_USER} --password=${MYSQL_PASSWORD} ${MYSQL_DATABASE}
