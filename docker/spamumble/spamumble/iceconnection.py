#!/usr/bin/env python

import Ice, Murmur
import logging

DEFAULT_HOST = "mumble-server"
DEFAULT_PORT = 6502

### callbacks ###

class MetaCallback(Murmur.MetaCallback):
    def __init__(self, con):
        self.con = con

    def started(self, vserver, current=None):
        #TODO: maybe get vserver and setup callbacks on it
        logging.debug("VServer %s started" % vserver)

    def stopped(self, vserver, current=None):
        logging.debug("VServer %s stopped" % vserver)

class ServerCallback(Murmur.ServerCallback):
    def __init__(self, con, server):
        self.con = con
        self.server = server

    def userConnected(self, user, current=None):
        logging.debug("User %s connected" % user.name)

    def userDisconnected(self, user, current=None):
        logging.debug("User %s disconnected" % user.name)

    def userStateChanged(self, user, current=None):
        logging.debug("User %s changed state" % user.name)

    def channelCreated(self, chan, current=None):
        logging.debug("Channel %s created with id %s" % (chan.name, chan.id))

    def channelRemoved(self, chan, current=None):
        logging.debug("Channel %s with id %s removed" % (chan.name, chan.id))

    def channelStateChanged(self, chan, current=None):
        logging.debug("Channel %s changed state (id %s)" % (chan.name, chan.id))

class ServerContextCallback(Murmur.ServerContextCallback):
    def __init__(self, con):
        self.con = con

    def contextAction(self, action, user, session, chanid, current=None):
        logging.debug("ContextAction %s performed by %s" % (action, user))

class Connection:
    def __init__(self, icehost=DEFAULT_HOST, iceport=DEFAULT_PORT, initdata=None):
        self.callbacks = {'meta':[], 'server':[], 'serverContext':[], 'auth':[]}
        self.host = (icehost, iceport)
        if not initdata:
            initdata = Ice.InitializationData()
        self.ice = Ice.initialize(initdata)

        logging.debug("Connecting to %s:%s..." % self.host)
        self.meta = Murmur.MetaPrx.checkedCast(self.ice.stringToProxy('Meta:tcp -h %s -p %s' % self.host))
        logging.debug("Connection to %s:%s successful" % self.host)

        self.adapter = self.ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h %s" % self.host[0])
        self.adapter.activate()
        self._callbackSetup()

    def _callbackSetup(self):
        metaCB = Murmur.MetaCallbackPrx.uncheckedCast(self.adapter.addWithUUID(MetaCallback(self)))
        self.meta.addCallback(metaCB)

        for server in self.meta.getBootedServers():
            serverCB = Murmur.ServerCallbackPrx.uncheckedCast(self.adapter.addWithUUID(ServerCallback(self, server))) 
            server.addCallback(serverCB)
        self.callbacks['server'].append(serverCB)
        self.callbacks['meta'].append(metaCB)

    def setAuthenticator(self, authenticator, server=None):
        auth = Murmur.ServerAuthenticatorPrx.uncheckedCast(self.adapter.addWithUUID(authenticator))
        if server:
            server.setAuthenticator(auth)
        else:
            for server in self.meta.getBootedServers():
                server.setAuthenticator(auth)
        self.callbacks['auth'].append(auth)

    def addServerCB(self, cb, server=None):
        logging.debug("Adding ServerCallback %s", cb)
        serverCB = Murmur.ServerCallbackPrx.uncheckedCast(self.adapter.addWithUUID(cb))
        if server:
            server.addCallback(serverCB)
        else:
            for server in self.meta.getBootedServers():
                server.addCallback(serverCB)
        self.callbacks['server'].append(serverCB)

    def addServerContextCB(self, cb, session, name, label, server=None):
        logging.debug("Adding ServerContextCallback %s", cb)
        serverContextCB = Murmur.ServerContextCallbackPrx.uncheckedCast(self.adapter.addWithUUID(cb))
        if server:
            server.addContextCallback(session, name, label, serverContextCB, Murmur.ContextUser)
        else:
            for server in self.meta.getBootedServers():
                server.addContextCallback(session, name, label, serverContextCB, Murmur.ContextUser)
        self.callbacks['serverContext'].append(serverContextCB)

    def sendMessage(self, user, msg, server=None):
        logging.debug("Sending txt \"%s\" to %s" % (msg, user.name))
        if server:
            server.sendMessage(user.session, msg)
        else:
            server = self.meta.getServer(1)
            server.sendMessage(user.session, msg)

    def cleanup(self):
        logging.debug("trying to clean up...")
        for server in self.meta.getBootedServers():
            for cb in self.callbacks['server']:
                logging.debug("removing %s", cb)
                server.removeCallback(cb)
            for cb in self.callbacks['serverContext']:
                logging.debug("removing %s", cb)
                server.removeContextCallback(cb)
        for cb in self.callbacks['meta']:
            logging.debug("removing %s", cb)
            self.meta.removeCallback(cb)
            
    def waitForShutdown(self):
        try:
            self.ice.waitForShutdown()
        except Ice.ProtocolException, e:
            logging.critical(e)
            self.ice.waitForShutdown()
