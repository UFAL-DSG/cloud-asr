import urllib2
import json

def recognize_wav(data):
    baseurl = "http://www.google.com/speech-api/v2/recognize?lang=%s&maxresults=%d&key=%s" % (
        'cs', 5, 'PRIVATE KEY')
    header = {"Content-Type": "audio/l16; rate=%d" % 16000}

    request = urllib2.Request(baseurl, data, header)
    json_hypotheses = urllib2.urlopen(request).read()

    hypotheses = json.loads('{"result":[]}')
    for h in json_hypotheses.splitlines():
        if '"final":true' in h:
            hypotheses = json.loads(h)

    return hypotheses
