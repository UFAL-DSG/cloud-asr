FROM ufaldsg/cloud-asr-base

MAINTAINER Ondrej Klejch

RUN pip install flask flask-socketio flask-sqlalchemy Werkzeug==0.9.6 gunicorn==19.1.1

ADD . /opt/app
WORKDIR /opt/app
CMD while true; do gunicorn -c gunicorn_config.py run:app; done
