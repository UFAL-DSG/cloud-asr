#!/bin/bash

sudo apt-get install -y nginx
sudo cat <<SPEECH-API > /etc/nginx/sites-available/speech-api
server {
	location / {
		proxy_pass http://127.0.0.1:5000;
	}
}
SPEECH-API

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/speech-api /etc/nginx/sites-enabled/speech-api
sudo /etc/init.d/nginx restart


