IP=`ifconfig eth0 | sed -n 's/.*inet addr:\([^ ]*\) .*/\1/p'`
FRONTEND_HOST_PORT=8000
FRONTEND_GUEST_PORT=8000
WORKER_PORT=5678
WORKER_ADDR=tcp://${IP}:${WORKER_PORT}
MASTER_TO_WORKER_PORT=5679
MASTER_TO_WORKER_ADDR=tcp://${IP}:${MASTER_TO_WORKER_PORT}
MASTER_TO_FRONTEND_PORT=5680
MASTER_TO_FRONTEND_ADDR=tcp://${IP}:${MASTER_TO_FRONTEND_PORT}

build:
	sudo docker build -t frontend cloudasr/frontend/
	sudo docker build -t worker cloudasr/worker/
	sudo docker build -t master cloudasr/master/

run:
	sudo docker run --name frontend -p ${FRONTEND_HOST_PORT}:${FRONTEND_GUEST_PORT} -e WORKER_ADDR=${WORKER_ADDR} -d frontend
	sudo docker run --name worker -p ${WORKER_PORT}:${WORKER_PORT} -e MY_ADDR=tcp://0.0.0.0:${WORKER_PORT} -e MASTER_ADDR=${MASTER_TO_WORKER_ADDR} -e MODEL=en-GB -d worker
	sudo docker run --name master \
		-p ${MASTER_TO_WORKER_PORT}:${MASTER_TO_WORKER_PORT} \
		-p ${MASTER_TO_FRONTEND_PORT}:${MASTER_TO_FRONTEND_PORT} \
		-e WORKER_ADDR=tcp://0.0.0.0:${MASTER_TO_WORKER_PORT} \
		-e FRONTEND_ADDR=tcp://0.0.0.0:${MASTER_TO_FRONTEND_PORT} \
		-d master

run_worker:
	sudo docker run --name worker -p ${WORKER_PORT}:${WORKER_PORT} -e MY_ADDR=tcp://0.0.0.0:${WORKER_PORT} -e MASTER_ADDR=${MASTER_TO_WORKER_ADDR} -i -t --rm worker

run_frontend:
	sudo docker run --name frontend -p ${FRONTEND_HOST_PORT}:${FRONTEND_GUEST_PORT} -e WORKER_ADDR=${WORKER_ADDR} -i -t --rm frontend

run_master:
	sudo docker run --name master \
		-p ${MASTER_TO_WORKER_PORT}:${MASTER_TO_WORKER_PORT} \
		-p ${MASTER_TO_FRONTEND_PORT}:${MASTER_TO_FRONTEND_PORT} \
		-e WORKER_ADDR=tcp://0.0.0.0:${MASTER_TO_WORKER_PORT} \
		-e FRONTEND_ADDR=tcp://0.0.0.0:${MASTER_TO_FRONTEND_PORT} \
		-i -t --rm master

stop:
	sudo docker kill frontend worker master
	sudo docker rm frontend worker master

test:
	nosetests tests/
	nosetests cloudasr/master/
	nosetests cloudasr/worker/
	nosetests cloudasr/frontend/
