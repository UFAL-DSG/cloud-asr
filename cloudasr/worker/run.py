import os
from lib import create_worker


worker = create_worker(os.environ['MY_ADDR'], os.environ['MASTER_ADDR'])
worker.run()
