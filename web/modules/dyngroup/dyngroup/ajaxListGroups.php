<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/*require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require_once("../../../modules/dyngroup/includes/utilities.php");
require_once("../../../modules/dyngroup/includes/querymanager_xmlrpc.php");
require_once("../../../modules/dyngroup/includes/xmlrpc.php");
require_once("../../../modules/dyngroup/includes/request.php");
require("../../../modules/dyngroup/includes/dyngroup.php");*/
require("modules/pulse2/includes/profiles_xmlrpc.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$start = 0;
if (isset($_GET["start"])) {
    $start = $_GET['start'];
}

if(isset($_GET['type']))
    $is_gp = $_GET['type'];
else
    $is_gp = 0;

$params = array('min'=>$start, 'max'=>$start + $maxperpage, 'filter'=>$_GET["filter"]);
if ($is_gp && $is_gp == 1) { # Profile
    $list = getAllProfiles($params);
    $count = countAllProfiles($params);
} else {
    $list = getAllGroups($params);
    $count = countAllGroups($params);
}
$filter = $_GET["filter"];

$ids  = array();
$name = array();
$type = array();
$show = array();
$action_delete = array();
if ($is_gp != 1) {
    $delete = new ActionPopupItem(_T("Delete this group", 'dyngroup'), "delete_group", "supprimer", "id", "base", "computers");
} else {
    $delete = new ActionPopupItem(_T("Delete this profile", 'dyngroup'), "delete_group", "supprimer", "id", "base", "computers");
}
$empty = new EmptyActionItem();

foreach ($list as $group) {
    $ids[]=  array("id"=>$group->id, "gid"=>$group->id, "groupname"=> $group->name);
    $name[]= $group->getName();
    if ($group->isDyn()) {
        $type[]= (!$group->isRequest() ? sprintf(_T('result (%s)', 'dyngroup'), $group->countResult()) : _T('query', 'dyngroup'));
    } else {
        $type[]= _T('static group', 'dyngroup');
    }
    $show[]= ($group->canShow() ? _T('Visible', 'dyngroup') : _T('Hidden', 'dyngroup'));
    if ($group->is_owner == 1) {
        $action_delete[]= $delete;
    } else {
        $action_delete[]= $empty;
    }
}

if ($is_gp != 1) {
    $n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
} else {
    $n = new OptimizedListInfos($name, _T('Profile name', 'dyngroup'));
}
$n->setTableHeaderPadding(0);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $conf["global"]["maxperpage"];


if ($is_gp != 1) {
    $n->addExtraInfo($type, _T('Type', 'dyngroup'));
}
$n->addExtraInfo($show, _T('Display', 'dyngroup'));
$n->setParamInfo($ids);

if ($is_gp != 1) {
    $n->addActionItem(new ActionItem(_T("Display this group's content", 'dyngroup'), "display", "afficher", "id", "base", "computers"));
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupinvtabs","inventory","inventory", "base", "computers"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this group", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Share this group", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers"));
    if (in_array("msc", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "base", "computers", "grouptablogs"));
        $n->addActionItem(new ActionItem(_T("Software deployment on this group", "dyngroup"),"groupmsctabs","install","computer", "base", "computers"));
    }
} else {
    $n->addActionItem(new ActionItem(_T("Display this profile's content", 'dyngroup'), "display", "afficher", "id", "base", "computers"));
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupinvtabs","inventory","inventory", "base", "computers"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this profile", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Share this profile", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers"));
    if (in_array("msc", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"),"groupmsctabs","logfile","computer", "base", "computers", "grouptablogs"));
        $n->addActionItem(new ActionItem(_T("Software deployment on this profile", "dyngroup"),"groupmsctabs","install","computer", "base", "computers"));
    }
    if (in_array("imaging", $_SESSION["supportModList"])) {
        if (xmlrpc_isImagingInProfilePossible()) {
            $n->addActionItem(new ActionItem(_("Imaging management"),"groupimgtabs","imaging","computer", "base", "computers"));
        }
    }
}
$n->addActionItemArray($action_delete);
$n->addActionItem(new ActionItem(_T("Csv export", "dyngroup"),"csv","csv","computer", "base", "computers"));
$n->disableFirstColumnActionLink();

$n->display();
?>

