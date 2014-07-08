import os
import urllib2
import StringIO

basedir = os.path.dirname(os.path.realpath(__file__))
wav = open('%s/../resources/test.wav' % basedir, 'rb').read()

headers = {'Content-Type': 'audio/x-wav; rate=44100;'}
request = urllib2.Request('http://192.168.10.10/recognize', wav, headers)
response = urllib2.urlopen(request).read()

print response

