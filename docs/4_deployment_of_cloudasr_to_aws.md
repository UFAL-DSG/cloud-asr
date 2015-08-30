# Deployment of CloudASR to AWS
In this article we will describe how to deploy CloudASR to AWS.

- Start Mesos Cluster in AWS.
  Go to [https://mesosphere.com/amazon/setup](https://mesosphere.com/amazon/setup) and follow the instructions.

- Create MySQL Database.
  Create MySQL instance with [https://eu-central-1.console.aws.amazon.com/rds/home](https://eu-central-1.console.aws.amazon.com/rds/home) and run command:
  ```bash
  cat schema.sql | docker run -i --rm -a stdin -a stdout mysql mysql --host MYSQL_URL --port MYSQL_PORT --user=USER --password=PASSWORD cloudasr
  ```

- Start CloudASR.
  Edit `cloudasr.json` and  run`make run_on_mesos`.
  ```json
  {
      "domain": "cloudasr.aws",
      "registry": "registry.hub.docker.com",
      "tag": "17",
      "marathon_url": "MARATHON_ADDRESS",
      "marathon_login": "",
      "marathon_password": "",
      "master_ip": "MASTER_ADDRESS",
      "connection_string": "mysql://cloudasr:cloudasr@MYSQL_ADDRESS/cloudasr?charset=utf8",
      "google_login_client_id": "",
      "google_login_client_secret": "",
      "ga_tracking_id": "",
      "workers": [
          {"image": "ufaldsg/cloud-asr-worker-en-towninfo", "model": "en-towninfo", "instances": 1}
      ]
  }
  ```

- Run HaProxy.
  ```bash
  curl -X POST -H "Content-type: application/json"  "http://MARATHON_URL/v2/apps" -d '{
  	"id": "haproxy",
  	"constraints": [["hostname", "UNIQUE"]],
  	"acceptedResourceRoles": ["slave_public"],
  	"container": {
  		"docker": {
  			"portMappings": [{"containerPort": 80, "hostPort": 80, "protocol": "tcp"}],
  			"image": "choko/haproxy",
  			"network": "BRIDGE"
  		},
  		"type": "DOCKER"
  	},
  	"env": {
  		"MARATHON_URL": "MARATHON_URL",
  		"MARATHON_LOGIN": "",
  		"MARATHON_PASSWORD": ""
  	},
  	"mem": 256,
  	"cpus": 1,
  	"instances": 1
  }'
  ```

- Edit /etc/hosts.
  Because we didn't setup DNS name for CloudASR, we can mimic that with /etc/hosts file. Put the following lines to the file and replace `127.0.0.1` with IP address of the public slave.
  ```
  127.0.0.1   www.cloudasr.aws
  127.0.0.1   api.cloudasr.aws
  127.0.0.1   recordings.cloudasr.aws
  127.0.0.1   monitor.cloudasr.aws
  ```

- Try it out.
  Go to [http://www.cloudasr.aws/demo](http://www.cloudasr.aws/demo) and try the demo.
