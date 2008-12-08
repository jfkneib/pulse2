<?
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Hardware'; }

$uuid = '';
$hostname = '';
if (isset($_GET['uuid'])) { $uuid = $_GET['uuid']; }
if (isset($_GET['hostname'])) { $hostname = $_GET['hostname']; }

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("%s's inventory (GLPI)", "glpi"), $hostname), "modules/glpi/glpi/header.php");
$p->addTab("tab0", _T("Hardware", "glpi"), "", "modules/glpi/glpi/view_hardware.php", array('hostname'=>$hostname, 'uuid'=>$uuid));

$i = 1;
// TODO get the list with trads from agent (conf file...)
foreach (array('Network'=>_T('Network', "glpi"), 'Controller'=>_T('Controller', "glpi")) as $tab=>$str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('hostname'=>$hostname, 'uuid'=>$uuid, 'part' => $tab));
    $i++;
}

$p->display();

?>
