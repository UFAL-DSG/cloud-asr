#!/bin/bash

dir=`dirname "$0"`

curl -X POST --data-binary @$dir'/../resources/test.wav' --header 'Content-Type: audio/l16; rate=16000;' 'http://127.0.0.1:5000/recognize'
