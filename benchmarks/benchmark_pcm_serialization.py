import os
import wave
import base64
import struct
import json
from pcm_messages_pb2 import bytes_serialization, array_serialization

def serialize_via_json_array(frames):
    return [struct.unpack('h', frames[i:i+2])[0] for i in range(0, len(frames), 2)]

def serialize_via_base64(frames):
    return base64.b64encode(frames)

def serialize_via_utf8(frames):
    pcm = [struct.unpack('H', frames[i:i+2])[0] for i in range(0, len(frames), 2)]
    data = []
    for p in pcm:
        data.append(unichr(p & 255))
        data.append(unichr(p >> 8))

    return ''.join(data)

def format_json_message(serialize):
    def callback(frames):
        message = {'chunk': serialize(frames), 'frame_rate': 44100}
        return json.dumps(message)

    return callback

def serialize_via_bytes_protobuf(frames):
    message = bytes_serialization()
    message.body = frames
    message.frame_rate = 44100

    return message.SerializeToString()

def serialize_via_array_protobuf(frames):
    pcm = [struct.unpack('H', frames[i:i+2])[0] for i in range(0, len(frames), 2)]

    message = array_serialization()
    message.body.extend(pcm)
    message.frame_rate = 44100

    return message.SerializeToString()

def chunks():
    basedir = os.path.dirname(os.path.realpath(__file__))
    wav = wave.open("%s/../resources/test.wav" % basedir, "rb")

    while True:
        frames = wav.readframes(512)
        if len(frames) == 0:
            break

        yield frames

serializers = [
    ('frames', format_json_message(lambda x: ' ' * len(x))),
    ('bytes_protobuf', serialize_via_bytes_protobuf),
    ('base64', format_json_message(serialize_via_base64)),
    ('array_protobuf', serialize_via_array_protobuf),
    ('json_array', format_json_message(serialize_via_json_array)),
    ('utf8', format_json_message(serialize_via_utf8)),
]

for (name, serialize) in serializers:
    total_length = 0

    for chunk in chunks():
        message = serialize(chunk)
        total_length += len(message)

    print "%15s\t%d" % (name, total_length)

