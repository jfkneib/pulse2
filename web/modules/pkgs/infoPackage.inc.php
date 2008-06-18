<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

/**
 * module declaration
 */
// hide msc module for the moment
$mod = new Module("pkgs");
$mod->setVersion("2.0.0");
$mod->setRevision("$Rev: 213 $");
$mod->setDescription(_T("Packages", "pkgs"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(800);


$submod = new SubModule("pkgs");
$submod->setDescription(_T("Packages", "pkgs"));
$submod->setImg('modules/pkgs/img/navbar/pkgs');
$submod->setDefaultPage("pkgs/pkgs/index");

$page = new Page("index", _T('Show all packages', 'pkgs'));
$submod->addPage($page);
$page = new Page("add", _T('Add a package', 'pkgs'));
$submod->addPage($page);
$page = new Page("edit", _T('Edit a package', 'pkgs'));
$submod->addPage($page);

$page = new Page("ajaxPackageList");
$page->setFile("modules/pkgs/pkgs/ajaxPackageList.php");
$page->setOptions(array("visible"=>False, "AJAX" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);


?>
