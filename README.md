# Puffin
[![Build Status](https://travis-ci.org/loomchild/puffin.svg?branch=master)](https://travis-ci.org/loomchild/puffin)

## Introduction

The goal of the project is to allow average, tech-oriented user to run 
web applications with ease. The ultimate aim is to achieve greater decentralization 
of web services, such as social networks, file sharing, blog or email.

While many other tools are looking at containers as a way to run massive 
applications, Puffin concentrates on lightweight ones, each serving just a handful of people.

You can chose to host the applications on Puffin managed platform or on your own server.

## Demo

Live demo platform is available at [puffin.rocks](http://puffin.rocks)

[![Puffin Front Page](/doc/screenshot.png?raw=true)](http://puffin.rocks)

## Architecture
 
Puffin consists of two main components - application catalog and interface that provides 
means to run the applications. Any of them can be used independently - you 
can run the applications from the catalog directly, and you can use the 
interface to run your own applications that are not present in the catalog.

## Technology

Puffin is based on [Docker](https://www.docker.com/) containers and 
for orchestration is uses [Docker Compose](https://docs.docker.com/compose/).

Software is written in [Python 3](https://www.python.org/), 
using [Flask](http://flask.pocoo.org/) web microframework. 
[PosttgreSQL](http://www.postgresql.org/) database is used to store the data.
[Nginx](http://nginx.org/) is used as a reverse proxy.

## Deployment

### Demo deployment

The easiest way to deploy Puffin and start playing with it to use 
[Docker Compose](https://docs.docker.com/compose/):

	docker-compose up -d

Go to [http://localhost:8080](http://localhost:8080) to acces Puffin. 
Log In as user "puffin", password "puffin". Alternatively you can register 
your own user and confirm the email address via 
[http://localhost:8025](http://localhost:8025). 

To rebuild the code:

    docker-compose build

### Private deployment

To deploy Puffin for private needs, for a single user or a limited number of users, 
use docker-compose-single.yml file. In an initial form it will deploy on locahost:

    docker-compose -f docker-compose-single.yml up -d
 
If you want to run it on a server then copy the configuration file and
set SERVER_NAME, VIRTUAL_HOST and SECRET_KEY environment variables.

In this configuration users can't register themselves and no confirmation 
email will be sent. Log in as user "puffin", password "puffin" (make sure to change the password
after you login). 

You can create new users using Puffin console. First enter the container:
    
    docker exec -it puffin_main_1 bash

then execute puffin command:

    ./puffin.py user create \<login>

The initial password is the same as login, so it should be changed
by the account owner.

### Public deployment

To deploy Puffin for public use, so anyone can register to access it, use 
docker-compose-multi.yml file. In an initial form it will deploy on locahost:

    docker-compose -f docker-compose-multi.yml up -d
 
If you want to run it on a server then copy the configuration file and
set SERVER_NAME, VIRTUAL_HOST, SECRET_KEY and MAIL\_\* environment variables.
Also make sure to change the default "puffin" user password.

### Development deployment directly on host system

During development it's more convenient to run Puffin in virtualenv. 
You can still run all dependencies via Docker, but execute Puffin 
directly on the host system.

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
Read the message carefully and install the development versions of offending library 
(usually lib&lt;name&gt;-dev on Debian).

#### Run dependencies

Run dependencies, such as database and mail server, and configure them:

    docker-compose -f docker-compose-deps.yml up -d

#### Run Puffin

Finally run Puffin:

    ./puffin.py server

If you want to automatically reload the server on any code change, 
I recommend using [reload](https://github.com/loomchild/reload):

    reload ./puffin.py server

### Set-up DNS

To access applications from localhost you need to set-up DNS. 
On public server you need to configure wildacard DNS record to point to your domain.
On localhost there are two alternative solutions to this problem: 
set up a local DNS server or update /etc/hosts file.

#### Set-up local DNS server using dnsmasq

First install dnsmasq and use the following configuration file 
(on Debian create a new file in /etc/dnsmasq.d/): 
    
    address=/localhost/127.0.0.1

Next configure your nameservers in resolv.conf by adding the following line at the beginning 
(caution - this file is often overwritten by other programs such as NetworkManager - 
refer to their documentation on how to preserve this setting):

    nameserver 127.0.0.1

#### Update /etc/hosts

Update your /etc/hosts file, by adding the following lines:

    127.0.1.1 ghost.puffin.localhost
    127.0.1.1 rocket.chat.puffin.localhost
    127.0.1.1 owncloud.puffin.localhost
    127.0.1.1 redmine.puffin.localhost
    127.0.1.1 wordpress.puffin.localhost
    127.0.1.1 gogs.puffin.localhost

Each line corresponds to an application and user, add more if you want to try more applications. 

### Docker Machine

If you can't use docker directly on your system or would like to deploy 
Puffin on a remote server, [Docker Machine](https://docs.docker.com/machine/) comes in handy.

You can easily install Docker [in the cloud](https://docs.docker.com/machine/get-started-cloud/) 
or on [your own server](http://loomchild.net/2015/09/20/your-own-docker-machine/).

To create and activate a local Docker virtual machine, run:

	docker-machine create -d virtualbox dev
	eval "$(docker-machine env dev)"

After that all subsequent Docker commands will be executed in a virtual machine. 
Keep in mind that you'll need to use IP address or hostname of the machine 
to access Puffin, instead of locahost.

## Configuration

Puffin is configured via environment variables. 

Either set them directly before starting it:

    export SECRET_KEY=mysupersecretkey

or cofigure them in Docker Compose file.

For a full list of configuration options see [puffin/core/config.py](puffin/core/config.py).

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

# License

AGPL, see [LICENSE.txt](LICENSE.txt) for detais.
