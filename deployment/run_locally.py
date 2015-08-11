import os
import sys
import json

IP = "`(boot2docker ip || (ip addr show docker0 | grep -Po 'inet \K[\d.]+')) 2> /dev/null`"
CURDIR = os.getcwd()

API_HOST_PORT = 8000
MONITOR_HOST_PORT = 8001
RECORDINGS_HOST_PORT = 8002
WEB_HOST_PORT = 8003

MASTER_TO_WORKER_PORT = 5678
MASTER_TO_API_PORT = 5679
MONITOR_STATUS_PORT = 5680
RECORDINGS_SAVER_PORT = 5682
WORKER_PORT = 30000

MYSQL_ROOT_PASSWORD=123456
MYSQL_USER="cloudasr"
MYSQL_PASSWORD="cloudasr"
MYSQL_DATABASE="cloudasr"
MYSQL_PATH="`(boot2docker ssh 'mkdir /home/docker/mysql_data ; echo /home/docker/mysql_data') 2> /dev/null || echo %s/mysql_data`" % CURDIR

def format_name(domain, name):
    return "%s-%s" % (domain.replace('.', '-'), name)

def run_docker(image, tag, opts, command = ""):
    print " ".join(["docker run -d", " ".join(opts), "%s:%s" % (image, tag), command])

def stop_running_instances(config):
    print "docker ps -a | grep %s | awk '{print $1}' | xargs docker kill | xargs docker rm" % format_name(config["domain"], "")


def run_mysql(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'mysql'),
        "-e MYSQL_ROOT_PASSWORD=%s" % MYSQL_ROOT_PASSWORD,
        "-e MYSQL_USER=%s" % MYSQL_USER,
        "-e MYSQL_PASSWORD=%s" % MYSQL_PASSWORD,
        "-e MYSQL_DATABASE=%s" % MYSQL_DATABASE,
        "-v %s:/var/lib/mysql" % MYSQL_PATH,
        "-v %s/resources/mysql_utf8.cnf:/etc/mysql/conf.d/mysql_utf8.cnf" % CURDIR,
    ]

    run_docker("mysql", "latest", opts)
    print "sleep 5"

def run_master(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'master'),
        "-p %d:%d" % (MASTER_TO_WORKER_PORT, MASTER_TO_WORKER_PORT),
        "-p %d:%d" % (MASTER_TO_API_PORT, MASTER_TO_API_PORT),
        "-e WORKER_ADDR=tcp://0.0.0.0:%d" % MASTER_TO_WORKER_PORT,
        "-e API_ADDR=tcp://0.0.0.0:%d" % MASTER_TO_API_PORT,
        "-e MONITOR_ADDR=tcp://%s:%d" % (IP, MONITOR_STATUS_PORT),
    ]

    run_docker("ufaldsg/cloud-asr-master", config["tag"], opts)

def run_api(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'api'),
        "-p %d:80" % API_HOST_PORT,
        "-e MASTER_ADDR=tcp://%s:%d" % (IP, MASTER_TO_API_PORT),
        "--link %s:mysql" % format_name(config['domain'], 'mysql'),
        "-e CONNECTION_STRING='%s'" % config['connection_string'],
    ]

    run_docker("ufaldsg/cloud-asr-api", config["tag"], opts)


def run_web(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'web'),
        "-p %d:80" % WEB_HOST_PORT,
        "--link %s:mysql" % format_name(config['domain'], 'mysql'),
        "-e CONNECTION_STRING='%s'" % config['connection_string'],
        "-e GOOGLE_LOGIN_CLIENT_ID='%s'" % config['google_login_client_id'],
        "-e GOOGLE_LOGIN_CLIENT_SECRET='%s'" % config['google_login_client_secret'],
        "-e GA_TRACKING_ID='%s'" % config['ga_tracking_id'],
        "-e API_URL=http://%s:%d" % (IP, API_HOST_PORT),
    ]

    run_docker("ufaldsg/cloud-asr-web", config["tag"], opts)

def run_monitor(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'monitor'),
        "-p %d:80" % MONITOR_HOST_PORT,
        "-p %d:%d" % (MONITOR_STATUS_PORT, MONITOR_STATUS_PORT),
        "-e MONITOR_ADDR=tcp://0.0.0.0:%d" % MONITOR_STATUS_PORT,
    ]

    run_docker("ufaldsg/cloud-asr-monitor", config["tag"], opts)

def run_recordings_saver(config):
    opts = [
        "--name %s" % format_name(config['domain'], 'recordings'),
        "-p %d:80" % RECORDINGS_HOST_PORT,
        "-p %d:%d" % (RECORDINGS_SAVER_PORT, RECORDINGS_SAVER_PORT),
        "--link %s:mysql" % format_name(config['domain'], 'mysql'),
        "-e CONNECTION_STRING='%s'" % config['connection_string'],
        "-e STORAGE_PATH=/opt/app/static/data",
        "-v %s/recordings:/opt/app/static/data" % CURDIR,
        "-e DOMAIN=http://localhost:%d" % RECORDINGS_HOST_PORT,
    ]

    run_docker("ufaldsg/cloud-asr-recordings", config["tag"], opts)

def run_worker(config, worker_config):
    global WORKER_PORT

    for i in range(worker_config["instances"]):
        WORKER_PORT += 1
        port = WORKER_PORT

        opts = [
            "--name %s" % format_name(config['domain'], 'worker-%s-%d' % (worker_config["model"], i)),
            "-p %d:%d" % (port, 5678),
            "-e HOST=%s" % IP,
            "-e PORT0=%d" % port,
            "-e MASTER_ADDR=tcp://%s:%d" % (IP, MASTER_TO_WORKER_PORT),
            "-e RECORDINGS_SAVER_ADDR=tcp://%s:%d" % (IP, RECORDINGS_SAVER_PORT),
            "-e MODEL=%s" % worker_config["model"],
        ]

        run_docker(worker_config["image"], config["tag"], opts)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage python run_locally.py config.json"
        sys.exit(1)

    config = json.load(open(sys.argv[1]))
    config["connection_string"] = "mysql://%s:%s@mysql/%s?charset=utf8" % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)

    stop_running_instances(config)

    run_mysql(config)
    run_master(config)
    run_web(config)
    run_api(config)
    run_monitor(config)
    run_recordings_saver(config)

    for worker_config in config["workers"]:
        run_worker(config, worker_config)

