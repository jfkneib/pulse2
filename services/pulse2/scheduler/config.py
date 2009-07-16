# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# Misc
import ConfigParser
import re           # fo re.compil
import pwd          # for getpwnam
import grp          # for getgrpnam
import string       # for atoi
import logging      # logging stuff
import os.path      # for file checking

# Others Pulse2 Stuff
import pulse2.utils
from pulse2.xmlrpc import isTwistedEnoughForLoginPass
from pulse2.database.msc.config import MscDatabaseConfig


class SchedulerDatabaseConfig(MscDatabaseConfig):
    dbname = "msc"
    dbsection = "database"

    def __setup_fallback(self, mscconffile):
        logging.getLogger().info("Reading configuration file (database config): %s" % mscconffile)
        self.dbsection = "msc"
        MscDatabaseConfig.setup(self, mscconffile)

    def setup(self, conffile):
        mscconffile = pulse2.utils.getConfigFile("msc")
        if os.path.exists(conffile):
            try:
                logging.getLogger().info("Trying to read configuration file (database config): %s" % conffile)
                MscDatabaseConfig.setup(self, conffile)
            except Exception, e:
                logging.getLogger().warn("Configuration file: %s does not contain any database config" % conffile)
                self.__setup_fallback(mscconffile)
            if not self.cp.has_section("database"):
                logging.getLogger().warn("Configuration file: %s does not contain any database config" % conffile)
                self.__setup_fallback(mscconffile)
        elif os.path.exists(mscconffile):
            self.__setup_fallback(mscconffile)
        else:
            raise Exception("can find any config file")

