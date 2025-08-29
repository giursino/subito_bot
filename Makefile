ifdef TEST
DOCKER_RUN = docker run -it --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(PWD)/local/resources_test:/app/resources" subito_bot
else
DOCKER_RUN = docker run -it --rm -e DISPLAY=$(DISPLAY) -v /tmp/.X11-unix:/tmp/.X11-unix -v "$(PWD)/local/resources:/app/resources" subito_bot
endif

build: ## Build the Docker image
	docker build -t subito_bot .

publish-subito: ## Publish advertisements to Subito
	$(DOCKER_RUN) python main.py publish subito

publish-fb: ## Publish advertisements to Facebook
	$(DOCKER_RUN) python main.py publish fb

list: ## List all advertisements
	$(DOCKER_RUN) python main.py list

add: ## Create a new advertisement
	$(DOCKER_RUN) python main.py add

update: ## Update advertisements with a new SKU
	$(DOCKER_RUN) python main.py update

restore: ## Restore advertisements to original state
	$(DOCKER_RUN) python main.py restore

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

shell: ## Open a shell in the container for debugging
	$(DOCKER_RUN) zsh

clean: ## Clean the Docker image
	docker rmi -f subito_bot

rebuild: clean build ## Rebuild the Docker image