#!/bin/bash
# This script will prepare a set of hosts for use as a cloud for CloudASR on
# CESNET's MetaCloud platform.
#
# Assumptions:
# - current user can connect to each of these machines as root through ssh

set -e

HOSTS="147.251.9.251 147.251.9.244"
SHIPYARD_HOST="147.251.9.251"

# Stop all containers on the host.
for host in $HOSTS; do
    echo "> Cleaning up: ${host}"
    ssh root@${host} "docker rm -f \`docker ps --no-trunc -aq\`; exit 0"
done

echo "> Setting up ShipYard:"
ssh root@${SHIPYARD_HOST} "docker run -i -t -v /var/run/docker.sock:/docker.sock shipyard/deploy setup"


for host in $HOSTS; do
    echo "> Setting up host: ${host}"

    # Run shipyard agent.
    ssh root@${host} "docker run -d -t -v /var/run/docker.sock:/docker.sock \
        -e IP=${host} \
        -e URL=http://${SHIPYARD_HOST}:8000 -p 4500:4500 shipyard/agent"
done

