import os
from lib import create_worker


worker = create_worker(os.environ['MY_ADDR'])
worker.run()
