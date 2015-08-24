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
            "API_ADDR": "tcp://0.0.0.0:5680",
            "MONITOR_ADDR": "tcp://%s:31102" % master_ip
        },
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
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def recordings_spec(domain, master_ip, registry, tag, connection_string):
    return {
        "id": "recordings",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-recordings:%s" % (registry, tag),
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
            "CONNECTION_STRING": connection_string,
            "STORAGE_PATH": "/opt/app/static/data",
            "DOMAIN": "http://recordings." + domain
        },
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def api_spec(domain, master_ip, registry, tag, connection_string):
    return {
        "id": "api",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-api:%s" % (registry, tag),
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
            "CONNECTION_STRING": connection_string,
            "MASTER_ADDR": "tcp://%s:31101" % master_ip,
        },
        "dependencies": ["/%s/master" % domain]
    }

def web_spec(domain, master_ip, registry, tag, connection_string, google_login_client_id, google_login_client_secret, ga_tracking_id):
    return {
        "id": "www",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-web:%s" % (registry, tag),
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
            "CONNECTION_STRING": connection_string,
            "GOOGLE_LOGIN_CLIENT_ID": google_login_client_id,
            "GOOGLE_LOGIN_CLIENT_SECRET": google_login_client_secret,
            "GA_TRACKING_ID": ga_tracking_id,
            "API_URL": "http://api." + domain,
        },
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
        "mem": "512",
        "env": {
            "MASTER_ADDR": "tcp://%s:31100" % master_ip,
            "RECORDINGS_SAVER_ADDR": "tcp://%s:31105" % master_ip,
            "MODEL": model
        },
        "dependencies": [
            "/%s/master" % domain,
            "/%s/recordings" % domain
        ]
    }

def imageToWorkerName(image):
    import re
    m = re.search('ufaldsg\/cloud-asr-worker-(.*)', image)
    return "worker" + m.group(1).replace('-', '')

def ensure_charset_is_in_connection_string(connection_string):
    if not "charset=utf8" in connection_string:
        print "You have to specify charset=utf8 in your connection string"
        exit()

    return connection_string

def app_spec(config):
    domain = config["domain"]
    master_ip = config["master_ip"]
    registry = config.get("registry", "registry.hub.docker.io")
    tag = config.get("tag", "latest")
    connection_string = ensure_charset_is_in_connection_string(config["connection_string"])
    google_login_client_id = config["google_login_client_id"]
    google_login_client_secret = config["google_login_client_secret"]
    ga_tracking_id = config.get("ga_tracking_id", "")

    return {
        "id": domain,
        "apps": [
            master_spec(domain, master_ip, registry, tag),
            monitor_spec(domain, master_ip, registry, tag),
            recordings_spec(domain, master_ip, registry, tag, connection_string),
            api_spec(domain, master_ip, registry, tag, connection_string),
            web_spec(domain, master_ip, registry, tag, connection_string, google_login_client_id, google_login_client_secret, ga_tracking_id),
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
    login = config.get("marathon_login", None)
    password = config.get("marathon_password", None)

    print app_spec(config)
    r = requests.put(config["marathon_url"] + "/v2/groups", data=json.dumps(app_spec(config)), headers=headers, auth=(login, password))
    print r.json()
