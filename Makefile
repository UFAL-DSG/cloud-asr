SHELL=/bin/bash
IP=10.100.210.17
DEMO_URL=http://${IP}:8003/demo/en-towninfo
MONITOR_URL=http://${IP}:8001/
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
MYSQL_PATH=`docker-machine ssh dev '(mkdir /home/docker/mysql_data ; echo /home/docker/mysql_data) 2> /dev/null' || echo ${CURDIR}/mysql_data`
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
	-p 8003:80 \
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
	-e CONNECTION_STRING=${MYSQL_CONNECTION_STRING} \
	-e DEBUG=1 \
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
	-v ${MYSQL_PATH}:/var/lib/mysql \
	-v ${CURDIR}/resources/mysql_utf8.cnf:/etc/mysql/conf.d/mysql_utf8.cnf \
	-v ${CURDIR}/deployment/schema.sql:/docker-entrypoint-initdb.d/schema.sql

MYSQL_CONSOLE_CMD=mysql -v --host=mysql_address --user=${MYSQL_PASSWORD} --password=${MYSQL_PASSWORD} ${MYSQL_DATABASE}

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
	-e DEBUG=1 \
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
#	docker build -t ufaldsg/cloud-asr-base cloudasr/shared
	cp -r cloudasr/shared/cloudasr cloudasr/api/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/worker/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/master/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/monitor/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/recordings/cloudasr
	cp -r cloudasr/shared/cloudasr cloudasr/web/cloudasr
	docker build -t ufaldsg/cloud-asr-api cloudasr/api/
	docker build -t ufaldsg/cloud-asr-worker cloudasr/worker/
	docker build -t ufaldsg/cloud-asr-master cloudasr/master/
	docker build -t ufaldsg/cloud-asr-monitor cloudasr/monitor/
	docker build -t ufaldsg/cloud-asr-recordings cloudasr/recordings/
	docker build -t ufaldsg/cloud-asr-web cloudasr/web
	rm -rf cloudasr/api/cloudasr
	rm -rf cloudasr/worker/cloudasr
	rm -rf cloudasr/master/cloudasr
	rm -rf cloudasr/monitor/cloudasr
	rm -rf cloudasr/recordings/cloudasr
	rm -rf cloudasr/web/cloudasr
remove-all:
	docker stop $(docker container list -a -q)
	docker rm $(docker container list -a -q)
	docker rmi $(docker images -a)

remove-images:
	docker images | grep "ufaldsg/" | awk '{print $$3}' | xargs docker rmi

pull:
	docker pull mysql
	docker pull ufaldsg/cloud-asr-web
	docker pull ufaldsg/cloud-asr-api
	docker pull ufaldsg/cloud-asr-worker
	docker pull ufaldsg/cloud-asr-master
	docker pull ufaldsg/cloud-asr-monitor
	docker pull ufaldsg/cloud-asr-recordings

mysql_data:
	echo "PREPARING MySQL DATABASE"
	docker run ${MYSQL_OPTS} -d mysql
	sleep 15
	docker stop mysql && docker rm mysql
	touch mysql_data 2> /dev/null || echo "MySQL DATABASE PREPARED"

check_ip:
	test ${IP} || { echo "ERROR: Could not obtain an IP address of the machine. Please, update the IP variable in the Makefile manually."; exit 1; }

run: check_ip mysql_data
	@echo docker run ${MYSQL_OPTS} -d mysql
	docker run ${MYSQL_OPTS} -d mysql
	docker run ${WEB_OPTS} -d ufaldsg/cloud-asr-web
	docker run ${API_OPTS} -d ufaldsg/cloud-asr-api
	docker run ${WORKER_OPTS} -d ufaldsg/cloud-asr-worker
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master
	docker run ${MONITOR_OPTS} -d ufaldsg/cloud-asr-monitor
	docker run ${RECORDINGS_OPTS} -d ufaldsg/cloud-asr-recordings

run_locally: check_ip mysql_data
	bash <( python ${CURDIR}/deployment/run_locally.py ${IP} ${CURDIR}/cloudasr.json )
run_mysql:
	docker run ${MYSQL_OPTS} -d mysql
run_api2:
	docker run ${API_OPTS} -d ufaldsg/cloud-asr-api
run_worker2:
	docker run ${WORKER_OPTS} -d ufaldsg/cloud-asr-worker
run_master2:
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master

stop_locally:
	docker ps -a | \
		grep `grep "domain" cloudasr.json | sed 's/ *"domain": *"//;s/",//;s/\./-/g'` | \
		awk '{print $$1}' | \
		xargs docker kill | \
		xargs docker rm

run_mesos:
	python ${CURDIR}/deployment/run_on_mesos.py ${CURDIR}/cloudasr.json

run_worker:
	docker run ${WORKER_OPTS} -i -t --rm ufaldsg/cloud-asr-worker

run_web:
	docker run ${WEB_OPTS} -i -t --rm ufaldsg/cloud-asr-web python run.py

run_api:
	docker run ${API_OPTS} -i -t --rm ufaldsg/cloud-asr-api python run.py

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
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose cloudasr/shared/cloudasr
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose -e test_factory cloudasr/api
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose -e test_factory cloudasr/master
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose -e test_factory cloudasr/worker/test_lib.py
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose -e test_factory cloudasr/monitor
	PYTHONPATH=${CURDIR}/cloudasr/shared python2.7 -m nose -e test_factory cloudasr/recordings

integration-test:
	docker run ${API_VOLUMES} --rm ufaldsg/cloud-asr-api python2.7 -m nose /opt/app/test_factory.py
	docker run ${MASTER_VOLUMES} --rm ufaldsg/cloud-asr-master python2.7 -m nose /opt/app/test_factory.py
	docker run ${MONITOR_VOLUMES} --rm ufaldsg/cloud-asr-monitor python2.7 -m nose /opt/app/test_factory.py
	docker run ${RECORDINGS_VOLUMES} --rm ufaldsg/cloud-asr-recordings python2.7 -m nose /opt/app/test_factory.py
	docker run ${WORKER_VOLUMES} --rm ufaldsg/cloud-asr-worker python2.7 -m nose /opt/app/test_factory.py /opt/app/vad/test.py

test:
	python2.7 -m nose tests/

compile-messages:
	protoc --python_out=. ./cloudasr/shared/cloudasr/messages/messages.proto

mysql-console:
	docker run --link cloudasr-com-mysql:mysql_address -i -t --rm mysql ${MYSQL_CONSOLE_CMD}

open-demo:
	open ${DEMO_URL} || google-chrome ${DEMO_URL} || echo "open url in your browser: ${DEMO_URL}"

open-monitor:
	open ${MONITOR_URL} || google-chrome ${MONITOR_URL} || echo "open url in yout browser: ${MONITOR_URL}"

test-curl:
	curl -X POST --data-binary @resources/test.wav --header 'Content-Type: audio/x-wav; rate=16000;' http://${IP}:8000/recognize?lang=en-towninfo | ( json_pp || cat )
