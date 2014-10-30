CloudASR
========

CloudASR is a software platform and a public ASR webservice. Its three strong features are:
 - automatic scalability with increased workload
 - ease of deployment
 - state-of-the-art incremental speech recognition performance

Platform’s API supports both batch and incremental speech recognition. The batch version is compatible with Google Speech API. New ASR engines can be added onto the platform and work simultaneously.


Installation
------------
In order to be able to run CloudASR Docker has to be installed on the host machine. You can follow the instructions for your distribution at [http://docs.docker.com/installation/](http://docs.docker.com/installation/)

Running CloudASR
----------------
Just type `make run` and CloudASR will be running in a moment.


Examples
--------
Open [localhost:8000](http://localhost:8000) and try out our interactive demo.
Or you can run `curl -X POST --data-binary @resources/test.wav --header 'Content-Type: audio/x-wav; rate=16000;' 'http:/localhost:8000/recognize'` and you should see a response like this:

```json
{
  "result": [
    {
      "alternative": [
        {
          "confidence": 0.5549500584602356,
          "transcript": "I'M LOOKING FOR A MORE"
        },
        {
          "confidence": 0.14846260845661163,
          "transcript": "I AM LOOKING FOR A MORE"
        },
        {
          "confidence": 0.08276544511318207,
          "transcript": "I'M LOOKING FOR A MODERATE"
        },
        {
          "confidence": 0.06668572872877121,
          "transcript": "I'M LOOKING FOR A MODEL"
        },
        {
          "confidence": 0.06668572872877121,
          "transcript": "I'M LOOKING FOR A MODERN"
        }
      ],
      "final": true
    }
  ],
  "result_index": 0

```
