# Contributing

There are many ways you can contribute to Puffin project. 
I hope that everyone will find something for themselves.

## Adding new applications

First see how other applications are configured in [apps/](apps/) directory. 
To add your application simply fork puffin repository and submit a Pull Request with your changes.

There are no clear rules which applications will be accepted as of yet,
but the main conditions are free / open source license and relatively low memory footprint 
(this will be improved in the near future by using optimized database dependency container images).

## Issues

If you find an bug in Puffin, or would like to propose an enhancement, 
please report it via GitHub [Issues](https://github.com/loomchild/puffin/issues).

## Development

For core project organisation we use [Trello](https://trello.com/b/ov1cHTtu). 
For direct communication we use [mailing list](mailto:puffin@librelist.com) mailing list.

## Running your own Puffin

You can run your own clone of puffin for yourself and your friends. 
First you need to do is to is to install Docker on your server.
The easiest way is via Docker Machine [in the cloud](https://docs.docker.com/machine/get-started-cloud/) 
or on [your own server](http://loomchild.net/2015/09/20/your-own-docker-machine/).

Next you need to run Puffin. To do that follow the instructions in [README](README.md#using-docker).
For security reasons make sure to change the SECRET_KEY. 
Keep in mind the software is in early alpha development stage, so it should be used for experimentation only.

## Server

You can donate your own server to host other people's containers. This option is not available yet. 

## Donations

If you'd like to donate money to Puffin to help us maintain our infrastructure and fund the development, 
click on the below button:

[![Gratipay](https://img.shields.io/gratipay/loomchild.svg)](https://gratipay.com/~loomchild/)
