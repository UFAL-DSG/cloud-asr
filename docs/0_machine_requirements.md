Your machine requirements
=========================
- 60GB of memory
- 8GB of RAM
- 4 cores minimum 8 cores recommended


OSX docker-machine
~~~~~~~~~~~~~~~~~~
Example command to create local VirtualBox machine

```
docker-machine create --driver virtualbox --virtualbox-cpu-count "8" --virtualbox-memory 8192 --virtualbox-disk-size "60000" dev2
```
