#!/usr/bin/env python

import Murmur
import logging
from utils import log_exceptions
from db import ForumDB
from dbdict import DictDB

toddlers = DictDB("toddlers.json", format='json') 

db = ForumDB()
spamembers = db.getSpaMembers()

class KindergardenOnConnect(Murmur.ServerCallback):
    def __init__(self, con, kgChanId, kgGroup, toddlers=toddlers, allowed=spamembers):
        self.labelAdd = "Set as toddler"
        self.labelDel = "Unset as toddler"
        self.infoMsg = "<span style='color:red;font-weight:bold;'>You are still treated as a toddler.</span>"
        self.con = con
        self.chanid = kgChanId
        self.group = kgGroup
        self.toddlers = toddlers
        self.allowed = allowed
        self.server = self.con.meta.getServer(1)

        self.contextCB = KindergardenContext(self.con, self.chanid, self.group, self.toddlers)

        onlineUsers = self.server.getUsers()
        for user in onlineUsers.values():
            self.userConnected(user)

    def userDisconnected(self, user, current=None):
        pass

    @log_exceptions
    def userConnected(self, user, current=None):
        #set up menu entries
        if user.name == "ditch":
            logging.debug("Setting up kindergarden menu entries for %s" % user.name)
            self.con.addServerContextCB(self.contextCB, user.session, "kgadd", self.labelAdd, self.server)
            self.con.addServerContextCB(self.contextCB, user.session, "kgdel", self.labelDel, self.server)

        #check for toddler status
        if user.userid in self.toddlers:
            logging.debug("Connected user %s seems to be a toddler." % user.name)
            self.server.addUserToGroup(0, user.session, self.group)
            user.channel = self.chanid
            self.server.setState(user)
            self.con.sendMessage(user, self.infoMsg)

    def userStateChanged(self, user, current=None):
        pass

    def channelCreated(self, chan, current=None):
        pass

    def channelRemoved(self, chan, current=None):
        pass

    def channelStateChanged(self, chan, current=None):
        pass

class KindergardenContext(Murmur.ServerContextCallback):
    def __init__(self, con, chan, group, toddlers=toddlers, allowed=spamembers):
        self.addMsg = "<span style='color:red;font-weight:bold;'>You are now treated as a toddler.</span>"
        self.removedMsg = "<span style='color:red;font-weight:bold;'>You are no longer a toddler.</span>"
        self.con = con
        self.toddlers = toddlers
        self.allowed = allowed
        self.chanid = chan
        self.group = group
        self.server = self.con.meta.getServer(1)
        
    @log_exceptions
    def contextAction(self, action, user, session, chanid, current=None):
        logging.debug("User %s called %s" % (user.name, action))
        if action == "kgdel":
            if user.session == session:
                return
            else:
                target = self.server.getState(session)
                if target.userid in self.toddlers:
                    logging.debug("target of %s (user %s) is a toddler." % (action, target.name))
                    target.channel = 0
                    logging.debug("removing toddler status from %s." % target.name)
                    del self.toddlers[target.userid]
                    self.toddlers.sync()
                    logging.debug("current toddlers: %s" % self.toddlers)
                    self.server.removeUserFromGroup(0, session, self.group)
                    self.server.setState(target)
                    self.con.sendMessage(target, self.removedMsg)
                else:
                    logging.debug("target of %s (user %s) wasn't a toddler." % (action, target.name))
                    
        elif action == "kgadd":
            target = self.server.getState(session)
            if target.userid == -1:
                self.con.sendMessage(user, "You can't mark anonymous users as toddlers. Just put them into root or something...")
                return
            if target.name in self.allowed:
                self.con.sendMessage(user, "As strange as it may seem: SpA members are no toddlers.")
                return
            if user.session == session:
                self.con.sendMessage(user, "Don't be silly!")
                return
            if target.userid in self.toddlers:
                self.con.sendMessage(user, "%s already is a toddler" % target.name)
                return

            target.channel = self.chanid
            logging.debug("%s is adding %s as a toddler" % (user.name, target.name))
            self.toddlers[target.userid] = chanid
            self.toddlers.sync()
            logging.debug("current %s: %s" % (self.group, self.toddlers))
            self.server.addUserToGroup(0, session, self.group)
            self.server.setState(target)
            self.con.sendMessage(target, self.addMsg)

        return
