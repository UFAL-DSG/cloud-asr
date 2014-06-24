#!/bin/bash

sudo pip install supervisor
sudo ln -s /vagrant/supervisord.conf /etc/supervisord.conf

sudo cat <<EOF > /etc/init/supervisord.conf
description     "supervisord"

start on vagrant-mounted
stop on runlevel [016]

pre-start script
        echo \$MOUNTPOINT >> /var/run/mount.log
        [ \$MOUNTPOINT = "/vagrant" ] && touch /var/run/vagrant_mounted
        [ \$MOUNTPOINT = "/var/www/speech-api" ] && touch /var/run/api_mounted

        [ -f /var/run/vagrant_mounted -a -f /var/run/api_mounted ] || stop
end script

respawn

exec /usr/local/bin/supervisord --nodaemon --configuration /etc/supervisord.conf
EOF

sudo start supervisord
