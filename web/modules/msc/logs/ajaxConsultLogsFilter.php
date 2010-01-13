<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

require_once("../../../modules/msc/includes/functions.php");
require_once("../../../modules/msc/includes/commands_xmlrpc.inc.php");
require_once("../../../modules/msc/includes/command_history.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = empty($_GET["filter"])                ? ''    : $_GET['filter'];
$start = empty($_GET["start"])                  ? 0     : $_GET["start"];

if (!empty($_GET["commands"])) {
    setCommandsFilter($_GET["commands"]);
}

# $count = count_all_commands_for_consult($filter);
list($count, $cmds) = get_all_commands_for_consult($start, $start + $maxperpage, $filter);

$a_cmd = array();
$a_date = array();
$a_creator = array();
$a_target = array();
$params = array();

$actionplay = new ActionPopupItem(_T("Start", "msc"),"msctabsplay","start","msc", "base", "computers");
$actionpause = new ActionPopupItem(_T("Pause", "msc"),"msctabspause","pause","msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"),"msctabsstop","stop","msc", "base", "computers");
$actionstatus  = new ActionPopupItem(_T("Status", "msc"), "msctabsstatus","status", "msc", "base", "computers");
$actionsinglestatus  = new ActionPopupItem(_T("Status", "msc"), "msctabssinglestatus","status", "msc", "base", "computers");
$actionstatus->setWidth("600");
$actionempty = new EmptyActionItem();
$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();

$n = null;

foreach ($cmds as $item) {
    $label = $item['title'];
    $creation_date = $item['creation_date'];
    $creator = $item['creator'];
    $target = $item['target'];
    $target_uuid = $item['uuid'];
    $cmd_id = $item['cmdid'];
    $bid = $item['bid'];
    $gid = $item['gid'];
    $current_state = $item['current_state'];
    $creation_date = _toDate($creation_date);
    $status = $item['status'];
    if ($status) { $icons = state_tmpl_macro($status); }
    else { $icons = state_tmpl($current_state); }
    $tab = 'tablogs';
    if ($icons['play'] == '' && $icons['stop'] == '' && $icons['pause'] == '') { $tab = 'tabhistory'; }
        
    if ($target_uuid && $target_uuid != '') {
        $linkdetail = urlStr("base/computers/msctabs/$tab", array('uuid'=>$target_uuid, 'cmd_id'=>$cmd_id, 'bundle_id'=>$bid, 'gid'=>$gid));
        $linklogs = urlStr("base/computers/msctabs/$tab", array('uuid'=>$target_uuid, 'gid'=>$gid));
    } else {
        $linkdetail = urlStr("base/computers/groupmsctabs/$tab", array('uuid'=>$target_uuid, 'cmd_id'=>$cmd_id, 'bundle_id'=>$bid, 'gid'=>$gid));
        $linklogs = urlStr("base/computers/groupmsctabs/$tab", array('uuid'=>$target_uuid, 'gid'=>$gid));
    }
    $a_date[] = $creation_date;
    $a_creator[] = $creator;
    $no_actions = False;
    if ($target == 'UNVISIBLEMACHINE') {
        $target = _T('Unavailable machine', 'msc');
        $a_cmd[] = $label;
        $a_target[] = $target;
        $no_actions = True;
    } elseif ($target == 'UNVISIBLEGROUP') {
        $target = _T('Unavailable group', 'msc');
        $a_cmd[] = $label;
        $a_target[] = $target;
        $no_actions = True;
    } else {
        $a_cmd[] = sprintf("<a href='%s' class='bundle' title='%s'>%s</a>", $linkdetail , $label, $label);
        $a_target[] = sprintf("<a href='%s' class='bundle' title='%s'>%s</a>", $linklogs, $target, $target);
    }

    $params[] = array('cmd_id'=>$cmd_id, 'title'=>$label, 'gid'=>$gid, 'bundle_id'=>$bid, 'gid'=>$gid);

    if ($no_actions) {
        $a_start[] = $actionempty;
        $a_stop[] = $actionempty;
        $a_pause[] = $actionempty;
        $a_details[] = $actionempty;
    } else {    
        if ($icons['play'] == '') { $a_start[] = $actionempty; } else { $a_start[] = $actionplay; }
        if ($icons['stop'] == '') { $a_stop[] = $actionempty; } else { $a_stop[] = $actionstop; }
        if ($icons['pause'] == '') { $a_pause[] = $actionempty; } else { $a_pause[] = $actionpause; }
        if ((!isset($bid) || $bid == '') && (!isset($gid) || $gid == '')) { # gid
            $a_details[] = $actionsinglestatus;
        } else {
            $a_details[] = $actionstatus;
        }
    }
}

$n = new OptimizedListInfos($a_cmd, _T("Command", "msc"));
$n->addExtraInfo($a_creator, _T("Creator", "msc"));
$n->addExtraInfo($a_date, _T("Creation date", "msc"));
$n->addExtraInfo($a_target, _T("Target", "msc"));

$n->addActionItemArray($a_start);
$n->addActionItemArray($a_pause);
$n->addActionItemArray($a_stop);
$n->addActionItemArray($a_details);

$n->disableFirstColumnActionLink(); # TODO put several columns actions
$n->setParamInfo($params);
$n->setTableHeaderPadding(1);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $maxperpage;

$n->display();

?>
<!-- inject styles -->
<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />

<style>
li.pause_old a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/stock_media-pause.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
a.bundle {
    text-decoration: none;
    color: #222222;
}


</style>