class SchedulerConfig(pulse2.utils.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
    cp = None

    # [scheduler] section default values
    announce_check = dict()
    awake_time = 600
    clean_states_time = 3600
    active_clean_states =  '' # possible states are : stop run
    cacert = "/etc/mmc/pulse2/scheduler/keys/cacert.pem"
    client_check = None
    dbencoding = 'utf-8'
    enablessl = True
    localcert = "/etc/mmc/pulse2/scheduler/keys/privkey.pem"
    host = "127.0.0.1"
    max_command_time = 3600
    max_slots = 300
    max_upload_time = 21600
    max_wol_time = 300
    mg_assign_algo = 'default'
    mode = 'async'
    password = 'password'
    port = 8000
    resolv_order = ['fqdn', 'netbios', 'hosts', 'ip']
    scheduler_path = '/usr/sbin/pulse2-scheduler'
    server_check = None
    username = 'username'
    verifypeer = False

    # [daemon] section
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0
    setrlimit = ''

    # [launcher_xxx] section
    launchers = {
    }

    launchers_uri = {}

    def setoption(self, section, key, attrib, type = 'str'):
        if type == 'str':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.get(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'bool':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getboolean(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        if type == 'int':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getint(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'pass':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getpassword(section, key))
                logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, section, key))
            else:
                logging.getLogger().warn("scheduler %s: section %s, option %s not set, using default value" % (self.name, section, key))

    def presetup(self, config_file):
        """
            used to pre-parse conf file to gather enough data to setuid() soon
        """
        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option("daemon", "user"):
            self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
        if self.cp.has_option("daemon", "group"):
            self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
        if self.cp.has_option("daemon", "umask"):
            self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
        if self.cp.has_option("handler_hand01", "args"):
            self.logdir = os.path.dirname(re.compile("['|\"]").split(self.cp.get("handler_hand01", "args"))[1])
        if self.cp.has_option("daemon", "setrlimit"):
            self.setrlimit = self.cp.get("daemon", "setrlimit")

    def setup(self, config_file):
        # Load configuration file
        if not self.cp: # self.cp is set if presetup() was already called
            self.presetup(config_file)

        # [scheduler] section parsing
        self.name = self.cp.get("scheduler", "id")

        self.setoption("scheduler", "awake_time", "awake_time", 'int')
        self.setoption("scheduler", "clean_states_time", "clean_states_time", 'int')
        self.setoption("scheduler", "active_clean_states", "active_clean_states")
        self.active_clean_states_run = False
        self.active_clean_states_stop = False
        for s in self.active_clean_states.split(','):
            if s == 'run': self.active_clean_states_run = True
            if s == 'stop': self.active_clean_states_stop = True
                
        self.setoption("scheduler", "max_slots", "max_slots", 'int')
        self.setoption("scheduler", "max_command_time", "max_command_time", 'int')
        self.setoption("scheduler", "max_upload_time", "max_upload_time", 'int')
        self.setoption("scheduler", "max_wol_time", "max_wol_time", 'int')
        self.setoption("scheduler", "dbencoding", "dbencoding")
        self.setoption("scheduler", "enablessl", "enablessl", 'bool')

        if self.cp.has_option("scheduler", "mg_assign_algo"):
            self.mg_assign_algo = self.cp.get("scheduler", 'mg_assign_algo')

        if self.enablessl:
            if self.cp.has_option("scheduler", "privkey"):
                self.localcert = self.cp.get("scheduler", "privkey")
            if self.cp.has_option("scheduler", "localcert"):
                self.localcert = self.cp.get("scheduler", "localcert")
            if self.cp.has_option("scheduler", "certfile"):
                self.cacert = self.cp.get("scheduler", "certfile")
            if self.cp.has_option("scheduler", "cacert"):
                self.cacert = self.cp.get("scheduler", "cacert")
            if self.cp.has_option("scheduler", "verifypeer"):
                self.verifypeer = self.cp.getboolean("scheduler", "verifypeer")
            if not os.path.isfile(self.localcert):
                raise Exception('scheduler "%s": can\'t read SSL key "%s"' % (self.name, self.localcert))
                return False
            if not os.path.isfile(self.cacert):
                raise Exception('scheduler "%s": can\'t read SSL certificate "%s"' % (self.name, self.cacert))
                return False
            if self.verifypeer: # we need twisted.internet.ssl.Certificate to activate certs
                import twisted.internet.ssl
                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception('scheduler "%s": I need at least Python Twisted 2.5 to handle peer checking' % (self.name))
                    return False

        if self.cp.has_option("scheduler", "listen"): # TODO remove in a future version
            logging.getLogger().warning("'listen' is obsolete, please replace it in your config file by 'host'")
            self.setoption("scheduler", "listen", "host")
        else:
            self.setoption("scheduler", "host", "host")
        self.setoption("scheduler", "port", "port")
        self.port = int(self.port)
        self.setoption("scheduler", "username", "username")
        self.setoption("scheduler", "password", "password", 'pass')
        if not isTwistedEnoughForLoginPass():
            if self.username != '':
                if self.username != 'username':
                    logging.getLogger().warning("your version of twisted is not high enough to use login (scheduler/username)")
                self.username = ''
            if self.password != '':
                if self.password != 'password':
                    logging.getLogger().warning("your version of twisted is not high enough to use password (scheduler/password)")
                self.password = ''

        self.setoption("scheduler", "mode", "mode")
        self.setoption("scheduler", "resolv_order", "resolv_order")
        if not type(self.resolv_order) == type([]):
            self.resolv_order = self.resolv_order.split(' ')
        self.setoption("scheduler", "scheduler_path", "scheduler_path")

        if self.cp.has_option("scheduler", "client_check"):
            self.client_check = {}
            for token in self.cp.get("scheduler", "client_check").split(','):
                (key, val) = token.split('=')
                self.client_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'client_check', self.client_check))
        if self.cp.has_option("scheduler", "server_check"):
            self.server_check = {}
            for token in self.cp.get("scheduler", "server_check").split(','):
                (key, val) = token.split('=')
                self.server_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))
        if self.cp.has_option("scheduler", "announce_check"):
            self.announce_check = {}
            for token in self.cp.get("scheduler", "announce_check").split(','):
                (key, val) = token.split('=')
                self.announce_check[key] = val
            logging.getLogger().info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))

        # [daemon] section parsing (parsing ofr user, group, and umask is done above in presetup)
        if self.cp.has_section("daemon"):
            if self.cp.has_option('daemon', 'pid_path'):
                logging.getLogger().warning("'pid_path' is deprecated, please replace it in your config file by 'pidfile'")
                self.setoption('daemon', 'pid_path', 'pid_path')
            else:
                self.setoption('daemon', 'pidfile', 'pid_path')

        # [launcher_xxx] section parsing
        for section in self.cp.sections():
            if re.compile("^launcher_[0-9]+$").match(section):
                username = self.cp.get(section, "username")
                password = self.cp.getpassword(section, "password")
                if not isTwistedEnoughForLoginPass():
                    if username != '':
                        logging.getLogger().warning("your version of twisted is not high enough to use login (%s/username)"%(section))
                        username = ''
                    if password != '':
                        logging.getLogger().warning("your version of twisted is not high enough to use password (%s/password)"%(section))
                        password = ''

                self.launchers[section] = {
                        'enablessl': self.cp.getboolean(section, "enablessl"),
                        'host': self.cp.get(section, "host"),
                        'username': username,
                        'password': password,
                        'port': self.cp.get(section, "port")
                    }
                if self.launchers[section]["enablessl"]:
                    uri = "https://"
                else:
                    uri = 'http://'
                if self.launchers[section]['username'] != '':
                    uri += '%s:%s@' % (self.launchers[section]['username'], self.launchers[section]['password'])
                uri += '%s:%d' % (self.launchers[section]['host'], int(self.launchers[section]['port']))
                self.launchers_uri.update({section: uri})
