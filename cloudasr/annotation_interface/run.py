import os
from lib import create_recordings_saver

saver = create_recordings_saver("tcp://0.0.0.0:5682", "/tmp/data")
saver.run()
