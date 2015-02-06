# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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
Update plugin for the MMC agent
"""
import logging
import subprocess
import json
from time import time
from twisted.internet.threads import deferToThread
deferred = deferToThread.__get__  # Create an alias for deferred functions

logger = logging.getLogger()

from mmc.support.mmctools import SecurityContext, RpcProxyI
from mmc.core.tasks import TaskManager

from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.dashboard.panel import Panel

from mmc.plugins.update.config import updateConfig
from mmc.plugins.update.database import updateDatabase
from mmc.plugins.msc import create_update_command
from pulse2.managers.group import ComputerGroupManager
from mmc.plugins.base.computers import ComputerManager

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

APIVERSION = "0:1:0"
last_update_check_ts = None
available_updates = []


def getApiVersion():
    return APIVERSION


def activate():
    config = updateConfig("update")
    if config.disabled:
        logger.warning("Plugin UpdateMgr: disabled by configuration.")
        return False
    if not updateDatabase().activate(config):
        logger.error("UpdateMgr database not activated")
        return False

    DashboardManager().register_panel(Panel('product_updates'))
    DashboardManager().register_panel(Panel('clients_updates'))

    # Add create update commands in the task manager
    if config.enable_update_commands:
        TaskManager().addTask("update.create_update_commands",
                              (create_update_commands,),
                              cron_expression=config.update_commands_cron)
    if config.enable_update_description:
        TaskManager().addTask("add_update_description",
                              (add_update_description,),
                              cron_expression=config.add_update_description_cron)
    return True


def calldb(func, *args, **kw):
    return getattr(updateDatabase(), func).__call__(*args, **kw)


def get_os_classes(params):
    return updateDatabase().get_os_classes(params)


def enable_only_os_classes(os_classes_ids):
    """
    Enable spacified os_classes and disble others
    """
    return updateDatabase().enable_only_os_classes(os_classes_ids)


def get_update_types(params):
    return updateDatabase().get_update_types(params)


def add_update_description():
    return updateDatabase().add_update_description()


def get_updates(params):
    """
    Get updates standard function,
    if gid or uuids is defined group view is used
    else global view is used
    """
    if ('gid' or 'uuids') in params:
        return _get_updates_for_group(params)
    else:
        return updateDatabase().get_updates(params)


def _get_updates_for_group(params):
    """
    Get updates from uuids list if params['uuids'] is a correct list of uuid
    and from group if params['gid'] is a correct group id
    """
    if 'gid' in params:
        params['uuids'] = []
        # Creating root context
        ctx = SecurityContext()
        ctx.userid = 'root'

        # get uuid for all computer of this group
        ComputerList = ComputerGroupManager().get_group_results(
            ctx, params['gid'], 0, -1, {})
        for uuid in ComputerList:
            params['uuids'].append(int(uuid.lower().replace('uuid', '')))

    # get updates for this group
    updates = updateDatabase().get_updates_for_group(params)
    return updates


def get_machines_update_status(not_supported=False):
    """
    Get machine update status as a dict as key
    and status string as value.
    commons status values :"not_supported","not_registered",
    "up-to-date","need_update","update_available","update_planned",
    "os_update_disabled".
    The "not_supported" value can be disabled with not_supported param.
    """
    # Creating root context
    ctx = SecurityContext()
    ctx.userid = 'root'

    machines_status = {}
    uuids = []

    # get computer list who returned update
    machines_update = updateDatabase().get_machines()
    # get activated os computers:
    machines_os_enabled = _get_updatable_computers(ctx, activated=True)
    # get disabled os computers:
    machines_os_disabled = _get_updatable_computers(ctx, activated=False)
    # get uuid for all computer
    ComputerList = ComputerManager().getComputersList(ctx, {}).keys()
    uuids = []
    # convert uuid as string number
    for uuid in ComputerList:
        uuids.append(int(uuid.lower().replace('uuid', '')))
    machines_os_enabled = [
        int(uuid.lower().replace('uuid', '')) for uuid in machines_os_enabled]
    machines_os_disabled = [
        int(uuid.lower().replace('uuid', '')) for uuid in machines_os_disabled]
    # get status of all machines
    for uuid in uuids:
        if uuid in machines_os_disabled:
            machines_status["UUID" + str(uuid)] = "os_update_disabled"
        elif uuid in machines_os_enabled:
            if uuid in machines_update:
                # if no neutral update not installed on this machine
                if len(updateDatabase().get_neutral_updates_for_host(uuid, 0)) == 0:
                    # if no eligible update
                    if len(updateDatabase().get_eligible_updates_for_host(uuid)) == 0:
                        machines_status["UUID" + str(uuid)] = "up-to-date"
                    else:
                        machines_status["UUID" + str(uuid)] = "update_planned"
                else:
                    machines_status["UUID" + str(uuid)] = "update_available"
            else:
                machines_status["UUID" + str(uuid)] = "not_registered"
        elif not_supported:
            machines_status["UUID" + str(uuid)] = "not_supported"

    return machines_status


def set_update_status_for_group(gid, update_ids, status):
    """
    Set updates status for one define group of machine, for multiples defines
    update to status param value.
    This does not affect global status of update
    """
    for update_id in update_ids:
        updateDatabase().set_update_status_for_group(gid, update_id, status)
    return True


def set_update_status(update_id, status):
    """
    Set  global status of one update
    """
    return updateDatabase().set_update_status(update_id, status)


def _get_updatable_computers(ctx, activated=True):
    # Get active computer manager
    computer_manager = ComputerManager().getManagerName()

    if computer_manager == 'inventory':
        dyngroup_pattern = '%d==inventory::Hardware/OperatingSystem==%s'
    elif computer_manager == 'glpi':
        dyngroup_pattern = '%d==glpi::Operating system==%s'
    else:
        logging.getLogger().error(
            'Update module: Unsupported computer manager %s' %
            computer_manager)
        return False
    # Get all enabled os_classes
    if activated:
        os_classes = updateDatabase().get_os_classes(
            {'filters': {'enabled': 1}})
    else:
        os_classes = updateDatabase().get_os_classes(
            {'filters': {'enabled': 0}})

    targets = []
    # Create update command for enabled os_classes
    for os_class in os_classes['data']:

        patterns = os_class['pattern'].split('||')
        request = []
        equ_bool = []

        for i in xrange(len(patterns)):
            request.append(dyngroup_pattern % (i + 1, patterns[i]))
            equ_bool.append(str(i + 1))

        request = '||'.join(request)
        equ_bool = 'OR(%s)' % ','.join(equ_bool)

        targets.extend(ComputerManager().getComputersList(
            ctx, {
                'request': request, 'equ_bool': equ_bool}).keys())
    return targets


def create_update_commands():
    # TODO: ensure that this method is called by taskmanager
    # and not directly by XMLRPC

    # Creating root context
    ctx = SecurityContext()
    ctx.userid = 'root'
    targets = _get_updatable_computers(ctx)
    # Fetching all targets
    for uuid in targets:
        machine_id = int(uuid.lower().replace('uuid', ''))
        updates = updateDatabase().get_eligible_updates_for_host(
            machine_id)

        update_list = [update['uuid'] for update in updates]

        # Create update command for this host with update_list
        create_update_command(ctx, [uuid], update_list)
    return True


def get_update_conflicts_for_host(uuid):
    return updateDatabase().get_update_conflicts_for_host(uuid)


class RpcProxy(RpcProxyI):

    updMgrPath = '/usr/share/pulse-update-manager/pulse-update-manager'

    def runInShell(self, cmd):
        process = subprocess.Popen(
            [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        out, err = process.communicate()
        return out.strip(), err.strip(), process.returncode

    def getProductUpdates(self):

        @deferred
        def _getProductUpdates():
            global last_update_check_ts, available_updates
            o, e, ec = self.runInShell('%s -l --json' % self.updMgrPath)

            # Check json part existence
            if not '===JSON_BEGIN===' in o or not '===JSON_END===' in o:
                available_updates = False

            # Get json output
            json_output = o.split('===JSON_BEGIN===')[1].split(
                '===JSON_END===')[0].strip()
            packages = json.loads(json_output)['content']

            result = []

            for pkg in packages:
                pulse_filters = (
                    'python-mmc',
                    'python-pulse2',
                    'mmc-web',
                    'pulse',
                    'mmc-agent')

                # Skip non-Pulse packages
                if not pkg[2].startswith(pulse_filters):
                    continue

                result.append({
                    'name': pkg[2],
                    'title': pkg[1]
                })

            # Caching last result
            available_updates = result
            last_update_check_ts = time()

        global last_update_check_ts, available_updates
        # If last checking is least than 4 hours, return cached value
        if not last_update_check_ts or (time() - last_update_check_ts) > 14400:
            _getProductUpdates()

        return available_updates

    def installProductUpdates(self):

        # Reset update cache
        global last_update_check_ts, available_updates
        last_update_check_ts = None
        available_updates = []

        pulse_packages_filter = "|grep -e '^python-mmc' -e '^python-pulse2' -e '^mmc-web' -e '^pulse' -e '^mmc-agent$'"
        install_cmd = "LANG=C dpkg -l|awk '{print $2}' %s|xargs apt-get -y install" % pulse_packages_filter
        install_cmd = "%s -l|awk '{print $1}' %s|xargs %s -i" % (
            self.updMgrPath, pulse_packages_filter, self.updMgrPath)
        install_cmd += '; for service in /etc/init.d/{mmc-agent,pulse2-*}; do $service restart; done'

        @deferred
        def _runInstall():
            # Running install command with no pipe
            subprocess.call(install_cmd, shell=True)

        _runInstall()

        return True
