<?
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

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

require_once("../../../modules/inventory/includes/xmlrpc.php");
require_once("../../../modules/base/includes/edit.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"];
$from = $_GET['from'];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

if ($_GET['uuid'] != '') {
    $table = $_GET['part'];
    $graph = getInventoryGraph($table);
    $inv = getLastMachineInventoryPart($table, array('uuid'=>$_GET["uuid"], 'filter'=>$filter, 'min'=>$start, 'max'=>($start + $maxperpage)));
    $count = countLastMachineInventoryPart($table, array('uuid'=>$_GET["uuid"], 'filter'=>$filter));

    /* display everything else in separated tables */
    $n = null;
    $h = array();
    $index = 0;
    if ($count > 0 and is_array($inv) and is_array($inv[0]) and is_array($inv[0][1])) {
        foreach ($inv[0][1] as $def) {
            foreach ($def as $k => $v) {
                $h[$k][$index] = $v;
            }
            $index+=1;
        }
    }
    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($table));
    foreach ($h as $k => $v) {
        if ($k != 'id' && $k != 'timestamp' && !in_array($k, $disabled_columns)) {
            if (in_array($k, $graph) && count($v) > 1) {
                $type = ucfirst($_GET['part']);
                # TODO should give the tab in the from param
                $nhead = _T($k, 'inventory')." <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&from=$from&field=$k";
                foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
                    $nhead .= "&$get=".$_GET[$get];
                }
                $nhead .= "' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
                $k = $nhead;
            } else {
                $k = _T($k, 'inventory');
            }

            if ($n == null) {
                $n = new OptimizedListInfos($v, $k);
            } else {
                $n->addExtraInfo($v, $k);
            }
        }
    }
    if ($n != null) {
        $n->setTableHeaderPadding(1);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $maxperpage;
        $n->display();
    }
    ?><a href='<?= urlStr("inventory/inventory/csv", array('table'=>$table, 'uuid'=>$_GET["uuid"])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a><?php
} else {
    $display = $_GET['part'];
    $machines = getLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'filter'=>$filter, 'min'=>$start, 'max'=>($start + $maxperpage)));
    $count = countLastMachineInventoryPart($display, array('gid'=>$_GET["gid"], 'filter'=>$filter));

    $result = array();
    $index = 0;
    $params = array();
    foreach ($machines as $machine) {
        $name = $machine[0];
        if (count($machine[1]) == 0) {
            $result['Machine'][$index] = $name;
            $index += 1;
        }
        foreach ($machine[1] as $element) {
            $result['Machine'][$index] = $name;
            foreach ($element as $head => $val) {
                if ($head != 'id' && $head != 'timestamp') {
                    $result[$head][$index] = $val;
                }
            }
            $index += 1;
        }
        $params[] = array('hostname'=>$machine[0], 'uuid'=>$machine[2]);
    }
    $n = null;
    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
    $graph = getInventoryGraph($display);
    foreach ($result as $head => $vals) {
        if (!in_array($head, $disabled_columns)) {
            if (in_array($head, $graph) && count($vals) > 1) {
                $type = ucfirst($_GET['part']);
                # TODO should give the tab in the from param
                $nhead = _T($head, 'inventory')." <a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&from=$from&field=$head";
                foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
                    $nhead .= "&$get=".$_GET[$get];
                }
                $nhead .= "' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
                $head = $nhead;
            } else {
                $head = _T($head, 'inventory');
            }
            if ($n == null) {
                $n = new OptimizedListInfos($vals, $head);
            } else {
                $n->addExtraInfo($vals, $head);
            }
        }
    }

    if ($n != null) {
        $n->addActionItem(new ActionItem(_T("View", "inventory"),"invtabs","voir","inventory", "base", "computers"));
        $n->addActionItem(new ActionPopupItem(_T("Informations", "inventory"),"infos","infos","inventory", "inventory", "inventory"));
        $n->setParamInfo($params);
        $n->setTableHeaderPadding(1);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $maxperpage;
        $n->display();
    }
    ?><a href='<?= urlStr("inventory/inventory/csv", array('table'=>$display, 'gid'=>$_GET["gid"], 'filter' => $_GET['filter'])) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a><?php
}

?>

</table>

