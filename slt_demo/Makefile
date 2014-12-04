IP=`ifconfig docker0 | sed -n 's/addr://g;s/.*inet \([^ ]*\) .*/\1/p'`

MONITOR_OPTS=--name monitor \
	-p 8001:80 \
	-p 5681:5681 \
	-e MONITOR_ADDR=tcp://0.0.0.0:5681

MASTER_OPTS=--name master \
	-p 5679:5679 \
	-p 5680:5680 \
	-e WORKER_ADDR=tcp://0.0.0.0:5679 \
	-e FRONTEND_ADDR=tcp://0.0.0.0:5680 \
	-e MONITOR_ADDR=tcp://${IP}:5681

FRONTEND_OPTS=--name frontend \
	-p 8000:80 \
	-e MASTER_ADDR=tcp://${IP}:5680

WORKER_EN_OPTS=--name worker_en \
	-p 30000:5678 \
	-e HOST=${IP} \
	-e PORT0=30000 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e MODEL=en-towninfo \
	-v ${CURDIR}/data:/tmp/data

WORKER_EN_WIKI_OPTS=--name worker_en_wiki \
	-p 30001:5678 \
	-e HOST=${IP} \
	-e PORT0=30001 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e MODEL=en-wiki \
	-v ${CURDIR}/data:/tmp/data

WORKER_CS_OPTS=--name worker_cs \
	-p 30002:5678 \
	-e HOST=${IP} \
	-e PORT0=30002 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e MODEL=cs \
	-v ${CURDIR}/data:/tmp/data

WORKER_CS_ALEX_OPTS=--name worker_cs_alex \
	-p 30003:5678 \
	-e HOST=${IP} \
	-e PORT0=30003 \
	-e MASTER_ADDR=tcp://${IP}:5679 \
	-e MODEL=cs-alex \
	-v ${CURDIR}/data:/tmp/data

pull:
	docker pull ufaldsg/cloud-asr-frontend
	docker pull ufaldsg/cloud-asr-worker-en-towninfo
	docker pull ufaldsg/cloud-asr-worker-en-wiki
	docker pull ufaldsg/cloud-asr-worker-cs
	docker pull ufaldsg/cloud-asr-worker-cs-alex
	docker pull ufaldsg/cloud-asr-master
	docker pull ufaldsg/cloud-asr-monitor

run_locally:
	docker run ${FRONTEND_OPTS} -d ufaldsg/cloud-asr-frontend
	docker run ${WORKER_EN_OPTS} -d ufaldsg/cloud-asr-worker-en-towninfo
	docker run ${WORKER_EN_WIKI_OPTS} -d ufaldsg/cloud-asr-worker-en-wiki
	docker run ${WORKER_CS_OPTS} -d ufaldsg/cloud-asr-worker-cs
	docker run ${WORKER_CS_ALEX_OPTS} -d ufaldsg/cloud-asr-worker-cs-alex
	docker run ${MASTER_OPTS} -d ufaldsg/cloud-asr-master
	docker run ${MONITOR_OPTS} -d ufaldsg/cloud-asr-monitor

run_mesos:
	python ${CURDIR}/../deployment/run_on_mesos.py ${CURDIR}/mesos.json

stop:
	docker kill frontend master monitor worker_en worker_en_wiki worker_cs worker_cs_alex
	docker rm frontend master monitor worker_en worker_en_wiki worker_cs worker_cs_alex

