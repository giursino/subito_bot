# Automate Your Ad Postings

## About The Project
This project helps to speed-up insertion and filling of advertisements on the website [Subito.it](https://www.subito.it/) and [Facebook Marketplace](https://www.facebook.com/marketplace).

### Built With
* Python
* [Selenium](https://www.selenium.dev/)

### Prerequisites
* Linux
* [Docker](https://www.docker.com/)
* Make

## Setup
Please note, using the Docker container, the local resources are located in the `local/resources` directory and mounted to `resource` container directory.

* create `local/resources` directory coping the contents of `resources` directory
* update `credentials_*.json` with correct credentials
* run `make build` to build the docker image

## Usage
* run `make list` to see the items to publish to subito.it
* run `make add` to add items to the list to publish to subito.it
* run `make update` to update items and images on the list
* run `make restore` to restore items and images to original state
* run `make publish-subito` to publish the items list to subito.it 
* run `make publish-fb` to publish the items list to Facebook Marketplace 

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

### Testing
To run the tests with a specific resources directory `local/resources_test`:

```sh
make TEST=1 list
...
```

## Credits

This project is based on the original [Subito Bot](https://github.com/KennyRotella/subito_bot/commit/633c0d7fd1107e9875cd62e65d169c393ba46ec3) created by [Kenny Rotella](https://github.com/KennyRotella). The project has been improved and adapted to work with Facebook Marketplace by [giursino](https://github.com/giursino). The Docker engineering was also carried out by [giursino](https://github.com/giursino). The functionality for updating advertisements was conceived and developed by [giursino](https://github.com/giursino).

Special thanks to all contributors and the open-source community for their invaluable support and contributions.