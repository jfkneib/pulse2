# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Caching related functions / objects
"""

import logging
import ConfigParser
import os.path

import pulse2.utils
import pulse2.package_server.config

class UUIDCache(pulse2.utils.Singleton):
    """
    This is a object-cache for UUID/MAC conversion stuff.

    It work like this:
     - if info is in cache *and* less than memoryLifetime, serve it
     - if not, try to find it into the local cache (UUIDS.txt); it less than diskLifetime, serve it and update local cache, resetting lifetime
     - if not, try to find it asking the agent, updating both disk cache and local cache, resetting lifetime
    """

    cachePath = pulse2.package_server.config.P2PServerCP().imaging_api['uuid_cache_file']
    log = logging.getLogger('imaging')
    log.info("Using %s as UUID Cache File" % cachePath)
    config = ConfigParser.ConfigParser()

    def __init__(self):
        pulse2.utils.Singleton.__init__(self)
        if not os.path.isfile(self.cachePath):
            try:
                self.log.info("Creating my UUID Cache File %s" % (self.cachePath))
                fp = open(self.cachePath, 'wb')
                self.config.write(fp)
                fp.close()
            except Exception, e:
                self.log.warn("Can't create my UUID Cache File %s : %s" % (self.cachePath, e))
                return None
        if not self._fetch():
            return None

    def _flush(self):
        """
        Update cache file using our memory stucture
        """
        try:
            self.log.debug("Writing my UUID Cache File %s" % (self.cachePath))
            fp = open(self.cachePath, 'wb')
            self.config.write(fp)
            fp.close()
        except Exception, e:
            self.log.warn("Can't write my UUID Cache File %s : %s" % (self.cachePath, e))
            return False
        return True

    def _fetch(self):
        """
        Update memory stucture using our cache file
        """
        try:
            self.log.info("Reading my UUID Cache File %s" % (self.cachePath))
            fp = open(self.cachePath, 'rb')
            self.config.readfp(fp)
            fp.close()
        except Exception, e:
            self.log.warn("Can't read my UUID Cache File %s : %s" % (self.cachePath, e))
            return False
        return True

    def getByMac(self, mac):
        """
        Get a computer by its MAC from the cache.

        @param mac : the client mac address (mandatory)
        @type mac : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        uuid = ''
        shortname = ''
        fqdn = ''

        if not pulse2.utils.isMACAddress(mac):
            return False

        mac = pulse2.utils.normalizeMACAddress(mac)

        for section in self.config.sections() :
            if self.config.has_option(section, 'mac'):
                if self.config.get(section, 'mac') == mac:
                    uuid = section
                    if self.config.has_option(section, 'shortname'):
                        shortname = self.config.get(section, 'shortname')
                    if self.config.has_option(section, 'fullname'):
                        fqdn = self.config.get(section, 'fullname')
                    return {
                        'uuid'      : uuid,
                        'mac'       : mac,
                        'shortname' : shortname,
                        'fqdn'      : fqdn
                        }
        return False

    def getByShortName(self, name):
        """
        Get a computer by its shortname from the cache.

        @param name : the client name (mandatory)
        @type name : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        uuid = ''
        mac = ''
        fqdn = ''

        for section in self.config.sections :
            if self.config.has_option(section, 'shortname'):
                if self.config.get(section, 'shortname') == name:
                    shortname = self.config.get(section, 'shortname')
                    uuid = section
                    if self.config.has_option(section, 'mac'):
                        mac = self.config.get(section, 'mac')
                    if self.config.has_option(section, 'fullname'):
                        fqdn = self.config.get(section, 'fullname')
                    return {
                        'uuid'      : uuid,
                        'mac'       : mac,
                        'shortname' : shortname,
                        'fqdn'      : fqdn
                        }
        return False

    def getByUUID(self, uuid):
        """
        Get a computer by its UUID from the cache.

        @param uuid : the client UUID (mandatory)
        @type uuid : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        mac = ''
        shortname = ''
        fqdn = ''

        if not pulse2.utils.isUUID(uuid):
            return False

        if self.config.has_section(uuid):
            if self.config.has_option(uuid, 'mac'):
                mac = self.config.get(uuid, 'mac')
            if self.config.has_option(uuid, 'shortname'):
                shortname = self.config.get(uuid, 'shortname')
            if self.config.has_option(uuid, 'fullname'):
                fqdn = self.config.get(uuid, 'fullname')
            return {
                'uuid'      : uuid,
                'mac'       : mac,
                'shortname' : shortname,
                'fqdn'      : fqdn
                }
        return False

    def get(self, uuid):
        """
        """
        return self.getByUUID(uuid)

    def set(self, uuid, mac, shortname = '', domain = ''):
        """
        Add a computer in cache.

        @param uuid : the client UUID (mandatory)
        @type uuid : str
        @param mac : the client MAC address(mandatory)
        @type mac : str
        @param shortname : the client host name (default : '')
        @type shortname : str
        @param domain : the client domain name (default: '')
        @type domain : str

        @return: True on success
        @rtype: boolean
        """

        if not pulse2.utils.isMACAddress(mac):
            return False
        if not pulse2.utils.isUUID(uuid):
            return False
        fqdn = shortname + '.' + domain
        mac = pulse2.utils.normalizeMACAddress(mac)
        if not self.config.has_section(uuid):
            self.config.add_section(uuid)
        self.config.set(uuid, 'mac', mac)
        self.config.set(uuid, 'shortname', shortname)
        self.config.set(uuid, 'fqdn', fqdn)
        self._flush()
        return True
