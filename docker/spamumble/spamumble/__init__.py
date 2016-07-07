#!/usr/bin/env python

import logging
from authenticator import ForumAuthenticator
from iceconnection import Connection
from notifier import NotifyOnConnect
from kindergarden import KindergardenOnConnect

def main():
    logging.basicConfig(filename='spamumble.log', format="%(asctime)s (%(levelname)s) [%(module)s] %(message)s", level=logging.DEBUG)
    try:
        connection = Connection() 
        connection.setAuthenticator(ForumAuthenticator(connection))
        connection.addServerCB(NotifyOnConnect(connection))
        kindergarden = KindergardenOnConnect(connection, 28, "toddlers")
        connection.addServerCB(kindergarden)
        connection.waitForShutdown()
    except KeyboardInterrupt:
        logging.info("ctrl-c: shutting down")
        connection.cleanup()
        connection.ice.shutdown()

if __name__ == "__main__":
    main()
