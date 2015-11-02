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
            "MASTER_ADDR": "tcp://alex.ms.mff.cuni.cz:31000",
            "RECORDINGS_SAVER_ADDR": "tcp://alex.ms.mff.cuni.cz:31005",
            "MODEL": config["id"],
            "MFCC_CONF_URL": config["mfcc.conf"],
            "TRI2B_BMMI_MDL_URL": config["tri2b.mdl"],
            "TRI2B_BMMI_MAT_URL": config["tri2b.mat"],
            "HCLG_TRI2B_BMMI_FST_URL": config["hclg.fst"],
            "WORDS_TXT_URL": config["words.txt"],
            "CONFIG_PY_URL": config["config.py"]
        },
        "mem": 2048,
        "cpus": 0.25,
        "instances": 1
    }

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url + "/v2/apps", data=json.dumps(marathon_request), headers=headers, auth=(login, password))

    return r.status_code == 201
