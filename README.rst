MTGCollector : Collection made easy
===================================

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

