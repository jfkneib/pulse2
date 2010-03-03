# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2.
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Configuration reader for imaging
"""

from mmc.support.config import PluginConfig
from pulse2.database.imaging.config import ImagingDatabaseConfig

class ImagingConfig(PluginConfig, ImagingDatabaseConfig):

    """
    Read and hold MMC agent imaging plugin configuration
    """

    web_def_date_fmt = "%Y-%m-%d %H:%M:%S"
    web_def_default_protocol = 'nfs'
    web_def_default_menu_name = 'Menu'
    web_def_default_timeout = '60'
    web_def_default_background_uri = ''
    web_def_default_message = 'Warning ! Your PC is being backed up or restored. Do not reboot !'
    web_def_kernel_parameters = 'quiet'
    web_def_image_parameters = ''

    def __init__(self, name = 'imaging', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            ImagingDatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        """
        Read web section of the imaging plugin configuration file
        """
        PluginConfig.readConf(self)
        ImagingDatabaseConfig.setup(self, self.conffile)
        if self.has_section("web"):
            for i in ('date_fmt', 'default_protocol', 'default_menu_name',
                      'default_timeout', 'default_background_uri',
                      'default_message'):
                full_name = "web_def_%s" % i
                if self.has_option("web", full_name):
                    setattr(self, full_name, self.get("web", full_name))
