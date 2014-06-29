#!/bin/bash

sudo sh -c 'echo "deb http://ppa.launchpad.net/nginx/stable/ubuntu lucid main" > /etc/apt/sources.list.d/nginx-stable-lucid.list'
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C
sudo apt-get update
sudo apt-get install -y nginx
sudo cat <<SPEECH-API > /etc/nginx/sites-available/speech-api
server {
	location / {
		proxy_pass http://127.0.0.1:5000;
	}

	location /socket.io {
		proxy_pass http://127.0.0.1:5000;

		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
	}

}
SPEECH-API

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/speech-api /etc/nginx/sites-enabled/speech-api
sudo /etc/init.d/nginx restart


