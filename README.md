# Subito Bot

## About The Project
This project helps to speed-up insertion and filling of advertisements on the website [Subito.it](https://www.subito.it/)

### Built With
* [Selenium](https://www.selenium.dev/)

### Prerequisites
* Linux
* [Docker](https://www.docker.com/)
* Make

## Setup
* rename `credentials.json.template` file to `credentials.json` and update it with correct credentials
* run `make build` to build the docker image

## Usage
* run `make list` to see the items to publish to subito.it
* run `make add` to add items to the list to publish to subito.it
* run `make update` to update items and images on the list
* run `make publish` to publish the items list to subito.it 

## Development

To enter on container shell:

```sh
make shell
```

Usage:

```sh
pip install -r requirements.txt
python main.py [list|add]
```