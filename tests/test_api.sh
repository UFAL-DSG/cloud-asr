#!/bin/bash

dir=`dirname "$0"`

curl -X POST --data-binary @$dir'/../resources/test.wav' --header 'Content-Type: audio/l16; rate=16000;' 'http://192.168.10.10/recognize'
