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

""" Class to map msc.commands_on_host to SA
"""

import logging
import time
import datetime
import sqlalchemy.orm

class CommandsOnHost(object):
    """ Mapping between msc.commands_on_host and SA
    """
    def getId(self):
        return self.id

    def getIdCommand(self):
        return self.fk_commands

    def getIdTarget(self):
        return self.fk_target

### Handle upload states ###
    def isUploadImminent(self):
        result = (self.isStateScheduled() and self.isInTimeSlot())
        logging.getLogger().debug("isUploadImminent(#%s): %s" % (self.getId(), result))
        return result

    def setUploadIgnored(self):
        self.setUploadStatut('IGNORED')
    def isUploadIgnored(self):
        result = (self.uploaded == 'IGNORED')
        logging.getLogger().debug("isUploadIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setUploadFailed(self):
        self.setUploadStatut('FAILED')
    def isUploadFailed(self):
        result = (self.uploaded == 'FAILED')
        logging.getLogger().debug("isUploadFailed(#%s): %s" % (self.getId(), result))
        return result

    def setUploadDone(self):
        self.setUploadStatut('DONE')
    def isUploadDone(self):
        result = (self.uploaded == 'DONE')
        logging.getLogger().debug("isUploadDone(#%s): %s" % (self.getId(), result))
        return result

    def setUploadInProgress(self):
        self.setUploadStatut('WORK_IN_PROGRESS')
    def isUploadRunning(self):
        result = (self.uploaded == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isUploadRunning(#%s): %s" % (self.getId(), result))
        return result

    def setUploadToDo(self):
        self.setUploadStatut('TODO')
    def isUploadToDo(self):
        result = (self.uploaded == 'TODO')
        logging.getLogger().debug("isUploadToDo(#%s): %s" % (self.getId(), result))
        return result

    def setUploadStatut(self, uploaded):
        self.uploaded = uploaded
        self.flush()
### /Handle upload states ###

### Handle execution states ###
    def isExecutionImminent(self):
        result = ((self.isStateScheduled() or self.getCommandStatut() == 'upload_done') and self.isInTimeSlot())
        logging.getLogger().debug("isExecutionImminent(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionIgnored(self):
        self.setExecutionStatut('IGNORED')
    def isExecutionIgnored(self):
        result = (self.executed == 'IGNORED')
        logging.getLogger().debug("isExecutionIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionFailed(self):
        self.setExecutionStatut('FAILED')
    def isExecutionFailed(self):
        result = (self.executed == 'FAILED')
        logging.getLogger().debug("isExecutionFailed(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionDone(self):
        self.setExecutionStatut('DONE')
    def isExecutionDone(self):
        result = (self.executed == 'DONE')
        logging.getLogger().debug("isExecutionDone(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionInProgress(self):
        self.setExecutionStatut('WORK_IN_PROGRESS')
    def isExecutionRunning(self):
        result = (self.executed == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isExecutionRunning(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionToDo(self):
        self.setExecutionStatut('TODO')
    def isExecutionToDo(self):
        result = (self.executed == 'TODO')
        logging.getLogger().debug("isExecutionToDo(#%s): %s" % (self.getId(), result))
        return result

    def setExecutionStatut(self, executed):
        self.executed = executed
        self.flush()
### /Handle execution states ###

### Handle deletion states ###
    def isDeleteImminent(self):
        result = ((self.isStateScheduled() or self.getCommandStatut() == 'execution_done') and self.isInTimeSlot())
        logging.getLogger().debug("isDeleteImminent(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteIgnored(self):
        self.setDeleteStatut('IGNORED')
    def isDeleteIgnored(self):
        result = (self.deleted == 'IGNORED')
        logging.getLogger().debug("isDeleteIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteFailed(self):
        self.setDeleteStatut('FAILED')
    def isDeleteFailed(self):
        result = (self.deleted == 'FAILED')
        logging.getLogger().debug("isDeleteFailed(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteDone(self):
        self.setDeleteStatut('DONE')
    def isDeleteDone(self):
        result = (self.deleted == 'DONE')
        logging.getLogger().debug("isDeleteDone(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteInProgress(self):
        self.setDeleteStatut('WORK_IN_PROGRESS')
    def isDeleteRunning(self):
        result = (self.deleted == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isDeleteRunning(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteToDo(self):
        self.setDeleteStatut('TODO')
    def isDeleteToDo(self):
        result = (self.deleted == 'TODO')
        logging.getLogger().debug("isDeletePossible(#%s): %s" % (self.getId(), result))
        return result

    def setDeleteStatut(self, deleted):
        self.deleted = deleted
        self.flush()
### /Handle deletion states ###

### Handle inventory states ###
    def isInventoryImminent(self):
        result = ((self.isStateScheduled() or self.getCommandStatut() == 'deletion_done') and self.isInTimeSlot())
        logging.getLogger().debug("isInventoryImminent(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryIgnored(self):
        self.setInventoryStatut('IGNORED')
    def isInventoryIgnored(self):
        result = (self.inventoried == 'IGNORED')
        logging.getLogger().debug("isInventoryIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryFailed(self):
        self.setInventoryStatut('FAILED')
    def isInventoryFailed(self):
        result = (self.inventoried == 'FAILED')
        logging.getLogger().debug("isInventoryFailed(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryDone(self):
        self.setInventoryStatut('DONE')
    def isInventoryDone(self):
        result = (self.inventoried == 'DONE')
        logging.getLogger().debug("isInventoryDone(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryInProgress(self):
        self.setInventoryStatut('WORK_IN_PROGRESS')
    def isInventoryRunning(self):
        result = (self.inventoried == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isInventoryRunning(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryToDo(self):
        self.setInventoryStatut('TODO')
    def isInventoryToDo(self):
        result = (self.inventoried == 'TODO')
        logging.getLogger().debug("isInventoryToDo(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryStatut(self, inventoried):
        self.inventoried = inventoried
        self.flush()

    """
    def setInventoryFailed(self):
        self.setCommandStatut('inventory_failed')
    def isInventoryFailed(self):
        result = (self.getCommandStatut() == 'inventory_failed')
        logging.getLogger().debug("isInventoryFailed(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryDone(self):
        self.setCommandStatut('inventory_done')
    def isInventoryDone(self):
        result = (self.getCommandStatut() == 'inventory_done')
        logging.getLogger().debug("isInventoryDone(#%s): %s" % (self.getId(), result))
        return result

    def setInventoryInProgress(self):
        self.setCommandStatut('inventory_in_progress')
    def isInventoryRunning(self):
        result = (self.getCommandStatut() == 'inventory_in_progress')
        logging.getLogger().debug("isInventoryRunning(#%s): %s" % (self.getId(), result))
        return result
    """
### /Handle inventory states ###

### Handle WOL states ###
    def isWOLImminent(self):
        result = (self.isStateScheduled() and self.isInTimeSlot())
        logging.getLogger().debug("isWOLImminent(#%s): %s" % (self.getId(), result))
        return result
    def wasWOLPreviouslyRan(self):
        result = (getLastWOLAttempt() != None) # should check if still in WOL delay
        logging.getLogger().debug("wasWOLPreviouslyRan(#%s): %s" % (self.getId(), result))
        return result

    def setWOLIgnored(self):
        self.setWOLStatut('IGNORED')
    def isWOLIgnored(self):
        result = (self.awoken == 'IGNORED')
        logging.getLogger().debug("isWOLIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setWOLFailed(self):
        self.setWOLStatut('FAILED')
    def isWOLFailed(self):
        result = (self.awoken == 'FAILED')
        logging.getLogger().debug("isWOLFailed(#%s): %s" % (self.getId(), result))
        return result

    def setWOLDone(self):
        self.setWOLStatut('DONE')
    def isWOLDone(self):
        result = (self.awoken == 'DONE')
        logging.getLogger().debug("isWOLDone(#%s): %s" % (self.getId(), result))
        return result

    def setWOLInProgress(self):
        self.setWOLStatut('WORK_IN_PROGRESS')
    def isWOLRunning(self):
        result = (self.awoken == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isWOLRunning(#%s): %s" % (self.getId(), result))
        return result

    def setLastWOLAttempt(self):
        self.last_wol_attempt = datetime.datetime.now()
        self.flush()
    def getLastWOLAttempt(self):
        return self.last_wol_attempt

    def setWOLToDo(self):
        self.setWOLStatut('TODO')
    def isWOLToDo(self):
        result = (self.awoken == 'TODO')
        logging.getLogger().debug("isWOLToDo(#%s): %s" % (self.getId(), result))
        return result

    def setWOLStatut(self, awoken):
        self.awoken = awoken
        self.flush()

    """
    def setWOLInProgress(self):
        self.setCommandStatut('wol_in_progress')
    def isWOLRunning(self):
        result = (self.getCommandStatut() == 'wol_in_progress')
        logging.getLogger().debug("isWOLRunning(#%s): %s" % (self.getId(), result))
        return result
    """
### /Handle wol states ###

### Handle reboot states ###
    def setRebootIgnored(self):
        self.setRebootIgnored('IGNORED')
    def isRebootIgnored(self):
        result = (self.rebooted == 'IGNORED')
        logging.getLogger().debug("isRebootIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setRebootFailed(self):
        self.setRebootStatut('FAILED')
    def isRebootFailed(self):
        result = (self.rebooted == 'FAILED')
        logging.getLogger().debug("isRebootFailed(#%s): %s" % (self.getId(), result))
        return result

    def setRebootDone(self):
        self.setRebootStatut('DONE')
    def isRebootDone(self):
        result = (self.rebooted == 'DONE')
        logging.getLogger().debug("isRebootDone(#%s): %s" % (self.getId(), result))
        return result

    def setRebootInProgress(self):
        self.setRebootStatut('WORK_IN_PROGRESS')
    def isRebootRunning(self):
        result = (self.rebooted == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isRebootRunning(#%s): %s" % (self.getId(), result))
        return result

    def setRebootToDo(self):
        self.setRebootStatut('TODO')
    def isRebootToDo(self):
        result = (self.rebooted == 'TODO')
        logging.getLogger().debug("isHRebootToDo(#%s): %s" % (self.getId(), result))
        return result

    def setRebootStatut(self, halted):
        self.rebooted = rebooted
        self.flush()
### /Handle halt states ###

### Handle halt states ###
    def setHaltIgnored(self):
        self.setHaltIgnored('IGNORED')
    def isHaltIgnored(self):
        result = (self.halted == 'IGNORED')
        logging.getLogger().debug("isHaltIgnored(#%s): %s" % (self.getId(), result))
        return result

    def setHaltFailed(self):
        self.setHaltStatut('FAILED')
    def isHaltFailed(self):
        result = (self.halted == 'FAILED')
        logging.getLogger().debug("isHaltFailed(#%s): %s" % (self.getId(), result))
        return result

    def setHaltDone(self):
        self.setHaltStatut('DONE')
    def isHaltDone(self):
        result = (self.halted == 'DONE')
        logging.getLogger().debug("isHaltDone(#%s): %s" % (self.getId(), result))
        return result

    def setHaltInProgress(self):
        self.setHaltStatut('WORK_IN_PROGRESS')
    def isHaltRunning(self):
        result = (self.halted == 'WORK_IN_PROGRESS')
        logging.getLogger().debug("isUploadRunning(#%s): %s" % (self.getId(), result))
        return result

    def setHaltToDo(self):
        self.setHaltStatut('TODO')
    def isHaltToDo(self):
        result = (self.halted == 'TODO')
        logging.getLogger().debug("isHaltToDo(#%s): %s" % (self.getId(), result))
        return result

    def setHaltStatut(self, halted):
        self.halted = halted
        self.flush()
### /Handle halt states ###

### Handle general states ###
    def setStateScheduled(self):
        self.setCommandStatut('scheduled')
    def isStateScheduled(self):
        result = (self.getCommandStatut() == 'scheduled' or self.getCommandStatut() == 're_scheduled')
        logging.getLogger().debug("isStateScheduled(#%s): %s" % (self.getId(), result))
        return result

    def setStateDone(self):
        self.setCommandStatut('done')
        self.setEndDate() # final state: we may write the date down
    def isStateDone(self):
        result = (self.getCommandStatut() == 'done')
        logging.getLogger().debug("isStateDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateFailed(self):
        self.setCommandStatut('failed')
        self.setEndDate() # final state: we may write the date down
    def isStateFailed(self):
        result = (self.getCommandStatut() == 'failed')
        logging.getLogger().debug("isStateFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateStopped(self):
        self.setCommandStatut('stop')
    def isStateStopped(self):
        result = (self.getCommandStatut() == 'stop' or self.getCommandStatut() == 'stopped')
        logging.getLogger().debug("isStateStopped(#%s): %s" % (self.getId(), result))
        return result

    def setStatePaused(self):
        self.setCommandStatut('pause')
    def isStatePaused(self):
        result = (self.getCommandStatut() == 'pause' or self.getCommandStatut() == 'paused')
        logging.getLogger().debug("isStatePaused(#%s): %s" % (self.getId(), result))
        return result
    def toggleStatePaused(self):
        if self.isStatePaused():
            self.setStateScheduled()
        else:
            self.setStatePaused()

    def setStateWolInProgress(self):
        self.setCommandStatut('wol_in_progress')
    def isStateWolInProgress(self):
        result = (self.getCommandStatut() == 'wol_in_progress')
        logging.getLogger().debug("isStateWolInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateWolDone(self):
        self.setCommandStatut('wol_done')
    def isStateWolDone(self):
        result = (self.getCommandStatut() == 'wol_done')
        logging.getLogger().debug("isStateWolDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateWolFailed(self):
        self.setCommandStatut('wol_failed')
    def isStateWolFailed(self):
        result = (self.getCommandStatut() == 'wol_failed')
        logging.getLogger().debug("isStateWolFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateUploadInProgress(self):
        self.setCommandStatut('upload_in_progress')
    def isStateUploadInProgress(self):
        result = (self.getCommandStatut() == 'upload_in_progress')
        logging.getLogger().debug("isStateUploadInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateUploadDone(self):
        self.setCommandStatut('upload_done')
    def isStateUploadDone(self):
        result = (self.getCommandStatut() == 'upload_done')
        logging.getLogger().debug("isStateUploadDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateUploadFailed(self):
        self.setCommandStatut('upload_failed')
    def isStateUploadFailed(self):
        result = (self.getCommandStatut() == 'upload_failed')
        logging.getLogger().debug("isStateUploadFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateExecutionInProgress(self):
        self.setCommandStatut('execution_in_progress')
    def isStateExecutionInProgress(self):
        result = (self.getCommandStatut() == 'execution_in_progress')
        logging.getLogger().debug("isStateExecutionInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateExecutionDone(self):
        self.setCommandStatut('execution_done')
    def isStateExecutionDone(self):
        result = (self.getCommandStatut() == 'execution_done')
        logging.getLogger().debug("isStateExecutionDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateExecutionFailed(self):
        self.setCommandStatut('execution_failed')
    def isStateExecutionFailed(self):
        result = (self.getCommandStatut() == 'execution_failed')
        logging.getLogger().debug("isStateExecutionFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateDeleteInProgress(self):
        self.setCommandStatut('delete_in_progress')
    def isStateDeleteInProgress(self):
        result = (self.getCommandStatut() == 'delete_in_progress')
        logging.getLogger().debug("isStateDeleteInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateDeleteDone(self):
        self.setCommandStatut('delete_done')
    def isStateDeleteDone(self):
        result = (self.getCommandStatut() == 'delete_done')
        logging.getLogger().debug("isStateDeleteDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateDeleteFailed(self):
        self.setCommandStatut('delete_failed')
    def isStateDeleteFailed(self):
        result = (self.getCommandStatut() == 'delete_failed')
        logging.getLogger().debug("isStateDeleteFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateInventoryInProgress(self):
        self.setCommandStatut('inventory_in_progress')
    def isStateInventoryInProgress(self):
        result = (self.getCommandStatut() == 'inventory_in_progress')
        logging.getLogger().debug("isStateInventoryInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateInventoryDone(self):
        self.setCommandStatut('inventory_done')
    def isStateInventoryDone(self):
        result = (self.getCommandStatut() == 'inventory_done')
        logging.getLogger().debug("isStateInventoryDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateInventoryFailed(self):
        self.setCommandStatut('inventory_failed')
    def isStateInventoryFailed(self):
        result = (self.getCommandStatut() == 'inventory_failed')
        logging.getLogger().debug("isStateInventoryFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateRebootInProgress(self):
        self.setCommandStatut('reboot_in_progress')
    def isStateRebootInProgress(self):
        result = (self.getCommandStatut() == 'reboot_in_progress')
        logging.getLogger().debug("isStateRebootInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateRebootDone(self):
        self.setCommandStatut('reboot_done')
    def isStateRebootDone(self):
        result = (self.getCommandStatut() == 'reboot_done')
        logging.getLogger().debug("isStateRebootDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateRebootFailed(self):
        self.setCommandStatut('reboot_failed')
    def isStateRebootFailed(self):
        result = (self.getCommandStatut() == 'reboot_failed')
        logging.getLogger().debug("isStateRebootFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateHaltInProgress(self):
        self.setCommandStatut('halt_in_progress')
    def isStateHaltInProgress(self):
        result = (self.getCommandStatut() == 'halt_in_progress')
        logging.getLogger().debug("isStateHaltInProgress(#%s): %s" % (self.getId(), result))
        return result

    def setStateHaltDone(self):
        self.setCommandStatut('halt_done')
    def isStateHaltDone(self):
        result = (self.getCommandStatut() == 'halt_done')
        logging.getLogger().debug("isStateHaltDone(#%s): %s" % (self.getId(), result))
        return result

    def setStateHaltFailed(self):
        self.setCommandStatut('halt_failed')
    def isStateHaltFailed(self):
        result = (self.getCommandStatut() == 'halt_failed')
        logging.getLogger().debug("isStateHaltFailed(#%s): %s" % (self.getId(), result))
        return result

    def setStateOverTimed(self):
        self.setCommandStatut('over_timed')
    def isStateOverTimed(self):
        result = (self.getCommandStatut() == 'over_timed')
        logging.getLogger().debug("isStateOverTimed(#%s): %s" % (self.getId(), result))
        return result

    def setStateUnreachable(self):
        self.setCommandStatut('not_reachable')
    def isStateUnreachable(self):
        result = (self.getCommandStatut() == 'not_reachable')
        logging.getLogger().debug("isStateUnreachable(#%s): %s" % (self.getId(), result))
        return result

    def setCommandStatut(self, current_state):
        self.current_state = current_state
        self.flush()
    def getCommandStatut(self):
        return self.current_state

    def isInTimeSlot(self):
        if self.next_launch_date:
            return time.mktime(self.next_launch_date.timetuple()) <= time.time()
        else:
            return True
### /Handle general states ###

### Handle launcher ###
    def setCurrentLauncher(self, launcher):
        self.current_launcher = launcher
        self.flush()
    def getCurrentLauncher(self):
        return self.current_launcher
### /Handle launcher ###

### Handle local proxy stuff ###
    def isProxyClient(self):
        # I'm a client if:
        # fk_use_as_proxy is set (ie I found a proxy server)
        # fk_use_as_proxy is not equal to my id (ie the proxy server is not me)
        result = (self.fk_use_as_proxy != None and self.fk_use_as_proxy != self.id)
        logging.getLogger().debug("isProxyClient(#%s): %s" % (self.getId(), result))
        return result
    def isProxyServer(self):
        # I'm a server if:
        # order_in_proxy is set (ie I have chance to become a server)
        # fk_use_as_proxy is equal to my id (ie the proxy server is me)
        result = (self.order_in_proxy != None and self.id == self.fk_use_as_proxy)
        logging.getLogger().debug("isProxyServer(#%s): %s" % (self.getId(), result))
        return result

    def getOrderInProxy(self):
        return self.order_in_proxy

    def setUsedProxy(self, coh_id):
        self.fk_use_as_proxy = coh_id
    def getUsedProxy(self):
        return self.fk_use_as_proxy

### /Handle local proxy stuff ###

### Misc state changes handling  ###
    def reSchedule(self, delay, decrement):
        """ Reschedule when something went wrong """
        if decrement:
            if self.attempts_left < 1: # no attempts left
                self.setStateFailed()
                return # nothing more to do, give up
            elif self.attempts_left == 1: # was the last attempt: tag as done, no rescheduling
                self.attempts_left -= 1
                self.flush()
                self.setStateFailed()
                return # nothing more to do, give up
            else: # reschedule in other cases
                self.attempts_left -= 1
        self.next_launch_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + delay * 60))
        self.flush()
        self.setStateScheduled()

    def switchToWOLFailed(self, delay = 0, decrement = True):
        """
            goes in "wol_failed" state only if we where in
            "wol_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setWOLFailed()                                 # set task status
        if self.isStateWOLInProgress():                     # normal flow
            self.setStateWOLFailed                          # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToWOLDone(self):
        """
            goes in "wol_done" state only if we where in
            "wol_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setWOLDone()                                   # set task status
        if self.isStateWOLInProgress():                     # normal flow
            self.setStateWOLDone()                          # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToUploadFailed(self, delay = 0, decrement = True):
        """
            goes in "upload_failed" state only if we where in
            "upload_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setUploadFailed()                              # set task status
        if self.isStateUploadInProgress():                  # normal flow
            self.setStateUploadFailed                       # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToUploadDone(self):
        """
            goes in "upload_done" state only if we where in
            "upload_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setUploadDone()                                # set task status
        if self.isStateUploadInProgress():                  # normal flow
            self.setStateUploadDone()                       # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToExecutionFailed(self, delay = 0, decrement = True):
        """
            goes in "execution_failed" state only if we where in
            "execution_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setExecutionFailed()                           # set task status
        if self.isStateExecutionInProgress():               # normal flow
            self.setStateExecutionFailed()                  # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToExecutionDone(self):
        """
            goes in "execution_done" state only if we where in
            "execution_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setExecutionDone()                             # set task status
        if self.isStateExecutionInProgress():               # normal flow
            self.setStateExecutionDone()                    # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToDeleteFailed(self, delay = 0, decrement = True):
        """
            goes in "delete_failed" state only if we where in
            "delete_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setDeleteFailed()                              # set task status
        if self.isStateDeleteInProgress():                  # normal flow
            self.setStateDeleteFailed()                     # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToDeleteDone(self):
        """
            goes in "delete_done" state only if we where in
            "delete_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setDeleteDone()                                # set task status
        if self.isStateDeleteInProgress():                  # normal flow
            self.setStateDeleteDone()                       # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToInventoryFailed(self, delay = 0, decrement = True):
        """
            goes in "inventory_failed" state only if we where in
            "inventory_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setInventoryFailed()                           # set task status
        if self.isStateInventoryInProgress():               # normal flow
            self.setStateInventoryFailed()                  # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToInventoryDone(self):
        """
            goes in "inventory_done" state only if we where in
            "inventory_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setInventoryDone()                             # set task status
        if self.isStateInventoryInProgress():               # normal flow
            self.setStateInventoryDone()                    # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToRebootFailed(self, delay = 0, decrement = True):
        """
            goes in "reboot_failed" state only if we where in
            "reboot_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setRebootFailed()                              # set task status
        if self.isStateRebootInProgress():                  # normal flow
            self.setStateRebootFailed()                     # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToRebootDone(self):
        """
            goes in "reboot_done" state only if we where in
            "reboot_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setRebootDone()                                # set task status
        if self.isStateRebootInProgress():                  # normal flow
            self.setStateRebootDone()                       # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToHaltFailed(self, delay = 0, decrement = True):
        """
            goes in "halt_failed" state only if we where in
            "halt_in_progress" state, reschedule stuff.
            Returns True if processing can continue (most likely never),
            False else.
        """
        self.reSchedule(delay, decrement)                   # always reschedule
        self.setHaltFailed()                                # set task status
        if self.isStateHaltInProgress():                    # normal flow
            self.setStateHaltFailed()                       # set command status
            return False                                    # break flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

    def switchToHaltDone(self):
        """
            goes in "halt_done" state only if we where in
            "halt_in_progress" state.
            Returns True if processing can continue,
            False else.
        """
        self.setHaltDone()                             # set task status
        if self.isStateHaltInProgress():               # normal flow
            self.setStateHaltDone()                    # set command status
            return True                                     # continue command flow
        else:                                               # other state (pause, stop, etc ...)
            return False                                    # simply break flow

### /Misc state changes handling  ###

    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.orm.create_session()
        session.save_or_update(self)
        session.flush()
        session.close()

    def toH(self):
        return {
            'id': self.id,
            'fk_commands': self.fk_commands,
            'host': self.host,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'current_state': self.current_state,
            'stage': self.stage,
            'awoken': self.awoken,
            'uploaded': self.uploaded,
            'executed': self.executed,
            'deleted': self.deleted,
            'rebooted': self.rebooted,
            'inventoried': self.inventoried,
            'halted': self.halted,
            'next_launch_date': self.next_launch_date,
            'attempts_left': self.attempts_left,
            'next_attempt_date_time': self.next_attempt_date_time,
            'current_launcher': self.current_launcher,
            'scheduler': self.scheduler,
            'last_wol_attempt': self.last_wol_attempt,
            'order_in_proxy': self.order_in_proxy,
            'fk_use_as_proxy': self.fk_use_as_proxy
        }

    def setStartDate(self):
        """
        Set start_date field to current time, only if the field has not been
        already set.
        """
        if not self.start_date:
            self.start_date = datetime.datetime.now()
        self.flush()

    def setEndDate(self):
        """
        Set end_date field to current time
        """
        self.end_date = datetime.datetime.now()
        self.flush()

def startCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setStateScheduled()
    myCommandOnHost.next_launch_date = "0000-00-00 00:00:00"
    myCommandOnHost.flush()

def stopCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.setStateStopped()
    if myCommandOnHost.isUploadRunning():
        myCommandOnHost.setUploadFailed()
    if myCommandOnHost.isExecutionRunning():
        myCommandOnHost.setExecutionFailed()
    if myCommandOnHost.isDeleteRunning():
        myCommandOnHost.setDeleteFailed()
    myCommandOnHost.next_launch_date = "2031-12-31 23:59:59"
    myCommandOnHost.flush()

def togglePauseCommandOnHost(coh_id):
    session = sqlalchemy.orm.create_session()
    myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
    session.close()
    myCommandOnHost.togglePaused()

