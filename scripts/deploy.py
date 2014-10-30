#
# docker run --name frontend -p ${FRONTEND_HOST_PORT}:${FRONTEND_GUEST_PORT} -e WORKER_ADDR=${WORKER_ADDR} -d frontend
# sudo docker run --name worker -p ${WORKER_PORT}:${WORKER_PORT} -e MY_ADDR=tcp://0.0.0.0:${WORKER_PORT} -d worker

import os

MASTER_HOST = "147.251.9.251"
FRONTEND_HOSTS = ["147.251.9.251", "147.251.9.244"]
WORKER_HOSTS = ["147.251.9.251", "147.251.9.244"]


def docker_run(host, cmd):
    os.system("ssh root@%s 'docker run %s'" % (host, cmd,))


# Run master.
docker_run(MASTER_HOST, """-p 5000 -d cloudasr-master""")
master_addr = "tcp://%s:5000" % (MASTER_HOST, )

# Run frontends:
master_addr = "tcp://%s:5000" % (MASTER_HOST, )
for worker in FRONTEND_HOSTS:
    docker_run(worker,
        """-p 5000 MASTER_ADDR=%s -d cloudasr-frontend""" % (master_addr, ))

# Run workers:
for worker in WORKER_HOSTS:
    worker_addr = "tcp://%s:5000" % (worker, )
    docker_run(worker,
        """-p 5000 -e MY_ADDR=%s -e MASTER_ADDR=%s -d cloudasr-worker""" % (
            worker_addr, master_addr ))