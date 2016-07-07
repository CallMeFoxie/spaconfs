#!/usr/bin/env python

import MySQLdb, logging
from collections import namedtuple

class ForumDBException(MySQLdb.Error):
    pass

class ForumDB:
    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            self.con = MySQLdb.connect(host="spamysql", user="phpbb2", passwd="Tra8uhaWreTr", db="spaforum")
        except MySQLdb.Error, e:
            logging.error(e)
            raise ForumDBException
 
        self.cur = self.con.cursor()

    def _execute(self, *args):
        try:
            return self.cur.execute(*args)
        except MySQLdb.OperationalError:
            try:
                self._connect()
                return self.cur.execute(*args)
            except MySQLdb.Error, e:
                logging.error(e)
                raise ForumDBException

    def getSpaMembers(self):
        rows = self._execute("select username from phpbb_users left join phpbb_user_group using (user_id) where phpbb_user_group.group_id = 6")
        if not rows:
            return None
        else:
            return [x[0] for x in self.cur.fetchall()]

    def getUserFromId(self, uid):
        rows = self._execute("select username from phpbb_users where user_id = %s", (uid,))
        if not rows:
            return None
        else:
            return self.cur.fetchone()[0]

    def getUserData(self, uname):
        userData = namedtuple("UserData", "id, pw, type, name")
        rows = self._execute("select user_id, user_password, user_type, username from phpbb_users where lower(username) = lower(%s)", (uname,))
        if not rows:
            return None
        else:
            return userData._make(self.cur.fetchone())

    def getUserGroups(self, uid):
        self._execute("select group_name from phpbb_user_group left join phpbb_groups using (group_id) where user_id = %s", (uid,))
        return [x[0] for x in self.cur.fetchall()]

    def getUserAvatar(self, uid):
        rows = self._execute("select user_avatar, user_avatar_type from phpbb_users where user_id = %s", (uid,))
        if not rows:
            return None
        else:
            avatar, atype = self.cur.fetchone()
            if atype in ("avatar.driver.upload", ):
                return avatar
            else:
                return None

    def getBans(self, uid):
        banData = namedtuple("BanData", "reason, comment")
        rows = self._execute("select ban_reason, ban_give_reason from phpbb_banlist where ban_userid=%s", (uid,))
        if not rows:
            return None
        else:
            return [banData._make(x) for x in self.cur.fetchall()]
