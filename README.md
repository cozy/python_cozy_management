## Description

Helper to manage self hosting cozy

** ⚠ This tool has only been tested on the platforms we support (Debian / Ubuntu / Raspbian). Some of the commands will not work on other distributions. It is mostly a wrapper around shell commands, so if you use another distribution, you can probably read the code and adapt the commands to your distribution **

## Install

Make sure those packages are installed on your environment :
> python-requests python-docopt python-openssl	python-psutil python-pkg-resources

Then, install Python Cozy Management :
`pip install cozy_management`

## Usage

* **show_diag**: display a quick diagnostic of the server;
* **show_reporting**: display a full diagnostic of your server state;
* **ping_couchdb**: check whether CouchDB is running;
* **get_admin**: display credentials used by Cozy to connect to CouchDB;
* **get_couchdb_admins**: list all CouchDB admin logins;
* **create_token**: create a CouchDB admin user and write the credentials into Cozy configuration files;
* **delete_token**: delete CouchDB admin user used by Cozy and remove the configuration file;
* **reset_token**: delete and create the CouchDB admin user used by Cozy, updating the configuration files;
* **create_cozy_db**: create the database;
* **get_cozy_param <name>**: get a parameter of the instance. Current available parameters are `domain` and `locale`;
* **get_crt_common_name**: get the common name of the TLS certificate (the domain name);
* **generate_certificate <common_name> --size <size> --digest <digest>**: create a certificate;
* **make_links <common_name>**: create the symbolic links to the certificate files in NGinx configuration;
* **clean_links**: delete the symbolic links to the certificate files in NGinx configuration;
* **regenerate_dhparam**: regenerate the DH parameters (a file used when creating a certificate);
* **is_cozy_registered**: check whether user has already registered its server;
* **unregister_cozy**: delete user account from database;
* **fix_oom_scores**: try to prevent applications from the stack to be killed if memory goes low;
* **get_oom_scores**: get the Out Of Memory score for each application;
* **rebuild_app <app>**: reinstall every npm dependencies of an application;
* **rebuild_all_apps**: reinstall every npm dependencies of all applications (useful when upgrading Node version);
* **migrate_2_node4**: 
* **install_requirements**: 
* **install_cozy**: install the Cozy server;
* **wait_couchdb**: wait until couchdb has started;
* **wait_cozy_stack**: wait until full Cozy stack has started;
* **emulate_smtp [--bind <ip>] [--port <port>]** starts a fake SMTP server on port 25 for debugging purpose;
* **backup**: create a timestamped backup of Cozy configuration and data into `/var/lib/cozy/backups`;
* **restore <backup_filename>**: restore a backup;

## Contribution

* Pick and solve an [issue](https://github.com/cozy/python_cozy_management/issues)

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
