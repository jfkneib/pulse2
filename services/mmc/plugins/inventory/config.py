#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: __init__.py 3 2008-03-03 14:35:11Z cdelfosse $
#
# This file is part of MMC.
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from pulse2.database.inventory.config import InventoryDatabaseConfig
from mmc.support.mmctools import xmlrpcCleanup
from mmc.plugins.inventory.utilities import getInventoryParts
from mmc.support import mmctools

from ConfigParser import NoOptionError
import logging

class InventoryConfig(InventoryDatabaseConfig):
    disable = True
    expert_mode = {}
    graph = {}
    
    def init(self, name = 'inventory', conffile = None):
        self.dbsection = "inventory"
        self.name = name
        if not conffile: self.conffile = mmctools.getConfigFile(name)
        else: self.conffile = conffile

        InventoryDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        self.disable = self.cp.getboolean("main", "disable")
        for i in getInventoryParts():
            try:
                self.graph[i] = self.get("graph", i).split('|')
            except:
                self.graph[i] = []
            try:
                self.expert_mode[i] = self.get("expert_mode", i).split('|')
            except:
                self.expert_mode[i] = []


