import sys
import json
import requests

def master_spec(domain, slave_ip, registry):
    return {
        "id": "master",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-master" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5679, "hostPort": 31000},
                    {"containerPort": 5680, "hostPort": 31001}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "WORKER_ADDR": "tcp://0.0.0.0:5679",
            "FRONTEND_ADDR": "tcp://0.0.0.0:5680",
            "MONITOR_ADDR": "tcp://%s:31002" % slave_ip
        },
        "uris": [],
        "dependencies": ["/%s/monitor" % domain],
        "constraints": [["hostname", "LIKE", slave_ip]]
    }

def monitor_spec(domain, slave_ip, registry):
    return {
        "id": "monitor",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-monitor" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 31003},
                    {"containerPort": 5681, "hostPort": 31002}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MONITOR_ADDR": "tcp://0.0.0.0:5681"
        },
        "uris": [],
        "constraints": [["hostname", "LIKE", slave_ip]]
    }

def frontend_spec(domain, slave_ip, registry):
    return {
        "id": "frontend",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-frontend" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 0}
                ]
            }
        },
        "instances": "2",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MASTER_ADDR": "tcp://%s:31001" % slave_ip
        },
        "uris": [],
        "dependencies": ["/%s/master" % domain]
    }

def worker_spec(domain, slave_ip, registry):
    return {
        "id": "worker",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-worker" % registry,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5678, "hostPort": 0}
                ]
            }
        },
        "instances": "2",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MASTER_ADDR": "tcp://%s:31000" % slave_ip,
            "MODEL": "en-GB"
        },
        "uris": [],
        "dependencies": ["/%s/master" % domain]
    }

def app_spec(domain, slave_ip, registry):
    return {
        "id": domain,
        "apps": [master_spec(domain, slave_ip, registry), monitor_spec(domain, slave_ip, registry), frontend_spec(domain, slave_ip, registry), worker_spec(domain, slave_ip, registry)]
    }

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "Usage python run_on_mesos.py marathon_url domain slave_ip registry_url"
        sys.exit(1)

    marathon_url = sys.argv[1] + "/v2/groups"
    domain = sys.argv[2]
    slave_ip = sys.argv[3]
    registry = sys.argv[4]

    if registry != "":
        registry += "/"

    headers = {'Content-Type': 'application/json'}
    r = requests.put(marathon_url, data=json.dumps(app_spec(domain, slave_ip, registry)), headers=headers)
    print r.json()
