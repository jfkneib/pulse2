<?

/*
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');

$params = getParams();
$location = getCurrentLocation();

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$start = empty($_GET["start"]) || $_GET["start"] == ''    ? 0              : $_GET["start"];
$end = empty($_GET["end"]) || $_GET["end"] == ''          ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])                          ? ''             : $_GET['filter'];

list($count, $masters) = xmlrpc_getLocationImages($location, $start, $end, $filter);

// forge params
$addAction = new ActionPopupItem(_T("Add image to default boot menu", "imaging"), "master_add", "addbootmenu", "master", "imaging", "manage");
$emptyAction = new EmptyActionItem();
$addActions = array();

$a_label = array();
$a_desc = array();
$a_date = array();
$a_size = array();
$a_is_in_menu = array();

foreach ($masters as $master) {
    $l_params = array();
    $l_params = $params;
    $l_params["itemid"] = $master['imaging_uuid'];
    $l_params["itemlabel"] = urlencode($master['name']);

    if (!$master['menu_item']) {
        $addActions[] = $addAction;
    } else {
        $addActions[] = $emptyAction;
    }

    $list_params[] = $l_params;
    $a_label[] = $master['name'];
    $a_desc[] = $master['desc'];
    $a_date[] = _toDate($master['creation_date']);
    $a_size[] = humanReadable($master['size']);
    $a_is_in_menu[] = ($master['menu_item']?True:False);
}

// show images list
$l = new OptimizedListInfos($a_label, _T("Label", "imaging"));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_desc, _T("Description", "imaging"));
$l->addExtraInfo($a_date, _T("Created", "imaging"));
$l->addExtraInfo($a_size, _T("Size (compressed)", "imaging"));
$l->addExtraInfo($a_is_in_menu, _T("In default boot menu", "imaging"));
$l->addActionItemArray($addActions);
$l->addActionItem(
    new ActionPopupItem(_T("Create bootable iso", "imaging"),
    "master_iso", "backup", "master", "imaging", "manage")
);
$l->addActionItem(
    new ActionItem(_T("Edit image", "imaging"),
    "master_edit", "edit", "master", "imaging", "manage")
);
$l->addActionItem(
    new ActionPopupItem(_T("Delete", "imaging"),
    "master_delete", "delete", "master", "imaging", "manage")
);

$l->setTableHeaderPadding(1);
$l->disableFirstColumnActionLink();
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamformLevel2"));
$l->start = 0;
$l->end = $maxperpage;
$l->display();


?>
