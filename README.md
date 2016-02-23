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

### Demo deployment

The easiest way to deploy Puffin and start playing with it is to use Docker.

Deploy Puffin and its dependencies:

	docker-compose up -d

Go to [http://localhost:8080](http://localhost:8080) to acces Puffin.
Alternatively, you should be able to drop the port number, 
once the proxy starts up. 

After that you should be able to log as user puffin, password puffin.
Alternatively you can register your new user and confirm email.
[http://localhost:8025](http://localhost:8025) to access the emails. 

Update docker images:

	docker-compose pull

### Single-user deployment

To deploy Puffin for a single user, you can use docker-compose-single.yml 
file as a template. In an initial form it will deploy on locahost:

    docker-compose -f docker-compose-single.yml up -d
 
You need to copy it and change SERVER_NAME, VIRTUAL_HOST and SECRET_KEY
environment variables.

There is no email server configured and you can't register new users. 
If you want to run it on a public server, make sure to change the default
password.

### Multi-user deployment

To deploy Puffin for many users and allow registration, 
you can use docker-compose-multi.yml file as a template. 
In an initial form it will deploy on locahost:

    docker-compose -f docker-compose-multi.yml up -d
 
You need to copy it and change SERVER_NAME, VIRTUAL_HOST and SECRET_KEY
and MAIL_* environment variables.

Default user is created, so if you want to run it on a public server 
make sure to change the default password.

### Development deployment directly on host system

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

Run only dependencies and configure them:

    docker-compose -f docker-compose-deps.yml up -d

#### Run Puffin

Finally to run Puffin execute:

    ./puffin.py server

If you want to automatically reload the server on any code change, I recommend using [reload](https://github.com/loomchild/reload):

    reload ./puffin.py server

### Set-up DNS

To access applications from localhost you need to set-up DNS. There are two alternative solutions to this problem.
In production environment you need to configure wildacard DNS record to point to your domain.

#### Use dnsmasq

Install dnsmasq and add the following to its config file: 
    
    address=/localhost/127.0.0.1

Configure your nameservers in resolv.conf to include this line at the beginning 
(caution - this file is often overwritten by other programs, NetworkManager among others - 
refer to their documentation on how to preserve this setting):

    nameserver 127.0.0.1

#### Update /etc/hosts

Update your /etc/hosts file, by adding the following lines:

    127.0.1.1 ghost.<your-login>.localhost
    127.0.1.1 rocket.chat.<your-login>.localhost
    127.0.1.1 owncloud.<your-login>.localhost
    127.0.1.1 redmine.<your-login>.localhost
    127.0.1.1 wordpress.<your-login>.localhost

Each line corresponds to an application, add more if you want to try more applications if needed. 

### Docker Machine

If you can't use docker directly on your system or would like to deploy 
Puffin on a remote server, you can use Docker Machine.

For example to create a local Boot2Docker virtual machine, run:

	docker-machine create -d virtualbox dev
	eval "$(docker-machine env dev)"

After that you should be able to start Puffin. 
Keep in mind that you'll need to use IP address or hostnmae of the machine 
to access it, instead of locahost.

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
