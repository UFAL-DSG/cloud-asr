CloudASR
========

CloudASR is a software platform and a public ASR webservice. Its three strong features are:
 - automatic scalability with increased workload
 - ease of deployment
 - state-of-the-art incremental speech recognition performance

Platform’s API supports both batch and incremental speech recognition. The batch version is compatible with Google Speech API. New ASR engines can be added onto the platform and work simultaneously.

### Installation
In order to be able to run CloudASR Docker has to be installed on the host machine.
You can follow the instructions for your distribution at [http://docs.docker.com/installation/](http://docs.docker.com/installation/).
Additionally it is necessary to download docker images. You can do that by typing `make pull` - be aware that the images has several GBs.

### Running CloudASR locally
Just type `make run_locally` and everything will be running in a while.
You can open [http://localhost:8001](http://localhost:8001) to see which workers are running.
Additionally, you can open [http://localhost:8000](http://localhost:8000) and try out our interactive web demo.

### Running CloudASR on Mesos cluster
In order to be able to run the CloudASR on Mesos cluster, you have to update `marathon_url` and `master_ip` in the `mesos.json` configuration:
```json
{
    "domain": "cloudasr.com",
    "marathon_url": "localhost:8080",
    "master_ip": "127.0.0.1 - IP of the mesos-slave where the CloudASR master should run",
    "workers": [
        {"image": "ufaldsg/cloud-asr-worker-en-voxforge", "instances": 1},
        {"image": "ufaldsg/cloud-asr-worker-en-wiki", "instances": 1},
        {"image": "ufaldsg/cloud-asr-worker-en", "instances": 1},
        {"image": "ufalgsg/cloud-asr-worker-cs", "instances": 1},
        {"image": "ufaldsg/cloud-asr-worker-cs-alex", "instances": 1}
    ]
}
```
> Note that the suffix of the worker image name corresponds to `lang` parameter used in Batch and Online APIs. For `example ufaldsg/cloud-asr-worker-en` will handle requests with parameter `lang=en`.

After that you can type `make run_mesos` and you should see running instances in the Marathon console in a while. After that you should start a load-balancer on a server associated with the domain specified in the `mesos.json`. You can do that by typing:
```
docker run -p 80:80 -e MARATHON_URL=localhost:8080 -d choko/haproxy
```
After that you should be able to see the demo page on [http://demo.cloudasr.com](http://demo.cloudasr.com) and the monitor page on [http://monitor.cloudasr.com](http://monitor.cloudasr.com).


## How to use CloudASR
CloudASR provides two modes of speech recognition: online recognition and batch recognition.
In the following text we will describe how you can use them.

### Batch API
Batch API is compatible with Google Speech API, but it supports only wav files and json output at this moment.
Users can use parameter `lang` to specify which language they want to use for speech recognition. These language models are available now:
  - **en-voxforge** - English (Voxforge AM+Wikipedia LM)
  - **en-wiki** - English (TED AM+Wikipedia LM)
  - **en-towninfo** - English (VYSTADIAL TownInfo AM+LM)
  - **cs** - Czech (VYSTADIAL AM + Wikipedia LM)
  - **cs-alex** - Czech (VYSTADIAL AM + PTIcs LM)

If you want to transcribe english speech in a `recording.wav` file you can send following curl request:
```
curl -X POST --data-binary @recording.wav --header 'Content-Type: audio/x-wav; rate=16000;' 'http://localhost:8000/recognize?lang=en-towninfo'
```

and you should get a response similiar to this:
```json
{
  "result": [
    {
      "alternative": [
        {
          "confidence": 0.5549500584602356,
          "transcript": "I'M LOOKING FOR A BAR"
        },
        {
          "confidence": 0.14846260845661163,
          "transcript": "I AM LOOKING FOR A BAR"
        },
        {
          "confidence": 0.08276544511318207,
          "transcript": "I'M LOOKING FOR A RESTAURANT"
        },
        {
          "confidence": 0.06668572872877121,
          "transcript": "I AM LOOKING FOR A RESTAURANT"
        }
      ],
      "final": true
    }
  ],
  "result_index": 0
}
```

### Online API
Online API uses Sockets.io for transfering PCM chunks to the CloudASR server. Messages have following format:

#### From Client to Server
  - First we have to start recognition by sending information about used language.
    ```javascript
    socketio.emit('begin', {'lang': 'en-GB'})
    ```
  - After that we can send PCM chunks to the server. Every chunk is a 16 bit PCM array.
    ```javascript
    socketio.emit('chunk',  {'chunk': [128, 123, 15,..., 25], 'frame_rate': 16000})
    ```

  - Finally we end the recognition by sending following message
    ```javascript
    socketio.emit('end', {})
    ```

#### From Server to Client
Server responds to every chunk with a message with interim results:
```json
{
    "status": 0,
    "final": false,
    "result": {
        "hypotheses": [
            {"transcript": "I AM LOOKING"}
        ]
    }
}
```

At the end of the recognition server sends final hypothesis in the following format:
```json
{
    "result": [
        {
            "alternative": [
                {"confidence": 0.5364137887954712, "transcript": "I AM LOOKING FOR A MY"},
                {"confidence": 0.46358612179756165, "transcript": "I'M LOOKING FOR A MY"}
            ],
            "final": true
        }
    ],
    "result_index": 0
}
```

> Note that the Online API will switch from SocketsIO to binary Websockets to decrease the traffic in the near future.

#### Using CloudASR's SpeechRecognition.js library
If you want to use speech recegnition on your website, you can use our javascript library. Please add these scripts to your html:
```html
<script src="http://www.cloudasr.com/js/socket.io.js"></script>
<script src="http://www.cloudasr.com/js/Recorder.js"></script>
<script src="http://www.cloudasr.com/js/SpeechRecognition.js'"></script>
```

Then you can use SpeechRecognition in following manner:
```javascript
var speechRecognition = new SpeechRecognition();
speechRecognition.onStart = function() {
    console.log("Recognition started");
}

speechRecognition.onEnd = function() {
    console.log("Recognition ended");
}

speechRecognition.onError = function(error) {
    console.log("Error occured: " + error);
}

speechRecognition.onResult = function(result) {
    console.log(result);
}

var lang = "en-wiki";
$("#button_start").click(function() {
    speechRecognition.start(lang);
});

$("#button_stop").click(function() {
    speechRecognition.stop()
});
```

You can also take a look at source code of our demo page ([index.html](https://github.com/UFAL-DSG/cloud-asr/blob/master/cloudasr/frontend/templates/index.html), [main.js](https://github.com/UFAL-DSG/cloud-asr/blob/master/cloudasr/frontend/static/js/main.js)).

## Privacy & Terms
All data, including audio recording, is stored for the purpose of ASR quality improvement.
Note that the data can be shared with third parties for both research and commercial purposes.
All collected data will be made available to the ASR community; therefore, do not say anything you do not want
anyone to know about.

The service is available for free. As a result, no guarantees are given regarding the quality of
ASR results. As of now, it is a beta product; thus, things may break and the service may not be
available for large periods of time.

## Contact us
The CloudASR platform is developed by the Dialogue Systems Group at [UFAL](http://ufal.mff.cuni.cz) and the work is funded by the Ministry of Education, Youth and Sports of the Czech Republic under the grant agreement LK11221, by the core research funding of Charles University in Prague. The language resources presented in this work are stored and distributed by the LINDAT/CLARIN project of the Ministry of Education, Youth and Sports of the Czech Republic (project LM2010013).

If you have any questions regarding CloudASR you can reach us at our mailinglist: [cloudasr@googlegroups.com](cloudasr@googlegroups.com).
