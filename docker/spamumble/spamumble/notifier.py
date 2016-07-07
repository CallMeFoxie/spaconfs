#!/usr/bin/env python

import Murmur
import logging
from utils import log_exceptions

class NotifyOnConnect(Murmur.ServerCallback):
    def __init__(self, con):
        self.con = con

    def userDisconnected(self, user, current=None):
        pass

    @log_exceptions
    def userConnected(self, user, current=None):
        logging.debug("User %s with ID %s using release %s" % (user.name, user.userid, user.release))
        if user.name == "[SpA]SaintK":
            self.con.sendMessage(user, '<span style="color:red;font-weight:bold;">sup biatch</span>')
        if user.userid == -1:
            self.con.sendMessage(user, '<span style="color:red;font-weight:bold;">You are not a registered user and can\'t talk or join channels. Please consider registering at <a href="http://forum.specialattack.net/ucp.php?mode=register">http://forum.specialattack.net/ucp.php?mode=register</a> to use all mumble features</span>')

    def userStateChanged(self, user, current=None):
        pass

    def channelCreated(self, chan, current=None):
        pass

    def channelRemoved(self, chan, current=None):
        pass

    def channelStateChanged(self, chan, current=None):
        pass
