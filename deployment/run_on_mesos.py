import os
import sys
import json
import requests

def master_spec(domain, master_ip, port, registry, tag):
    return {
        "id": "master",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-master:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 5679, "hostPort": port},
                    {"containerPort": 5680, "hostPort": port + 1}
                ]
            }
        },
        "instances": 1,
        "cpus": 0.25,
        "mem": 256,
        "env": {
            "WORKER_ADDR": "tcp://0.0.0.0:5679",
            "API_ADDR": "tcp://0.0.0.0:5680",
            "MONITOR_ADDR": "tcp://%s:%d" % (master_ip, port + 2)
        },
        "dependencies": ["/%s/monitor" % domain],
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def monitor_spec(domain, master_ip, port, registry, tag):
    return {
        "id": "monitor",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-monitor:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 0},
                    {"containerPort": 5681, "hostPort": port + 2}
                ]
            }
        },
        "instances": 1,
        "cpus": 0.25,
        "mem": 256,
        "env": {
            "MONITOR_ADDR": "tcp://0.0.0.0:5681"
        },
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def recordings_spec(domain, master_ip, port, registry, tag, connection_string):
    return {
        "id": "recordings",
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": "%s/ufaldsg/cloud-asr-recordings:%s" % (registry, tag),
                "network": "BRIDGE",
                "portMappings": [
                    {"containerPort": 80, "hostPort": 0},
                    {"containerPort": 5682, "hostPort": port + 5}
                ]
            },
            "volumes": [
                {"containerPath": "/opt/app/static/data", "hostPath": "/mnt/h/cloudasr_recordings", "mode": "RW"}
            ]
        },
        "instances": 1,
        "cpus": 0.25,
        "mem": 256,
        "env": {
            "CONNECTION_STRING": connection_string,
            "STORAGE_PATH": "/opt/app/static/data",
            "DOMAIN": "http://recordings." + domain
        },
        "constraints": [["hostname", "LIKE", master_ip]]
    }

def api_spec(domain, master_ip, port, registry, tag, connection_string):
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
        "instances": 1,
        "cpus": 0.25,
        "mem": 256,
        "env": {
            "CONNECTION_STRING": connection_string,
            "MASTER_ADDR": "tcp://%s:%d" % (master_ip, port + 1),
        },
        "dependencies": ["/%s/master" % domain]
    }

def web_spec(domain, master_ip, port, registry, tag, connection_string, google_login_client_id, google_login_client_secret, ga_tracking_id, marathon_url, marathon_login, marathon_password):
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
        "instances": 1,
        "cpus": 0.25,
        "mem": 256,
        "env": {
            "CONNECTION_STRING": connection_string,
            "GOOGLE_LOGIN_CLIENT_ID": google_login_client_id,
            "GOOGLE_LOGIN_CLIENT_SECRET": google_login_client_secret,
            "GA_TRACKING_ID": ga_tracking_id,
            "API_URL": "http://api." + domain,
            "MARATHON_URL": marathon_url,
            "MARATHON_LOGIN": marathon_login,
            "MARATHON_PASSWORD": marathon_password,
            "MASTER_ADDR": "tcp://%s:%d" % (master_ip, port),
            "RECORDINGS_SAVER_ADDR": "tcp://%s:%d" % (master_ip, port + 5)
        },
        "dependencies": ["/%s/master" % domain]
    }

def worker_spec(domain, master_ip, port, image, model, instances, registry, tag, env, cpu, mem):
    env['MASTER_ADDR'] = "tcp://%s:%d" % (master_ip, port)
    env['RECORDINGS_SAVER_ADDR'] = "tcp://%s:%d" % (master_ip, port + 5)
    env['MODEL'] = model

    return {
        "id": "worker" + model,
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
        "cpus": cpu,
        "mem": mem,
        "env": env,
        "dependencies": [
            "/%s/master" % domain,
            "/%s/recordings" % domain
        ]
    }

def ensure_charset_is_in_connection_string(connection_string):
    if not "charset=utf8" in connection_string:
        print "You have to specify charset=utf8 in your connection string"
        exit()

    return connection_string

def app_spec(config):
    domain = config["domain"]
    master_ip = config["master_ip"]
    port = config.get("port", 31100)
    registry = config.get("registry", "registry.hub.docker.com")
    tag = config.get("tag", "latest")
    connection_string = ensure_charset_is_in_connection_string(config["connection_string"])
    google_login_client_id = config["google_login_client_id"]
    google_login_client_secret = config["google_login_client_secret"]
    ga_tracking_id = config.get("ga_tracking_id", "")

    return {
        "id": domain,
        "apps": [
            master_spec(domain, master_ip, port, registry, tag),
            monitor_spec(domain, master_ip, port, registry, tag),
            recordings_spec(domain, master_ip, port, registry, tag, connection_string),
            api_spec(domain, master_ip, port, registry, tag, connection_string),
            web_spec(domain, master_ip, port, registry, tag, connection_string, google_login_client_id, google_login_client_secret, ga_tracking_id, config["marathon_url"], config["marathon_login"], config["marathon_password"]),
        ] + [
            worker_spec(domain, master_ip, port, worker["image"], worker["model"], worker["instances"], registry, tag, worker.get('env', {}), worker.get('cpu', 0.5), worker.get('mem', 512)) for worker in config["workers"]
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
