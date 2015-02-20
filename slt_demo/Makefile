IP=`ifconfig docker0 | sed -n 's/addr://g;s/.*inet \([^ ]*\) .*/\1/p'`
MYSQL_ROOT_PASSWORD=123456
MYSQL_USER=cloudasr
MYSQL_PASSWORD=cloudasr
MYSQL_DATABASE=cloudasr
MYSQL_IP=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' mysql`
MYSQL_CONNECTION_STRING=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_IP}/${MYSQL_DATABASE}

MONITOR_OPTS=--name monitor \
	-p 8001:80 \
	-p 5681:5681 \
	-e MONITOR_ADDR=tcp://0.0.0.0:5681

MASTER_OPTS=--name master \
	-p 5679:5679 \
	-p 5680:5680 \
	-e WORKER_ADDR=tcp://0.0.0.0:5679 \
	-e API_ADDR=tcp://0.0.0.0:5680 \
	-e MONITOR_ADDR=tcp://${IP}:5681

WEB_OPTS=--name web \
	-p 8004:80 \
	-e CONNECTION_STRING=${MYSQL_CONNECTION_STRING} \
	-e GOOGLE_LOGIN_CLIENT_ID=${CLOUDASR_GOOGLE_LOGIN_CLIENT_ID} \
	-e GOOGLE_LOGIN_CLIENT_SECRET=${CLOUDASR_GOOGLE_LOGIN_CLIENT_SECRET} \
	-e API_URL=http://${IP}:8000 \

API_OPTS=--name api \
	-p 8000:80 \
	-e MASTER_ADDR=tcp://${IP}:5680

WORKER_EN_OPTS=--name worker_en \
	-p 30000:5678 \
	-e HOST=${IP} \
	-e PORT0=30000 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e RECORDINGS_SAVER_ADDR=tcp://${IP}:5682 \
	-e MODEL=en-towninfo

WORKER_EN_WIKI_OPTS=--name worker_en_wiki \
	-p 30001:5678 \
	-e HOST=${IP} \
	-e PORT0=30001 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e RECORDINGS_SAVER_ADDR=tcp://${IP}:5682 \
	-e MODEL=en-wiki

WORKER_EN_VOXFORGE_WIKI_OPTS=--name worker_en_voxforge_wiki \
	-p 30004:5678 \
	-e HOST=${IP} \
	-e PORT0=30004 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e RECORDINGS_SAVER_ADDR=tcp://${IP}:5682 \
	-e MODEL=en-voxforge

WORKER_CS_OPTS=--name worker_cs \
	-p 30002:5678 \
	-e HOST=${IP} \
	-e PORT0=30002 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e RECORDINGS_SAVER_ADDR=tcp://${IP}:5682 \
	-e MODEL=cs

WORKER_CS_ALEX_OPTS=--name worker_cs_alex \
	-p 30003:5678 \
	-e HOST=${IP} \
	-e PORT0=30003 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e RECORDINGS_SAVER_ADDR=tcp://${IP}:5682 \
	-e MODEL=cs-alex

ANNOTATION_INTERFACE_OPTS=--name annotation_interface \
	-p 5682:5682 \
	-p 8002:80 \
	-e CONNECTION_STRING=${MYSQL_CONNECTION_STRING} \
	-e GOOGLE_LOGIN_CLIENT_ID=${CLOUDASR_GOOGLE_LOGIN_CLIENT_ID} \
	-e GOOGLE_LOGIN_CLIENT_SECRET=${CLOUDASR_GOOGLE_LOGIN_CLIENT_SECRET} \
	-v ${CURDIR}/../cloudasr/annotation_interface/static/data:/opt/app/static/data

MYSQL_OPTS=--name mysql \
	-e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
	-e MYSQL_USER=${MYSQL_USER} \
	-e MYSQL_PASSWORD=${MYSQL_PASSWORD} \
	-e MYSQL_DATABASE=${MYSQL_DATABASE} \
	-v ${CURDIR}/mysql_data:/var/lib/mysql

pull:
	docker pull mysql
	docker pull ufaldsg/cloud-asr-web
	docker pull ufaldsg/cloud-asr-api
	docker pull ufaldsg/cloud-asr-worker-en-towninfo
	docker pull ufaldsg/cloud-asr-worker-en-wiki
	docker pull ufaldsg/cloud-asr-worker-en-voxforge
	docker pull ufaldsg/cloud-asr-worker-cs
	docker pull ufaldsg/cloud-asr-worker-cs-alex
	docker pull ufaldsg/cloud-asr-master
	docker pull ufaldsg/cloud-asr-monitor
	docker pull ufaldsg/cloud-asr-annotation-interface

mysql_data:
	echo "PREPARING MySQL DATABASE"
	docker run ${MYSQL_OPTS} -d mysql
	docker stop mysql && docker rm mysql

run_locally: mysql_data
	docker run ${MYSQL_OPTS} -d mysql
	docker run ${WEB_OPTS} -d ufaldsg/cloud-asr-web
	docker run ${API_OPTS} -d ufaldsg/cloud-asr-api
	docker run ${WORKER_EN_OPTS} -d ufaldsg/cloud-asr-worker-en-towninfo
	docker run ${WORKER_EN_WIKI_OPTS} -d ufaldsg/cloud-asr-worker-en-wiki
	docker run ${WORKER_EN_VOXFORGE_WIKI_OPTS} -d ufaldsg/cloud-asr-worker-en-voxforge
	docker run ${WORKER_CS_OPTS} -d ufaldsg/cloud-asr-worker-cs
	docker run ${WORKER_CS_ALEX_OPTS} -d ufaldsg/cloud-asr-worker-cs-alex
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master
	docker run ${MONITOR_OPTS} -d ufaldsg/cloud-asr-monitor
	docker run ${ANNOTATION_INTERFACE_OPTS} -d ufaldsg/cloud-asr-annotation-interface

run_mesos:
	python ${CURDIR}/../deployment/run_on_mesos.py ${CURDIR}/mesos.json

stop:
	docker kill web api master monitor worker_en worker_en_wiki worker_en_voxforge_wiki worker_cs worker_cs_alex annotation_interface mysql
	docker rm web api master monitor worker_en worker_en_wiki worker_en_voxforge_wiki worker_cs worker_cs_alex annotation_interface mysql

