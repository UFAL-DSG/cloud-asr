#!/bin/bash

set -e # Stop on any error

# --------------- SETTINGS ----------------
# Other settings
export DEBIAN_FRONTEND=noninteractive

sudo apt-get update
sudo apt-get install -y sox git python-dev python-pip python-setuptools libatlas-base-dev portaudio19-dev build-essential
sudo pip install cython pyyaml pystache flask

# install pyaudio
pushd /tmp
wget http://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_amd64.deb
sudo dpkg -i python-pyaudio_0.2.8-1_amd64.deb
popd # /tmp

if [ ! -f ~/runonce ]
then
  echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
  echo 'export LC_ALL="$LANG"' >> ~/.bashrc
  echo 'export LANGUAGE="$LANG"' >> ~/.bashrc

  # have to reboot for drivers to kick in, but only the first time of course
  sudo reboot
  touch ~/runonce
fi
