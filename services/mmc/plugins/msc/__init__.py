# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Big modules
import logging
import time
import re
import os

# Twisted
from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor, defer

# Helpers
from mmc.support.mmctools import shLaunch, xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext

from mmc.plugins.base.computers import ComputerManager
from pulse2.managers.group import ComputerGroupManager
from pulse2.managers.location import ComputerLocationManager
from mmc.plugins.msc.database import MscDatabase
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.qaction import qa_list_files
from mmc.plugins.msc.machines import Machines, Machine
from mmc.plugins.msc.download import MscDownloadedFiles, MscDownloadProcess
import mmc.plugins.msc.actions
import mmc.plugins.msc.keychain
import mmc.plugins.msc.package_api

from mmc.plugins.msc.MSC_Directory import MSC_Directory
from mmc.plugins.msc.MSC_File import MSC_File

# XMLRPC client functions
import mmc.plugins.msc.client.scheduler

# ORM mappings
import pulse2.database.msc.orm.commands_on_host

VERSION = '2.0.0'
APIVERSION = '0:0:0'
REVISION = int('$Rev$'.split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
    Run some tests to ensure the module is ready to operate.
    """
    config = MscConfig()
    config.init("msc")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin msc: disabled by configuration.")
        return False

    if not os.path.isdir(config.qactionspath):
        logger.error("Quick Actions config is invalid: %s is not a directory. Please check msc.ini." % config.qactionspath)
        return False

    if not MscDatabase().activate(config):
        return False

    return True

def activate_2():
    conf = MscConfig()
    conf.init('msc')
    dldir = conf.download_directory_path
    # Clean all lock or error status file in the download directory pool
    if os.path.exists(dldir):
        logging.getLogger().info('Cleaning lock file in %s' % dldir)
        for root, dirs, files in os.walk(dldir):
            for name in files:
                if name.endswith(MscDownloadedFiles.LOCKEXT) or name.endswith(MscDownloadedFiles.ERROREXT):
                    os.remove(os.path.join(root, name))
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.locationsCount = ComputerLocationManager().getLocationsCount()
        s.userids = ComputerLocationManager().getUsersInSameLocations(self.userid)
        s.filterType = "mine"
        return s

##
# config
##
def getRepositoryPath():
    return xmlrpcCleanup(MscConfig().repopath)

##
# msc_script
##
def msc_script_list_file():
    return qa_list_files()

##
# exec
##
def msc_exec(command):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_exec(command))

def msc_ssh(user, ip, command):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_ssh(user, ip, command))

def msc_scp(user, ip, source, destination):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_scp(user, ip, source, destination))

class RpcProxy(RpcProxyI):
    ##
    # machines
    ##
    def getMachine(self, params):
        ctx = self.currentContext
        return xmlrpcCleanup2(Machines().getMachine(ctx, params))

    ##
    # commands
    ##

    ############ Scheduler driving
    def scheduler_start_all_commands(self, scheduler):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_all_commands(scheduler))

    def scheduler_start_these_commands(self, scheduler, commands):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_these_commands(scheduler, commands))

    def scheduler_ping_and_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return mmc.plugins.msc.client.scheduler.ping_and_probe_client(scheduler, computer)

    def scheduler_ping_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.ping_client(scheduler, computer))

    def scheduler_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.probe_client(scheduler, computer))

    def can_download_file(self):
        path = MscConfig().web_dlpath
        return (len(path) > 0) and os.path.exists(MscConfig().download_directory_path)

    def download_file(self, uuid):
        path = MscConfig().web_dlpath
        ctx = self.currentContext
        if not path:
            ret = False
        else:
            bwlimit = MscConfig().web_def_dlmaxbw
            ctx = self.currentContext
            computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
            try: # FIXME: dirty bugfix, should be factorized upstream
                computer[1]['fullname']
            except KeyError:
                computer[1]['fullname'] = computer[1]['cn'][0]
            mscdlp = MscDownloadProcess(ctx.userid, computer, path, bwlimit)
            ret = mscdlp.startDownload()
        return ret

    def get_downloaded_files_list(self):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        return mscdlfiles.getFilesList()

    def get_downloaded_file(self, node):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        return mscdlfiles.getFile(node)

    def remove_downloaded_files(self, ids):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        mscdlfiles.removeFiles(ids)

    def establish_vnc_proxy(self, scheduler, uuid, requestor_ip):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        try: # FIXME: dirty bugfix, should be factorized upstream
            computer[1]['fullname']
        except KeyError:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.tcp_sproxy(scheduler, computer, requestor_ip, "5900"))

    def pa_adv_countAllPackages(self, filt):
        ctx = self.currentContext
        g = mmc.plugins.msc.package_api.GetPackagesAdvanced(ctx, filt)
        g.deferred = defer.Deferred()
        g.get()
        g.deferred.addCallback(lambda x: len(x))
        return g.deferred

    def _range(self, result, start, end):
        if end == -1:
            return (len(result), result[start:len(result)])
        return (len(result), result[start:end])

    def pa_adv_getAllPackages(self, filt, start, end):
        start = int(start)
        end = int(end)
        ctx = self.currentContext
        g = mmc.plugins.msc.package_api.GetPackagesAdvanced(ctx, filt)
        g.deferred = defer.Deferred()
        g.get()
        g.deferred.addCallback(self._range, start, end)
        return g.deferred

    ##
    # commands management
    ##
    def add_command_quick_with_id(self, idcmd, target, lang, gid = None):
        """
        @param idcmd: id of the quick action
        @type idcmd: str

        @param target: targets, list of computers UUIDs
        @type target: list

        @param lang: language to use for the command title (two characters)
        @type lang: str

        @param gid: if not None, apply command to a group of machine
        @type gid: str
        """
        ctx = self.currentContext
        result, qas = qa_list_files()
        if result and idcmd in qas:
            try:
                desc = qas[idcmd]["title" + lang]
            except KeyError:
                desc = qas[idcmd]["title"]
            if gid:
                # Get all targets corresponding to the computer given group ID
                target = ComputerGroupManager().get_group_results(ctx, gid, 0, -1, '', True)
            d = MscDatabase().addCommandQuick(ctx, qas[idcmd]["command"], target, desc, gid)
            d.addCallback(xmlrpcCleanup)
            ret = d
        else:
            ret = -1
        return ret


    def add_command_quick(self, cmd, target, desc, gid = None):
        """
        Deprecated
        """
        ctx = self.currentContext
        d = MscDatabase().addCommandQuick(ctx, cmd, target, desc, gid)
        d.addCallbacks(xmlrpcCleanup, lambda err: err)
        return d

    def add_command_api(self, pid, target, params, p_api, mode, gid = None, proxy = []):
        """
        @param target: must be list of UUID
        @type target: list
        """
        ctx = self.currentContext
        #get_group_results(self, ctx, gid, min, max, filter):
        if gid:
            target = ComputerGroupManager().get_group_results(ctx, gid, 0, -1, '', True)
        g = mmc.plugins.msc.package_api.SendPackageCommand(ctx, p_api, pid, target, params, mode, gid, proxies = proxy)
        g.deferred = defer.Deferred()
        g.send()
        g.deferred.addCallbacks(xmlrpcCleanup, lambda err: err)
        return g.deferred

    def add_bundle_api(self, porders, target, params, mode, gid = None, proxy = []):
        ctx = self.currentContext
        if gid:
            target = ComputerGroupManager().get_group_results(ctx, gid, 0, -1, '', True)
        g = mmc.plugins.msc.package_api.SendBundleCommand(ctx, porders, target, params, mode, gid, proxy)
        g.deferred = defer.Deferred()
        g.send()
        g.deferred.addCallbacks(xmlrpcCleanup, lambda err: err)
        return g.deferred

    def get_id_command_on_host(self, id_command):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getIdCommandOnHost(ctx, id_command))

    def displayLogs(self, params = {}):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().displayLogs(ctx, params))

    def get_all_commandsonhost_currentstate(self):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostCurrentstate(ctx))

    def count_all_commandsonhost_by_currentstate(self, current_state, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsonhostByCurrentstate(ctx, current_state, filt))

    def get_all_commandsonhost_by_currentstate(self, current_state, min = 0, max = 10, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostByCurrentstate(ctx, current_state, min, max, filt))

    def count_all_commandsonhost_by_type(self, type = 0, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsonhostByType(ctx, type, filt))

    def get_all_commandsonhost_by_type(self, type, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostByType(ctx, type, min, max, filt))

    def count_all_commands_on_host(self, uuid, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsOnHost(ctx, uuid, filt))

    def get_all_commands_on_host(self, uuid, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsOnHost(ctx, uuid, min, max, filt))

    def get_commands_on_host(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsOnHost(ctx, coh_id))

    def get_target_for_coh(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getTargetForCoh(ctx, coh_id))

    def get_commands_history(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsHistory(ctx, coh_id))

    def get_bundle(self, bundle_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getBundle(ctx, bundle_id))

    def get_commands(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommands(ctx, cmd_id))

    def get_command_on_group_status(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnGroupStatus(ctx, cmd_id))

    def get_command_on_bundle_status(self, bundle_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnBundleStatus(ctx, bundle_id))

    def get_command_on_host_title(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnHostTitle(ctx, cmd_id))

    def get_command_on_host_in_commands(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnHostInCommands(ctx, cmd_id))

    def set_commands_filter(self, filterType):
        ctx = self.currentContext
        ctx.filterType = filterType

    def get_commands_filter(self):
        ctx = self.currentContext
        return ctx.filterType

    #
    # default WEB values handling
    #
    def get_def_package_label(self, label, version):
        localtime = time.localtime()
        return "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
            label,
            version,
            localtime[0],
            localtime[1],
            localtime[2],
            localtime[3],
            localtime[4],
            localtime[5]
        )

    def get_web_def_awake(self):
        return xmlrpcCleanup(MscConfig().web_def_awake)

    def get_web_def_date_fmt(self):
        return xmlrpcCleanup(MscConfig().web_def_date_fmt)

    def get_web_def_inventory(self):
        return xmlrpcCleanup(MscConfig().web_def_inventory)

    def get_web_def_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_mode)

    def get_web_def_force_mode(self):
        return xmlrpcCleanup(MscConfig().web_force_mode)

    def get_web_def_maxbw(self):
        return xmlrpcCleanup(MscConfig().web_def_maxbw)

    def get_web_def_delay(self):
        return xmlrpcCleanup(MscConfig().web_def_delay)

    def get_web_def_attempts(self):
        return xmlrpcCleanup(MscConfig().web_def_attempts)

    def get_web_def_deployment_intervals(self):
        return xmlrpcCleanup(MscConfig().web_def_deployment_intervals)

    def get_web_def_vnc_view_only(self):
        return xmlrpcCleanup(MscConfig().web_vnc_view_only)

    def get_web_def_vnc_show_icon(self):
        return xmlrpcCleanup(MscConfig().web_vnc_show_icon)

    def get_web_def_vnc_network_connectivity(self):
        return xmlrpcCleanup(MscConfig().web_vnc_network_connectivity)

    def get_web_def_vnc_allow_user_control(self):
        return xmlrpcCleanup(MscConfig().web_vnc_allow_user_control)

    def get_web_def_allow_local_proxy(self):
        return xmlrpcCleanup(MscConfig().web_allow_local_proxy)

    def get_web_def_local_proxy_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_local_proxy_mode)

    def get_web_def_max_clients_per_proxy(self):
        return xmlrpcCleanup(MscConfig().web_def_max_clients_per_proxy)

    def get_web_def_proxy_number(self):
        return xmlrpcCleanup(MscConfig().web_def_proxy_number)

    def get_web_def_proxy_selection_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_proxy_selection_mode)

    def get_web_def_issue_halt_to(self):
        return xmlrpcCleanup(MscConfig().web_def_issue_halt_to)
    
    def get_web_def_show_reboot(self):
        return xmlrpcCleanup(MscConfig().web_show_reboot)

    def get_web_def_probe_order(self):
        return xmlrpcCleanup(MscConfig().web_probe_order)

##
# machines
##
def getPlatform(uuid):
    return xmlrpcCleanup2(Machine(uuid).getPlatform())

def pingMachine(uuid):
    return xmlrpcCleanup2(Machine(uuid).ping())

### Commands on host handling ###
# FIXME: we should realy rationalize this stuff !
def start_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.startCommandOnHost(coh_id)
    mmc.plugins.msc.client.scheduler.startCommand(None, coh_id)
    return xmlrpcCleanup(True)
def pause_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.togglePauseCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def restart_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.restartCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def stop_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.stopCommandOnHost(coh_id)
    mmc.plugins.msc.client.scheduler.stopCommand(None, coh_id)
    return xmlrpcCleanup(True)
### Command on host handling ###

def action_on_command(id, f_name, f_database, f_scheduler):
    # Update command in database
    getattr(MscDatabase(), f_database)(id)
    # Stop related commands_on_host on related schedulers
    scheds = MscDatabase().getCommandsonhostsAndSchedulers(id)
    logger = logging.getLogger()
    for sched in scheds:
        d = getattr(mmc.plugins.msc.client.scheduler, f_scheduler)(sched, scheds[sched])
        d.addErrback(lambda err: logger.error("%s: " % (f_name) + str(err)))

def action_on_bundle(id, f_name, f_database, f_scheduler):
    # Update command in database
    getattr(MscDatabase(), f_database)(id)
    # Stop related commands_on_host on related schedulers
    scheds = MscDatabase().getCommandsonhostsAndSchedulersOnBundle(id)
    logger = logging.getLogger()
    for sched in scheds:
        d = getattr(mmc.plugins.msc.client.scheduler, f_scheduler)(sched, scheds[sched])
        d.addErrback(lambda err: logger.error("%s: " % (f_name) + str(err)))

### Commands handling ###
def stop_command(c_id):
    return action_on_command(c_id, 'stop_command', 'stopCommand', 'stopCommands')

def start_command(c_id):
    return action_on_command(c_id, 'start_command', 'startCommand', 'startCommands')

def pause_command(c_id):
    return action_on_command(c_id, 'pause_command', 'pauseCommand', 'pauseCommands')

def restart_command(c_id):
    return action_on_command(c_id, 'restart_command', 'restartCommand', 'restartCommands')
###

### Bundle handling ###
def stop_bundle(bundle_id):
    action_on_bundle(bundle_id, 'stop_bundle', 'stopBundle', 'stopCommands')
    return True

def start_bundle(bundle_id):
    action_on_bundle(bundle_id, 'start_bundle', 'startBundle', 'startCommands')
    return True

def pause_bundle(c_id):
    return action_on_bundle(c_id, 'pause_bundle', 'pauseBundle', 'pauseCommands')

def restart_bundle(c_id):
    return action_on_bundle(c_id, 'restart_bundle', 'restartBundle', 'restartCommands')
###

##
# common
##
def get_keychain():
    return xmlrpcCleanup(mmc.plugins.msc.keychain.get_keychain())

def file_exists(filename):
    return os.path.exists(filename)

def is_dir(filename):
    return os.path.isdir(filename)

#############################
################# Package API
from mmc.plugins.msc.package_api import PackageA

def pa_getAllPackages(p_api, mirror = None):
    return PackageA(p_api).getAllPackages(mirror)

def pa_getPackageDetail(p_api, pid):
    return PackageA(p_api).getPackageDetail(pid)

def pa_getPackageLabel(p_api, pid):
    return PackageA(p_api).getPackageLabel(pid)

def pa_getPackageVersion(p_api, pid):
    return PackageA(p_api).getPackageVersion(pid)

def pa_getPackageSize(p_api, pid):
    return PackageA(p_api).ps_getPackageSize(pid)

def pa_getPackageInstallInit(p_api, pid):
    return PackageA(p_api).getPackageInstallInit(pid)

def pa_getPackagePreCommand(p_api, pid):
    return PackageA(p_api).getPackagePreCommand(pid)

def pa_getPackageCommand(p_api, pid):
    return PackageA(p_api).getPackageCommand(pid)

def pa_getPackagePostCommandSuccess(p_api, pid):
    return PackageA(p_api).getPackagePostCommandSuccess(pid)

def pa_getPackagePostCommandFailure(p_api, pid):
    return PackageA(p_api).getPackagePostCommandFailure(pid)

def pa_getPackageHasToReboot(p_api, pid):
    return PackageA(p_api).getPackageHasToReboot(pid)

def pa_getPackageFiles(p_api, pid):
    return PackageA(p_api).getPackageFiles(pid)

def pa_getFileChecksum(p_api, file):
    return PackageA(p_api).getFileChecksum(file)

def pa_getPackagesIds(p_api, label):
    return PackageA(p_api).getPackagesIds(label)

def pa_getPackageId(p_api, label, version):
    return PackageA(p_api).getPackageId(label, version)

def pa_isAvailable(p_api, pid, mirror):
    return PackageA(p_api).isAvailable(pid, mirror)

#############################

#############################
################# Mirrors API
from mmc.plugins.msc.mirror_api import MirrorApi

def ma_getMirror(machine):
    return MirrorApi().getMirror(machine)

def ma_getMirrors(machines):
    return MirrorApi().getMirrors(machines)

def ma_getFallbackMirror(machine):
    return MirrorApi().getFallbackMirror(machine)

def ma_getFallbackMirrors(machines):
    return MirrorApi().getFallbackMirrors(machines)

def ma_getApiPackage(machine):
    return MirrorApi().getApiPackage(machine)

def ma_getApiPackages(machines):
    return MirrorApi().getApiPackages(machines)

############ MSC_Directory
def repo_directory_scan(directory_path, mime_types_data):
    dir = MSC_Directory(directory_path, mime_types_data)
    dir.scan()
    return dir.array_files

def repo_directory_get_parent(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.get_parent()

def repo_directory_make_directory(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.make_directory()

def repo_directory_delete_directory(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.delete_directory()

def repo_directory_get_directory_only(directory_path):
    dir = MSC_Directory(directory_path)
    return xmlrpcCleanup(dir.get_directory_only())

def repo_directory_get_file_only(directory_path):
    dir = MSC_Directory(directory_path)
    return xmlrpcCleanup(dir.get_file_only())

def repo_directory_show_in_ascii(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.show_in_ascii()

#############################
############ MSC_File
def repo_file_get_content(filename):
    file = MSC_File(filename)
    return file.get_content()

def repo_file_write_content(filename, content):
    file = MSC_File(filename)
    return file.write_content(content)

def repo_file_download(filename, mimetypes = {'':''}):
    file = MSC_File(filename, mimetypes)
    return file.download()

def repo_file_download_to_local_host(filename, path_source):
    file = MSC_File(filename)
    return file.download_to_local_host(path_source)

def repo_file_create(filename):
    file = MSC_File(filename)
    return file.create()

def repo_file_remove(filename):
    file = MSC_File(filename)
    return file.remove()

def repo_file_rename(filename, new_name):
    file = MSC_File(filename)
    return file.rename()

def repo_file_execute(filename):
    file = MSC_File(filename)
    return file.execute()

def repo_file_upload(filename, file_to_upload):
    file = MSC_File(filename)
    return file.upload(file_to_upload)

#############################
def file_exists(filename):
    return os.path.exists(filename)

def is_dir(filename):
    return os.path.isdir(filename)

def xmlrpcCleanup2(obj):
    try:
        return xmlrpcCleanup(obj.toH())
    except:
        return xmlrpcCleanup(obj)
