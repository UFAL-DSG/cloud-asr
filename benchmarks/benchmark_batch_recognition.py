import sys
import time
import grequests
from collections import defaultdict


def make_request(id, wav):
    url = 'http://localhost:8000/recognize?lang=en-towninfo&id=' + str(id)
    headers = {'Content-Type': 'audio/x-wav; rate=44100;'}

    return grequests.post(url, data = wav, headers = headers)

def run_requests(n, batch_size):
    wav = open('resources/test.wav', 'rb').read()
    requests = [make_request(id, wav) for id in range(0, n)]

    return grequests.map(requests, size=batch_size)

def print_statistics(responses):
    responses_by_status = defaultdict(list)
    for response in responses:
        responses_by_status[str(response.status_code)].append(response.elapsed.total_seconds())

    for status_code, responses in responses_by_status.iteritems():
        count = len(responses)
        elapsed_time = sum(responses) / count
        print "%d requests returned %s status code with average elapsed time: %.2f s" % (count, status_code, elapsed_time)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage python benchmarks/benchmark_batch_recognition.py requests batch_size"
        sys.exit(1)

    requests = int(sys.argv[1])
    batch_size = int(sys.argv[2])

    responses = run_requests(requests, batch_size)
    print_statistics(responses)
