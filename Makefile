build:
	sudo docker build -t frontend cloudasr/frontend/

run:
	sudo docker run --name frontend -p 8000:8000 -d frontend

stop:
	sudo docker stop frontend
	sudo docker rm frontend
