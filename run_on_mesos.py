import sys
import json
import requests

def master_spec(ip, registry):
    return {
        "id": "master",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-master" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5679, "hostPort": 31000},
                    {"containerPort": 5680, "hostPort": 31001}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.5",
        "mem": "512",
        "env": {
            "WORKER_ADDR": "tcp://0.0.0.0:5679",
            "FRONTEND_ADDR": "tcp://0.0.0.0:5680",
            "MONITOR_ADDR": "tcp://%s:31002" % ip
        },
        "uris": [],
        "dependencies": ["/cloudasr/monitor"]
    }

def monitor_spec(ip, registry):
    return {
        "id": "monitor",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-monitor" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5681, "hostPort": 31002},
                    {"containerPort": 8001, "hostPort": 31003}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.5",
        "mem": "512",
        "env": {
            "MONITOR_ADDR": "tcp://0.0.0.0:5681"
        },
        "uris": []
    }

def frontend_spec(ip, registry):
    return {
        "id": "frontend",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-frontend" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 8000, "hostPort": 31004}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.5",
        "mem": "512",
        "env": {
            "MASTER_ADDR": "tcp://%s:31001" % ip
        },
        "uris": [],
        "dependencies": ["/cloudasr/master"]
    }

def worker_spec(ip, registry):
    return {
        "id": "worker",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-worker" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5678, "hostPort": 31005}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.5",
        "mem": "512",
        "env": {
            "MASTER_ADDR": "tcp://%s:31000" % ip,
            "HOSTNAME": ip,
            "PORT": 31005,
            "MODEL": "en-GB"
        },
        "uris": [],
        "dependencies": ["/cloudasr/master"]
    }

def app_spec(ip, registry):
    return {
        "id": "cloudasr",
        "apps": [master_spec(ip, registry), monitor_spec(ip, registry), frontend_spec(ip, registry), worker_spec(ip, registry)]
    }

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage python run_on_mesos.py marathon_url server_ip registry_url"
        sys.exit(1)

    marathon_url = sys.argv[1] + "/v2/groups"
    ip = sys.argv[2]
    registry = sys.argv[3]
    headers = {'Content-Type': 'application/json'}
    r = requests.put(marathon_url, data=json.dumps(app_spec(ip, registry)), headers=headers)
    print r.json()
