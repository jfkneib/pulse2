<?php
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

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
$p->addTop(sprintf(_T("Group creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
$p->addTab("tabdyn", _T("Dynamic group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", array());
$p->addTab("tabsta", _T("Static group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", array());
$p->addTab("tabfromfile", _T("Static group creation from import", "dyngroup"), "", "modules/dyngroup/dyngroup/import_from_file.php", array());
$p->display();

?>

