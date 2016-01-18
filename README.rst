MTGCollector : Collection made easy
===================================

Installation
------------

Whichever OS you use for mtgcollector, you'll need a working MySQL or Mariadb installation.

As this configuration is already well explained for different OSes on the web, we will not
describe how to install and configure it. You will need a network access to the server,
either on localhost or on the net. Unix sockets connection is not supported.


Linux
^^^^^

To install MTGCollector on linux, you first need to install its dependencies :

    - On Debian/Ubuntu and derivatives :

        $ sudo apt-get update && sudo apt-get install python3-mysql.connector

    - On Fedora :

        $ sudo dnf install mysql-connector-python3


Even if this is not mandatory we recommend using virtualenv to run mtgcollector. You can find it
named virtualenv or python-virtualenv depending on your distribution.

If you decided to use virtualenv you should then :

    $ virtualenv -p /usr/bin/python3 ${directory_to_store_virtualenv} --system-site-package
    $ source {directory_to_store_virtualenv}/bin/activate

Note : it might also be called `virtualenv-3.*`

And then install python's dependencies :

    $ pip3 install -r ${mtgcollector_folder}/requirements.pip

Note : pip3 can be named `pip` depending on your distribution.

You then only need to run

    $ python3 ${mtgcollector_folder}/mtgcollector.py --host ${address}

Going to the server's home page on a browser will let you configure the rest.


Windows
^^^^^^^

Download python3 from `https://www.python.org/downloads/`

Install mysql-connector from `https://dev.mysql.com/downloads/connector/python/`

In a shell, type

    $ pip install -r ${mtgcollector_folder}/requirements.pip

Then

    $ python3 ${mtgcollector_folder}/mtgcollector.py --host ${address}


Mac OSx
^^^^^^^

We couldn't try on Mac OSX, but the procedure should be approximately the same as for linux



Testing
-------

To test MTGCollector, you need a database.

To easily handle connection to the database, MTGCollector tester uses the following environment variables :

    - DATABASE_USER = "root"
    - DATABASE_PASSWORD = ""
    - DATABASE_HOST = "127.0.0.1"
    - DATABASE_PORT = 3306
    - DATABASE_NAME = "mtg_test"
    - SERVER_PORT = 5050

You can then run the tests with the standard python unittest procedure :

    $ python3 -m unittest --discover .

