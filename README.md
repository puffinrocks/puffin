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
The easiest way to deploy Puffin and start playing with it is to use Docker.

Create docker machine:

	docker-machine create -d virtualbox dev
	eval "$(docker-machine env dev)"

Deploy Puffin and its dependencies:

	docker-compose up -d

Access Puffin:

	docker-machine ip dev

Take the IP address of your machine and go to [IP]:8080 to access the system and [IP]:8025 to access the emails.
The ports can also be forwarded.

To execute Puffin commands, you can enter the container:

	docker exec -i -t dev_web_1 bash
	./puffin.py db upgrade

Update docker images:

	docker-compose pull
