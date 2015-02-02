import os
import sys
import json
import requests

def master_spec(domain, master_ip, registry, tag):
    return {
        "id": "master",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-master:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5679, "hostPort": 31100},
                    {"containerPort": 5680, "hostPort": 31101}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "WORKER_ADDR": "tcp://0.0.0.0:5679",
            "FRONTEND_ADDR": "tcp://0.0.0.0:5680",
            "MONITOR_ADDR": "tcp://%s:31102" % master_ip
        },
        "uris": [],
        "dependencies": ["/%s/monitor" % domain],
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def monitor_spec(domain, master_ip, registry, tag):
    return {
        "id": "monitor",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-monitor:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 31103},
                    {"containerPort": 5681, "hostPort": 31102}
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

def annotation_interface_spec(domain, master_ip, registry, tag):
    return {
        "id": "annotation",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-annotation-interface:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 31104},
                    {"containerPort": 5682, "hostPort": 31105}
                ]
            },
            "volumes": [
                {"containerPath": "/opt/app/static/data", "hostPath": "/home/data", "mode": "RW"}
            ]
        },
        "instances": "1",
        "cpus": "0.25",
        "mem": "256",
        "env": {
	        "GOOGLE_LOGIN_CLIENT_ID": os.environ["CLOUDASR_GOOGLE_LOGIN_CLIENT_ID"],
	        "GOOGLE_LOGIN_CLIENT_SECRET": os.environ["CLOUDASR_GOOGLE_LOGIN_CLIENT_SECRET"]
        },
        "uris": [],
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def frontend_spec(domain, master_ip, registry, tag):
    return {
        "id": "demo",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-frontend:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 0}
                ]
            }
        },
        "instances": "1",
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MASTER_ADDR": "tcp://%s:31101" % master_ip,
        },
        "uris": [],
        "dependencies": ["/%s/master" % domain]
    }

def worker_spec(domain, master_ip, image, model, instances, registry, tag):
    return {
        "id": imageToWorkerName(image),
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/%s:%s" % (registry, image, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5678, "hostPort": 0}
                ]
            }
        },
        "instances": instances,
        "cpus": "0.25",
        "mem": "256",
        "env": {
            "MASTER_ADDR": "tcp://%s:31100" % master_ip,
            "RECORDINGS_SAVER_ADDR": "tcp://%s:31105" % master_ip,
            "MODEL": model
        },
        "uris": [],
        "dependencies": [
            "/%s/master" % domain,
            "/%s/annotation" % domain
        ]
    }

def imageToWorkerName(image):
    import re
    m = re.search('ufaldsg\/cloud-asr-worker-(.*)', image)
    return "worker" + m.group(1).replace('-', '')

def app_spec(config):
    domain = config["domain"]
    master_ip = config["master_ip"]
    registry = config.get("registry", "registry.hub.docker.io")
    tag = config.get("tag", "latest")

    return {
        "id": domain,
        "apps": [
            master_spec(domain, master_ip, registry, tag),
            monitor_spec(domain, master_ip, registry, tag),
            annotation_interface_spec(domain, master_ip, registry, tag),
            frontend_spec(domain, master_ip, registry, tag),
        ] + [
            worker_spec(domain, master_ip, worker["image"], worker["model"], worker["instances"], registry, tag) for worker in config["workers"]
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
