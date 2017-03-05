# Puffin
[![Build Status](https://travis-ci.org/puffinrocks/puffin.svg?branch=master)](https://travis-ci.org/puffinrocks/puffin)

## Introduction

The goal of the project is to allow average, tech-oriented user to run web applications with ease. 
The idea is to create an easy to host, technology agnostic private cloud.
The ultimate aim is to achieve greater decentralization of web services, such as social networks, 
file sharing, blog or email.

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

### Local deployment

#### Set-up DNS

To access installed applications from localhost you need to set-up local DNS. 
There are many alternative solutions to this problem, the simplest one is to 
add the following lines at the top of your /etc/resolv.conf file:

    nameserver 127.0.0.1
    options ndots:0

Which can be done by executing the following command as root:

    echo -e "nameserver 127.0.0.1\noptions ndots:0\n$(cat /etc/resolv.conf)" > /etc/resolv.conf

Make sure that you disable your other local DNS server, such as dnsmasq, 
before running Puffin.

#### Clone git repository

Puffin application catalog is stored as git submodules. When cloning the repo 
make sure to use --recursive option:

    git clone --recursive git@github.com:puffinrocks/puffin.git

Or if you have already cloned the repo then update the submodules in it:

    git submodule update --init --recursive

#### Run Puffin

Clone the repository and use [Docker Compose](https://docs.docker.com/compose/):

    docker-compose up

Go to [http://puffin.localhost](http://puffin.localhost) to access Puffin.
Log In as user "puffin", password "puffin". 
Emails sent from Puffin are accessible via embedded Mailhog server at 
[http://mailhog.localhost](http://mailhog.localhost).

If [http://puffin.localhost](http://puffin.localhost) is not accessible you can 
try connecting to Puffin via a port: [http://localhost:8080](http://localhost:8080).
However, without DNS configured correctly, you won't be able to access the apps. 

Puffin server is automatically reloaded on every code change thanks 
to [reload](https://github.com/loomchild/reload). 
To rebuild the code after making more substantial change, such as modifying 
dependencies, run:

    docker-compose build

Puffin contains several convenience commands to upgrade the database, 
manage users, execute internal shell, etc. To get a complete list, run:

    docker-compose run puffin --help

### Production deployment

#### Configuration

To deploy Puffin for private needs, for a single user or a limited number of users, 
use [docker-compose-example.yml](./docker-compose-example.yml) file as a basis:

    cp docker-compose-example.yml docker-compose-production.yml

You need to change SERVER_NAME and VIRTUAL_HOST variables to point to your domain. 
You also need to set SECRET_KEY variable to a random value. 

For a full list of configuration options see [puffin/core/config.py](puffin/core/config.py).

#### Email

To send emails from Puffin and the applications you need to configure few environment variables 
before starting Puffin. It's probably easiest to register to an external email service to avoid 
being classified as spammer. The variables are (not all are obligatory, see 
[puffin/core/config.py](puffin/core/config.py) for more details):

    MAIL_SERVER
    MAIL_PORT
    MAIL_USE_TLS
    MAIL_USE_SSL
    MAIL_USERNAME
    MAIL_PASSWORD
    MAIL_DEFAULT_SENDER
    MAIL_SUPPRESS_SEND

#### Set-up DNS

On public server you need to configure wildacard DNS record to point to your 
root domain and all its subdomains.

#### Docker Machine

If you would like to deploy Puffin on a remote server, Docker Machine comes in handy.
You can easily install Docker [in the cloud](https://docs.docker.com/machine/get-started-cloud/) 
or on [your own server](http://loomchild.net/2015/09/20/your-own-docker-machine/).

To instruct Docker to interact with remote server run:

    eval "$(docker-machine env [machine-name])"

#### Run Puffin

Finally you can run Puffin:

    docker-compose -f docker-compose-production.yml up -d

#### Configure users

Initially only "puffin" user with "puffin" password will be created - make 
sure to change the password before exposing puffin to the outside world. 
Later you can either allow other users to register themselves on your platform 
(via SECURITY_REGISTERABLE=True config setting) or create them manually:

    docker-compose run puffin user create [login]

(The password will be the same as login, so it should be changed as soon as 
possible.)

#### Clustering

Clustering is currently not supported, but you may run apps on a separate 
machine than Puffin server itself. To achieve that take a look on MACHINE\_\* options. 
You also won't need network sections in your docker-compose file, 
since the networks will be created automatically on the remote machine.

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

# Changelog

See [CHANGELOG.md](CHANGELOG.md).

# License

AGPL, see [LICENSE.txt](LICENSE.txt) for details.
