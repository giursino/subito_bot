DOCKER_RUN = docker run -it --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(PWD)/local/resources:/app/resources" subito_bot

build:
	docker build -t subito_bot .

publish:
	$(DOCKER_RUN) python main.py

list:
	$(DOCKER_RUN) python main.py list

add:
	$(DOCKER_RUN) python main.py add

shell:
	$(DOCKER_RUN) zsh