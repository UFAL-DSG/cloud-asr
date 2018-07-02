bind = '0.0.0.0:80'
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
max_requests = 1000
workers = 1