# Puffin
[![Build Status](https://travis-ci.org/loomchild/puffin.svg?branch=master)](https://travis-ci.org/loomchild/puffin)

## Intro

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

Go to [http://localhost:8001](http://localhost:8080) to acces Puffin and 
[http://localhost:8025](http://localhost:8025) to access the emails.

Update docker images:

	docker-compose pull

### Directly on host system

During development it may be more convenient to run Puffin in virtualenv. 

#### Dependencies:

##### Python

First of all make sure that you have Python 3 installed on your system. For example on Debian run:

apt-get install python3 ...

##### Postgres

Puffin also uses Postgresql database, to configure it use:

##### Email

To send emails you can use any SMTP server. For simplicity I recomment [Mailhog]().
First download it:

then run it:

and change mail port before starting Puffin:

    export MAIL_PORT=8025

#### Virtual environment

To create the virtual environment run venv (or pyvenv on Debian):

    venv env

Next activate it:
    
    env/bin/activate

Install runtime and development dependencies:
    
    pip install -r requirements-dev.txt

You might have some problems in the last step, most likely due to missing libraries on your system. 
Read the message carefully and install the development versions of offending library (libxxx-dev on debian).

#### Running

To run puffin:

    ./puffin.py server

If you want to automatically reload the server on any code change, I recommend using [reload](https://github.com/loomchild/reload):

    reload ./puffin.py server

## Configuration

Puffin is configured via environment variables. 

Either set them directly before starting the system:

    export SECRET_KEY=mysupersecretkey

or cofigure them in .env file for Docker Compose 
(see [docker-compose.yml](docker-compose.yml) and [.env](./env) for example).

For a full list of configuration options see [puffin/core/config.py](puffin/core/config.py).

