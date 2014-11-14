import os
from lib import create_worker


worker = create_worker(os.environ['MODEL'], os.environ['HOST'], os.environ['PORT0'], os.environ['MASTER_ADDR'])
worker.run()
