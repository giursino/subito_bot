ifdef TEST
DOCKER_RUN = docker run -it --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(PWD)/local/resources_test:/app/resources" subito_bot
else
DOCKER_RUN = docker run -it --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(PWD)/local/resources:/app/resources" subito_bot
endif

build:
	docker build -t subito_bot .

publish:
	$(DOCKER_RUN) python main.py

list:
	$(DOCKER_RUN) python main.py list

add:
	$(DOCKER_RUN) python main.py add

update:
	$(DOCKER_RUN) python main.py update

shell:
	$(DOCKER_RUN) zsh

clean:
	docker rmi -f subito_bot

rebuild: clean build