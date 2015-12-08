# Puffin
[![Build Status](https://travis-ci.org/loomchild/puffin.svg?branch=master)](https://travis-ci.org/loomchild/puffin)

## Introduction

The goal of the project is to allow average, tech-oriented users to run their own server applications, without worrying about maintaining a server. The ultimate aim is to achieve greater decentralization of federated services, such as social networking, file sharing, blog or email, on the net.

While many other tools are looking at containers as a way to run massive applications, automatically scaling to millions of users, Puffin allows running lightweight applications serving just a single user or a handful of users.

First version is essentially a specialized package manager for Docker, with easy to use interface à la app store. Security will be managed through automatic software updates. Beginners will be able to run containers for free on hardware provided by volunteers, while more demanding users will be able to connect their own machine to run their or their friends' applications.

## Demo

Live demo is available at [puffin.rocks](http://puffin.rocks)

![Puffin Front Page](/doc/screenshot.png?raw=true)

## Deployment

### Using Docker 

The easiest way to deploy Puffin and start playing with it is to use Docker.

Create docker machine:

	docker-machine create -d virtualbox dev
	eval "$(docker-machine env dev)"

Deploy Puffin and its dependencies:

	docker-compose up -d

Go to [http://localhost:8080](http://localhost:8080) to acces Puffin and 
[http://localhost:8025](http://localhost:8025) to access the emails. 
The first things you need to do in Puffin is to register and confirm your email.

Update docker images:

	docker-compose pull

### Deploying directly on host system

During development it may be more convenient to run Puffin in virtualenv. 
All the dependencies can be run via Docker, but the program itself can be run locally.

#### Dependencies:

Make sure that you have Python 3 installed on your system. For example on Debian run:

    apt-get install python3

#### Virtual environment

First of all you need to install it:

    apt-get install python3-venv

then create it:

    pyvenv env

and activate it:
    
    . env/bin/activate

Next you can install runtime and development dependencies:
    
    pip install -r requirements-dev.txt

You might have some problems in the last step, most likely due to missing libraries on your system. 
Read the message carefully and install the development versions of offending library (lib&lt;name&gt;-dev on debian).

#### Run dependencies

Run only dependencies:

    docker-compose run main true

#### Configure dependencies

Create database:

    ./puffin.py db create

Populate database:

    ./puffin.py db upgrade

Start app proxy:

    ./puffin.py machine proxy

#### Run Puffin

Finally to run Puffin execute:

    ./puffin.py server

If you want to automatically reload the server on any code change, I recommend using [reload](https://github.com/loomchild/reload):

    reload ./puffin.py server

### Update /etc/hosts

To access applications from localhost, you need to update your /etc/hosts file, by adding the following lines:

    127.0.1.1 ghost.loomchild.localhost
    127.0.1.1 rocket.chat.loomchild.localhost
    127.0.1.1 owncloud.loomchild.localhost
    127.0.1.1 redmine.loomchild.localhost
    127.0.1.1 wordpress.loomchild.localhost

Each line corresponds to an application, add more if you want to try more applications if needed. 

In production environment you need to configure wildacard DNS record to point to your domain.

## Configuration

Puffin is configured via environment variables. 

Either set them directly before starting the system:

    export SECRET_KEY=mysupersecretkey

or cofigure them in .env file for [Docker Compose](http://docs.docker.com/compose/compose-file/#env-file).

For a full list of configuration options see [puffin/core/config.py](puffin/core/config.py).

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

# License

AGPL, see [LICENSE.txt](LICENSE.txt) for detais.
