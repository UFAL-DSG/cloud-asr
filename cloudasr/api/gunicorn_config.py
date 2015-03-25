bind = '0.0.0.0:80'
worker_class = 'socketio.sgunicorn.GeventSocketIOWorker'
max_requests = 1000
