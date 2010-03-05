# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
Imaging and ImagingApi are two class that handle calls to the imaging api.
"""

from pulse2.apis.clients import Pulse2Api
from pulse2.utils import isMACAddress
import logging

# need to get a ImagingApiManager, it will manage a Imaging api for each mirror
# defined in the conf file.


class Imaging(Pulse2Api):

    def __init__(self, *attr):
        self.name = "Imaging"
        Pulse2Api.__init__(self, *attr)

    # Computer registration
    def computerRegister(self, computerName, MACAddress, imagingData):
        """
        Called by pulse2-imaging-server to tell the Package Server to
        register a new computer. The computer name may contain a profile
        and an entity path (self,like profile:/entityA/entityB/computer)

        @type computerName: str
        @type MACAddress: str
        @raise : TypeError is computerName is not a str
        @raise : TypeError is MACAddress is not a mac addr
        @rtype : bool
        """
        if type(computerName) != str and type(computerName) != unicode:
            raise TypeError('Bad Computer name: %s' % computerName)
        if not isMACAddress(MACAddress):
            raise TypeError('BAD MAC address: %s' % MACAddress)
        d = self.callRemote("computerRegister", computerName, MACAddress, imagingData)
        d.addErrback(self.onErrorRaise, "Imaging:computerRegister", [computerName, MACAddress, imagingData])
        return d

    def computersRegister(self, computers):
        """
        Mass method to perform multiple computerRegister.
        Always called by the MMC agent.

        @param computers: list of triplets (hostname,MAC address,imaging data)
        @type computers: list

        @return: the (computer/MAC address) that were successfully registered.
        @rtype: list
        """
        d = self.callRemote("computersRegister", computers)
        d.addErrback(self.onErrorRaise, "Imaging:computersRegister", [computers])
        return d

    def computerPrepareImagingDirectory(self, MACAddress, imagingData=False):
        """
        Asks the Package Server to create the file system structure for the given computer uuid thanks to imagingData content.
        If imagingData is False, the package server queries the MMC agent for the imaging data.
        """
        if not isMACAddress(MACAddress):
            raise TypeError
        d = self.callRemote("computerPrepareImagingDirectory", MACAddress, imagingData)
        d.addErrback(self.onErrorRaise, "Imaging:computerPrepareImagingDirectory", [MACAddress, imagingData])
        return d

    def computerCreateImageDirectory(self, MACAddress):
        """
        Asks the Package Server to create the file system structure for the given computer uuid thanks to imagingData content.
        """
        if not isMACAddress(MACAddress):
            raise TypeError
        d = self.callRemote("computerCreateImageDirectory", MACAddress)
        d.addErrback(self.onErrorRaise, "Imaging:computerCreateImageDirectory", [MACAddress])
        return d

    def computerUnregister(self, uuid, archive=True):
        """
        Remove computer data from the Imaging Server.
        The computer must be registered again to use imaging.
        If archive is True, the computer imaging data are stored in an archive directory, else it is wiped out.
        """
        d = self.callRemote("computerUnregister", uuid, archive)
        d.addErrback(self.onErrorRaise, "Imaging:computerUnregister", [uuid, archive])
        return d

    # Computer Menu management
    def computerMenuUpdate(self, uuid):
        """
        Ask the pserver to update a menu.
        """
        d = self.callRemote("computerMenuUpdate", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerMenuUpdate", uuid)
        return d

    def computersMenuSet(self, menus):
        """
        send a full bunch of menus in a uuid=>menu format
        to the pserver.
        """
        d = self.callRemote("computersMenuSet", menus)
        d.addErrback(self.onErrorRaise, "Imaging:computersMenuSet", menus)
        return d

    def computerChangeDefaultMenuItem(self, uuid, num):
        """
        Ask the pserver to change the default item in a menu
        """
        d = self.callRemote("computerChangeDefaultMenuItem", uuid, num)
        d.addErrback(self.onErrorRaise, "Imaging:computerChangeDefaultMenuItem", uuid, num)
        return d

    # Computer log management
    def computerLogGet(self, uuid): # str
        """Get the imaging log of a computer."""
        d = self.callRemote("computerLogGet", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerLogGet", uuid)
        return d

    # Computer images management
    def computerBackupImagesGet(self, uuid): # list of imageData
        """
        Returns the data about the backup images for the given computer.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImagesGet", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImagesGet", uuid)
        return d

    def computerBackupImageLogGet(self, uuid, imageId):
        """
        Get the imaging log of a computer backup image.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImageLogGet", uuid, imageId)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImageLogGet", [uuid, imageId])
        return d

    def computerImageIsoBuild(self, uuid, imageId):
        """
        Build the auto restoration ISO CDROM of an image.
        Called by the MMC agent.
        """
        d = self.callRemote("computerImageIsoBuild", uuid, imageId)
        d.addErrback(self.onErrorRaise, "Imaging:computerImageIsoBuild", [uuid, imageId])
        return d

    def computerBackupImagesSetInformations(self, imageId, informations):
        """
        Set backup image informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImagesSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImagesSetInformations", [imageId, informations])
        return d

    # Imaging server images management
    def imagingServerStatus(self):
        """
        Returns a dict containing the status of the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerStatus")
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerStatus", None)
        return d

    def imagingServerMastersGet(self): # list of imageData
        """
        Returns the list of available master on the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerMastersGet")
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerMastersGet", None)
        return d

    def imagingServerMasterSetInformations(self, imageId, informations):
        """
        Set master image informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerMasterSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerMasterSetInformations", [imageId, informations])
        return d

    def imagingServerBootServicesGet(self): # list of bootServiceData
        """
        Returns the list of available boot services on the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerBootServicesGet")
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerBootServicesGet")
        return d

    def imagingServerBootServiceSetInformations(self, imageId, informations):
        """
        Set boot service informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerBootServiceSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerBootServiceSetInformations", [imageId, informations])
        return d

    def imagingServerDefaultMenuGet(self): # imagingMenu
        """
        Returns the default boot menu of the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerDefaultMenuGet")
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerDefaultMenuGet")
        return d

    def imagingServerDefaultMenuSet(self, imagingMenu):
        """
        Set the default boot menu on this imaging server for new computer without a profile.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerDefaultMenuSet", imagingMenu)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerDefaultMenuSet", imagingMenu)
        return d

    def imagingServerMasterIsoBuild(self, imageId):
        """
        Build the auto restoration ISO CDROM of a master.
        Called by the MMC agent.
        """
        d = self.callRemote("imagingServerMasterIsoBuild", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerMasterIsoBuild", imageId)
        return d

    def imagingServerBackupToMaster(self, imageId):
        """Convert a backup image to a master."""
        d = self.callRemote("imagingServerBackupToMaster", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerBackupToMaster", imageId)
        return d

    def imagingServerMasterDisable(self, imageId):
        """Disable a master."""
        d = self.callRemote("imagingServerMasterDisable", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerMasterDisable", imageId)
        return d

    def imagingServerMasterDelete(self, imageId, archive = True):
        """Delete a master. Maybe archive it."""
        d = self.callRemote("imagingServerMasterDelete", imageId, archive)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerMasterDelete", [imageId, archive])
        return d

    def imagingServerConfigurationSet(self, configuration):
        """Set the imaging server configuration (dict)."""
        d = self.callRemote("imagingServerConfigurationSet", configuration)
        d.addErrback(self.onErrorRaise, "Imaging:imagingServerConfigurationSet", configuration)
        return d

    # inventory related stuff
    def injectInventory(self, uuid, inventory):
        """
        Called by pulse2-imaging-server to give the Package Server a new inventory from MACAddress.
        """
        d = self.callRemote("injectInventory", uuid, inventory)
        d.addErrback(self.onErrorRaise, "Imaging:injectInventory", [uuid, inventory])
        return d

    # misc stuff
    def getComputerByMac(self, MACAddress):
        """
        Get a computer UUID using the MAC Address
        """
        d = self.callRemote("getComputerByMac", MACAddress)
        d.addErrback(self.onErrorRaise, "Imaging:getComputerByMac", MACAddress)
        return d

    # Logging stuff
    def logClientAction(self, uuid, level, phase, message):
        """
        Log action done by uuid
        """
        d = self.callRemote("logClientAction", uuid, level, phase, message)
        d.addErrback(self.onErrorRaise, "Imaging:logClientAction", uuid, level, phase, message)
        return d

    # Images related stuff
    def imageRegister(self, computer_uuid, image_uuid):
        """
        Declare a new image done on computer
        """
        d = self.callRemote("imageRegister", computer_uuid, image_uuid)
        d.addErrback(self.onErrorRaise, "Imaging:logClientAction", computer_uuid, image_uuid)
        return d

class ImagingApi(Imaging):
# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.

    def __init__(self, url=None):
        self.logger = logging.getLogger()
        credit = ''
        if type(url) == str or type(url) == unicode:
            self.server_addr = url
            if url.find('@') != -1:
                credit = url.split('/')[2].split('@')
            Imaging.__init__(self, credit, url)
        elif type(url) == dict:
            if url['enablessl']:
                self.server_addr = 'https://'
            else:
                self.server_addr = 'http://'

            if url['username'] != '':
                self.server_addr += url['username']
                credit = url['username']
                if url['password'] != '':
                    self.server_addr += ":" + url['password']
                    credit += ":" + url['password']
                self.server_addr += "@"

            self.server_addr += url['server'] + ':' + str(url['port']) + url['mountpoint']

            if url['verifypeer']:
                Imaging.__init__(self, credit, self.server_addr, url['verifypeer'], url['cacert'], url['localcert'])
            else:
                Imaging.__init__(self, credit, self.server_addr)
        else:
            self.logger.error("Imaging api : cant connect to %s, dont know how to do" % (url))
        self.logger.debug("ImagingApi> connected to %s" % (self.server_addr))
