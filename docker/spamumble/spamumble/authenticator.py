#!/usr/bin/env python

from db import ForumDB
from phpass import PasswordHash
from utils import log_exceptions
import Murmur, PythonMagick
import logging, os, time

class InvalidateOnLeave(Murmur.ServerCallback):
    def __init__(self, fa):
        self.fa = fa

    def userDisconnected(self, user, current=None):
        logging.debug("Removing %s's info from cache (disconnected)" % user.name)
        try:
            del self.fa.usercache[user.userid]
        except KeyError:
            pass
        if user.userid in self.fa.bots:
            logging.debug("Freeing BotID %s" % user.userid)
            self.fa.bots.remove(user.userid)
            self.fa.botids.append(user.userid)


    def userConnected(self, user, current=None):
        pass

    def userStateChanged(self, user, current=None):
        pass

    def channelCreated(self, chan, current=None):
        pass

    def channelRemoved(self, chan, current=None):
        pass

    def channelStateChanged(self, chan, current=None):
        pass

class ForumAuthenticator(Murmur.ServerAuthenticator):
    def __init__(self, con):
        self.con = con
        self.db = ForumDB()
        self.usercache = {}
        self.avatar_path = "/avatars/dcd83b3563190c3d191b4ec7315f2171_"
        self.id_offset = 1000000000
        self.pwhash = PasswordHash()
        self.botpw = "lipFLI9hhc0lI"
        self.bots = []
        self.botids = list(range(100,200))
        self.botids.reverse()

        logging.debug("Registering InvalidateOnLeave callback")
        self.con.addServerCB(InvalidateOnLeave(self))

    @log_exceptions
    def isBot(self, name, pw):
        res = ((name.startswith('[Bot]') or name.startswith('[clone]') or name.startswith('[SpA]Eve')) and (str(pw) == str(self.botpw)))
        logging.debug("bot status is %s" % res)
        
        return res

    @log_exceptions
    def authenticate(self, name, pw, certificates, certhash, certstrong, current=None):
        # uid is -1 for authentication failures and -2 for unknown user (fallthrough)
        logging.debug("User %s trying to auth" % name)
        if self.isBot(name, pw):
            currentId = self.botids.pop()
            logging.info("Authenticated %s as ID %s with groups bots" % (name, currentId))
            self.bots.append(currentId)
            logging.debug(repr(currentId, name, ['bots']))
            return (currentId, name, ['bots'])

        userData = self.db.getUserData(name)
        if not userData:
            logging.debug("%s is an unknown user" % name)
            return (-2, name, None)
        elif not self.pwhash.check_password(pw, userData.pw):
            logging.info("wrong pw for %s - expected %s, got %s" % (userData.name, userData.pw, pw))
            return (-1, userData.name, None)
        elif not userData.type in (0, 3):
            logging.debug("%s is denied because marked as inactive" % userData.name)
            return (-1, userData.name, None)
        else:
            uid = userData.id + self.id_offset
            bans = self.db.getBans(userData.id)
            if bans:
                for ban in bans:
                    logging.debug("BAN: user is marked as banned %s", (repr(ban),))
                    return (uid, userData.name, ['banned'])
            grouplist = [x.lower() for x in self.db.getUserGroups(userData.id)]
            logging.info("Authenticated %s as ID %s with groups %s" % (userData.name, uid, ','.join(grouplist)))
            self.usercache[uid] = {'name': userData.name, 'groups': grouplist}
            logging.debug( (uid, userData.name, grouplist))
            return (uid, userData.name, grouplist)

    def getInfo(self, id, current=None):
        return (False, None)

    @log_exceptions
    def nameToId(self, name, current=None):
        # uid is -2 for unknown name
        userData = self.db.getUserData(name)
        if not userData:
            logging.debug("nameToId for %s is %s" % (name, -2))
            return -2
        else:
            logging.debug("nameToId for %s is %s" % (name, userData.id + self.id_offset))
            return userData.id + self.id_offset

    @log_exceptions
    def idToName(self, id, current=None):
        # uname is "" for unkown id
        if id in self.usercache:
            logging.debug("idToName for %s is %s (cached)" % (id, self.usercache[id]['name']))
            return self.usercache[id]['name']

        uname = self.db.getUserFromId(id-self.id_offset)
        if uname:
            logging.debug("idToName for %s is %s" % (id, uname))
            return uname
        else:
            logging.debug("idToName for %s is \"\"" % id)
            return ""

    @log_exceptions
    def idToTexture(self, id, current=None):
        if id in self.usercache:
            uinfo = self.usercache[id]
            if 'avatar' in uinfo:
                logging.debug("Avatar for %s found in cache" % id)
                return uinfo['avatar']

        uid = id - self.id_offset
        filename = self.db.getUserAvatar(uid)
        if not filename:
            logging.debug("No avatar for %s found" % id)
            self.usercache[id]['avatar'] = None 
            return None 
        else:
            name, ext = os.path.splitext(filename)
            filepath = self.avatar_path + str(uid) + ext
            logging.debug("Requested texture for avatar %s" % filepath)
            try:
                img = PythonMagick.Image(filepath)
            except:
		logging.debug("Error magicking image %s" % filepath)
                return None
            blob = PythonMagick.Blob()
            img.write(blob, 'jpeg')
            logging.debug("Caching avatar %s" % filepath)
            if id not in self.usercache:
                self.usercache[id] = {}
            self.usercache[id]['avatar'] = blob.data
            return blob.data
