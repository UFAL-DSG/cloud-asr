import json
import requests

def run_worker_on_marathon(url, login, password, config):
    if url is None:
        return False

    marathon_request = {
        "id": "cloudasr.com/worker-" + config["id"],
        "container": {
            "docker": {
                "image": "ufaldsg/cloud-asr-worker-downloader",
                "portMappings": [{"containerPort": 5678, "hostPort": 0, "protocol": "tcp"}],
                "network": "BRIDGE"
            },
            "type": "DOCKER"
        },
        "env": {
            "MASTER_ADDR": config["master_addr"],
            "RECORDINGS_SAVER_ADDR": config["recordings_saver_addr"],
            "MODEL": config["id"],
            "MODEL_URL": config["model_url"],
        },
        "mem": float(config["mem"]),
        "cpus": float(config["cpu"]),
        "instances": 1
    }

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url + "/v2/apps", data=json.dumps(marathon_request), headers=headers, auth=(login, password))

    return r.status_code == 201
