#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
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

from mmc.support.mmctools import xmlrpcCleanup, RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.base.provisioning import ProvisioningManager
from mmc.plugins.glpi.database import GlpiConfig, Glpi
from mmc.plugins.glpi.computers import GlpiComputers
from mmc.plugins.glpi.provisioning import GlpiProvisioner
from mmc.plugins.pulse2.location import ComputerLocationManager
from mmc.plugins.glpi.location import GlpiLocation
import logging

VERSION = "2.0.0"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    config = GlpiConfig("glpi")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin glpi: disabled by configuration.")
        return False

    GlpiLocation().init(config) # does Glpi().activate()
    if not Glpi().db_check():
        return False
                    
    ComputerManager().register("glpi", GlpiComputers)
    ProvisioningManager().register("glpi", GlpiProvisioner)
    if config.displayLocalisationBar:
        ComputerLocationManager().register("glpi", GlpiLocation)

    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class RpcProxy(RpcProxyI):
    def getLocationsList(self, filt = None):
        ctx = self.currentContext
        return xmlrpcCleanup(GlpiLocation().getLocationsList(ctx, filt))

def getLastMachineInventoryFull(uuid):
    return xmlrpcCleanup(Glpi().getLastMachineInventoryFull(uuid))

def inventoryExists(uuid):
    return xmlrpcCleanup(Glpi().inventoryExists(uuid))

def getLastMachineInventoryPart(uuid, part):
    return xmlrpcCleanup(Glpi().getLastMachineInventoryPart(uuid, part))

def getMachineMac(uuid):
    return xmlrpcCleanup(Glpi().getMachineMac(uuid))

def getMachineIp(uuid):
    return xmlrpcCleanup(Glpi().getMachineIp(uuid))

# TODO
def getInventoryEM(part):
    return []

