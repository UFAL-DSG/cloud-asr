# Docker cheatsheet

- Run a command in a Docker container
  ```bash
  docker run --rm ubuntu echo Hello world
  ```

- Share a file with a Docker container
  ```bash
  docker run -v /var/log/syslog:/syslog --rm ubuntu tail syslog
  ```

- Run an interactive command inside a Docker container
  ```bash
  docker run -i -t -v /var/log/syslog:/syslog --rm ubuntu tail -f syslog
  ```bash

- Run a deamon command inside a Docker container
  ```bash
  docker run -d --name deamon -v /var/log/syslog:/syslog --rm ubuntu tail -f syslog
  ```

- Kill a running container
  ```bash
  docker kill deamon
  ```

- Kill all running containers
  ```bash
  docker ps -aq | xargs docker kill | xargs docker rm
  ```

- Build a Docker image
  ```bash
  docker build -t ufaldsg/cloud-asr-worker cloudasr/worker
  ```

- Pull a Docker image from a Docker repository
  ```bash
  docker pull ufaldsg/cloud-asr-worker
  ```
