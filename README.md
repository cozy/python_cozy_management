## Description

Helper to manage self hosting cozy

## Install / Hack

Get build dependencies

    sudo apt-get install python python-pip python-dev python-requests

Setup your virtual environment:

    sudo pip install virtualenv
    virtualenv virtualenv
    . virtualenv/bin/activate

Install dependencies:

    pip install -r requirements/common.txt

## Contribution

* Pick and solve an [issue](https://github.com/cozy/python_cozy_management/issues)

## Tests

[![Build
Status](https://travis-ci.org/cozy/python_cozy_management.png?branch=master)](https://travis-ci.org/cozy/python_cozy_management)

Install development dependencies

    pip install -r requirements/dev.txt

Run tests

    lettuce tests

## License

Python Cozy management is developed by Cozy Cloud and distributed under the AGPL v3 license.

## What is Cozy?

![Cozy Logo](https://raw.github.com/cozy/cozy-setup/gh-pages/assets/images/happycloud.png)

[Cozy](http://cozy.io) is a platform that brings all your web services in the
same private space.  With it, your web apps and your devices can share data
easily, providing you with a new experience. You can install Cozy on your own
hardware where no one profiles you. 

## Community 

You can reach the Cozy Community by:

* Chatting with us on IRC #cozycloud on irc.freenode.net
* Posting on our [Forum](https://forum.cozy.io/)
* Posting issues on the [Github repos](https://github.com/cozy/)
* Mentioning us on [Twitter](http://twitter.com/mycozycloud)
