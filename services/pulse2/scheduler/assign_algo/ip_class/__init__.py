#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
    Pulse2 PackageServer
"""

import random
from pulse2.scheduler.assign_algo import MGAssignAlgo

class MGUserAssignAlgo(MGAssignAlgo):
    name = 'ip_class'
    # functions has to be put
    def getMachineGroup(self, myT):
        netmask = [255, 254, 0, 0] # FIXME: netmask is hardcoded !!!
        if myT.target_ipaddr:
            real_target =  myT.target_ipaddr.split('||')[0]
            try:
                a_ip = map(lambda x: int(x), real_target.split('.'))
                for i in range(0,4):
                    a_ip[i] = a_ip[i] & netmask[i]
                return '.'.join(map(lambda x: str(x), a_ip))
            except ValueError:
                return ''
        return ''

    def getMaxNumberOfGroups(self):
        return 3
