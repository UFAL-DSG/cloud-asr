import sys
import json
import requests

def master_spec(domain, master_ip, registry):
    return {
        "id": "master",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-master:latest" % registry,
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
            "MONITOR_ADDR": "tcp://%s:31002" % master_ip
        },
        "uris": [],
        "dependencies": ["/%s/monitor" % domain],
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def monitor_spec(domain, master_ip, registry):
    return {
        "id": "monitor",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-monitor:latest" % registry,
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
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def frontend_spec(domain, master_ip, registry):
    return {
        "id": "demo",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%sufaldsg/cloud-asr-frontend:latest" % registry,
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
            "MASTER_ADDR": "tcp://%s:31001" % master_ip,
        },
        "uris": [],
        "dependencies": ["/%s/master" % domain]
    }

def worker_spec(master_name, master_ip, image, instances):
    return {
        "id": imageToWorkerName(image),
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": image,
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5678, "hostPort": 0}
                ]
            },
            "volumes": [
                {"containerPath": "/tmp/data", "hostPath": "/tmp/data", "mode": "RW"}
            ]
        },
        "instances": instances,
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MASTER_ADDR": "tcp://%s:31000" % master_ip
        },
        "uris": [],
        "dependencies": [master_name]
    }

def imageToWorkerName(image):
    import re
    m = re.search('ufaldsg\/cloud-asr-worker-(.*)', image)
    return "worker" + m.group(1).replace('-', '')

def app_spec(config):
    domain = config["domain"]
    master_ip = config["master_ip"]
    registry = config.get("registry", "")
    master_name = "/%s/master" % domain

    return {
        "id": domain,
        "apps": [
            master_spec(domain, master_ip, registry),
            monitor_spec(domain, master_ip, registry),
            frontend_spec(domain, master_ip, registry),
        ] + [
            worker_spec(master_name, master_ip, registry + worker["image"], worker["instances"]) for worker in config["workers"]
        ]
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage python run_on_mesos.py mesos.json"
        sys.exit(1)

    config = json.load(open(sys.argv[1]))
    headers = {'Content-Type': 'application/json'}
    print app_spec(config)
    r = requests.put(config["marathon_url"] + "/v2/groups", data=json.dumps(app_spec(config)), headers=headers)
    print r.json()
