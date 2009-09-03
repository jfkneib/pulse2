<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("modules/dyngroup/includes/groups.inc.php");

$name = quickGet('name', $p_first = True, $urldecode = False);
$id = quickGet('id');
$visibility = quickGet('visible');
$already_exists = false;

if ($id) {
    $group = new Group($id, true);
    if (!$name) { $name = $group->getName(); }
    if (!$visibility) { $visibility = $group->canShow(); }
    $already_exists = true;
} else {
    $group = new Group();
}

$members = unserialize(base64_decode($_POST["lmembers"]));
$machines = unserialize(base64_decode($_POST["lmachines"]));
$listOfMembers = unserialize(base64_decode($_POST["lsmembers"]));

if (isset($_POST["bdelmachine_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $ma = preg_split("/##/", $member);
            unset($members[$member]);
            unset($listOfMembers[$ma[1]]);
        }
    }
} elseif (isset($_POST['bfiltmachine_x'])) {
    $truncate_limit = getMaxElementsForStaticList();
    $listOfMachines = getRestrictedComputersList(0, $truncate_limit, array('get'=>array('cn', 'objectUUID'), 'filter'=>$_POST['filter']), False);
    $count = getRestrictedComputersListLen(array('filter'=>$_POST['filter']));
    if ($truncate_limit < $count) {
        new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine['cn']."##".$machine['objectUUID']] = $machine['cn'];
    }

} elseif (isset($_POST["baddmachine_x"])) {
    if (isset($_POST["machines"])) {
        foreach ($_POST["machines"] as $machine) {
            $ma = preg_split("/##/", $machine);
            $members[$machine] = $ma[0];
            $listOfMembers[$ma[1]] = array('hostname'=>$ma[0], 'uuid'=>$ma[1]);
        }
    }
} elseif (isset($_POST["bconfirm"]) and $name != '' and !xmlrpc_group_name_exists($name, $id)) {
    $listOfCurMembers = $group->members();
    $curmem = array();
    foreach ($listOfCurMembers as $member) {
        $curmem[$member['hostname']."##".$member['uuid']] = $member['hostname'];
    }

    if (!$curmem) { $curmem = array(); }
    if (!$listOfCurMembers) { $listOfCurMembers = array(); }

    $listN = array();
    $listC = array();
    foreach ($listOfMembers as $member) { $listN[$member['uuid'].'##'.$member['hostname']] = $member; }
    foreach ($listOfCurMembers as $member) { $listC[$member['uuid'].'##'.$member['hostname']] = $member; }

    $newmem = array_diff_assoc($listN, $listC);
    $delmem = array_diff_assoc($listC, $listN);
    
    if ($group->id) {
        $group->setName($name);
        if ($visibility == 'show') { $group->show(); } else { $group->hide(); }
    } else {
        $group->create($name, ($visibility == 'show'));
    }
    
    $res = $group->delMembers($delmem) && $group->addMembers($newmem);
    
    if ($res) {
        if ($already_exists) {
            new NotifyWidgetSuccess(_T("Group successfully modified", "dyngroup"));
        } else {
            new NotifyWidgetSuccess(_T("Group successfully created", "dyngroup"));
        }
        $list = $group->members();
        $members = array();
        foreach ($list as $member) {
            $listOfMembers[$member['uuid']] = $member;
            $members[$member['hostname']."##".$member['uuid']] = $member['hostname'];
        }
        if ($visibility == 'show') {
            header("Location: " . urlStrRedirect("base/computers/computersgroupcreator", array('tab'=>'tabsta', 'id'=>$group->id)));
        }
    } else {
        new NotifyWidgetFailure(_T("Group failed to modify", "dyngroup"));
    }
} elseif (isset($_POST["bconfirm"]) and $name == '') {
    new NotifyWidgetFailure(_T("You must specify a group name", "dyngroup"));
} elseif (isset($_POST["bconfirm"]) and xmlrpc_group_name_exists($name, $id)) {
    new NotifyWidgetFailure(sprintf(_T("A group already exists with name '%s'", "dyngroup"), $name));
} else {
    $list = $group->members();
    $members = array();
    foreach ($list as $member) {
        $members[$member['hostname']."##".$member['uuid']] = $member['hostname'];
        $listOfMembers[$member['uuid']] = $member;
    }

    if (!$members) { $members = array(); }
    if (!$listOfMembers) { $listOfMembers = array(); }
    
    $truncate_limit = getMaxElementsForStaticList();
    $listOfMachines = getRestrictedComputersList(0, $truncate_limit, array('get'=>array('cn', 'objectUUID')), False);
    $count = getRestrictedComputersListLen();
    if ($truncate_limit < $count) {
        new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers", "dyngroup"), $truncate_limit));
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine['cn']."##".$machine['objectUUID']] = $machine['cn'];
    }
}
ksort($members);
reset($members);
ksort($machines);

$diff = array_diff_assoc($machines, $members);
natcasesort($diff);

drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $group->id, htmlspecialchars($name), $_POST['filter']);

?>

