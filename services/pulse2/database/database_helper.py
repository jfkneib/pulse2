# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
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

"""
Define classes to help implementing the database access in all the
pulse2 modules.
"""

from pulse2.utils import Singleton
from pulse2.ddl import DDLContentManager, DBControl
from pulse2.database.sqlalchemy_tests import checkSqlalchemy, MIN_VERSION, MAX_VERSION, CUR_VERSION
from sqlalchemy.exc import DBAPIError, NoSuchTableError

import logging
NB_DB_CONN_TRY = 2

class DatabaseHelper(Singleton):
    is_activated = False
    config = None

    def db_check(self):
        required_version = DDLContentManager().get_version(self.my_name)
        if not checkSqlalchemy():
            self.logger.error("Sqlalchemy: current version is %s. Must be between %s and %s" % (CUR_VERSION, MIN_VERSION, MAX_VERSION))
            return False

        conn = self.connected()
        if conn:
            if required_version > conn :
                return self.db_update()
            elif required_version != -1 and conn != required_version:
                self.logger.error("%s database version error: v.%s needeed, v.%s found; please update your schema !" % (self.my_name, required_version, conn))
                return False
        else:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check %s." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser, self.configfile))
            return False

        return True
    def db_update(self):
        """Automatic database update"""
 
        db_control = DBControl(user=self.config.dbuser, 
                               passwd=self.config.dbpasswd, 
                               host=self.config.dbhost, 
                               port=self.config.dbport, 
                               module=self.config.dbname,
                               log=self.logger,
                               use_same_db=True)

        return db_control.process()
       

    def connected(self):
        try:
            if self.db != None:
                if hasattr(self, "version"):
                    return self.version.select().execute().fetchone()[0]
                elif hasattr(self, "Version"):
                    return self.version.select().execute().fetchone()[0]
                else:
                    return True
            return False
        except:
            if (self.db != None) and (self.session != None):
                return True
            return False

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin
        configuration.

        @rtype: str
        """
        if self.config == None:
            raise Exception("Object must have a config attribute")
        if self.config.dbport:
            port = ":" + str(self.config.dbport)
        else:
            port = ""
        url = "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)
        if self.config.dbdriver == 'mysql':
            # See http://www.sqlalchemy.org/docs/05/reference/dialects/mysql.html#character-sets
            # charset=utf8 will convert all data to UTF-8, even if tables are
            # stored in Latin-1
            url += '?charset=utf8&use_unicode=0'
            if self.config.dbsslenable:
                url = url + "&ssl_ca=%s&ssl_key=%s&ssl_cert=%s" % (self.config.dbsslca, self.config.dbsslkey, self.config.dbsslcert)
        return url

    def enableLogging(self, level = None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            if hasattr(self.config, "dbdebug"):
                level = self.config.dbdebug
            else:
                level = logging.INFO
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    def getDbConnection(self):
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError, e:
                self.logger.error(e)
            except Exception, e:
                self.logger.error(e)
            if ret: break
        if not ret:
            raise "Database connection error"
        return ret

    def initMappersCatchException(self):
        try:
            self.initMappers()
        except NoSuchTableError, e:
            logging.getLogger().warn('The table %s does not exists.'%str(e))
            return False
        except Exception, e:
            logging.getLogger().warn(e)
            return False
        return True

###########################################################
def id2uuid(id):
    return "UUID%d" % id

def uuid2id(uuid):
    return uuid.replace("UUID", "")

###########################################################
class DBObject(object):
    to_be_exported = ['id', 'name', 'label']
    need_iteration = []
    i18n = []
    def getUUID(self):
        if hasattr(self, 'id'):
            return id2uuid(self.id)
        logging.getLogger().warn("try to get %s uuid!"%(type(self)))
        return False
    def to_h(self):
        return self.toH()
    def toH(self, level = 0):
        ret = {}
        for i in dir(self):
            if i in self.i18n:
                pass

            if i in self.to_be_exported:
                ret[i] = getattr(self, i)
            if i in self.need_iteration and level < 1:
                # we don't want to enter in an infinite loop
                # and generally we don't need more levels
                attr = getattr(self, i)
                if type(attr) == list:
                    new_attr = []
                    for a in attr:
                        new_attr.append(a.toH(level+1))
                    ret[i] = new_attr
                else:
                    ret[i] = attr.toH(level+1)
        if hasattr(self, 'id'):
            ret['db_uuid'] = self.getUUID()
        return ret

