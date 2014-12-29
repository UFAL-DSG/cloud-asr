import os
from lib import create_recordings_saver

saver = create_recordings_saver("tcp://0.0.0.0:" + os.environ["PORT0"], "/tmp/data")
saver.run()
