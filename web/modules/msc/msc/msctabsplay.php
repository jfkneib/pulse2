<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');

if (isset($_POST["bconfirm"])) {
    /* Form handling */
    $from = $_POST['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    if ($_POST['gid'] != '') {
        $coh_id = $_POST["coh_id"];
        $cmd_id = $_POST["cmd_id"];
        $gid = $_POST["gid"];
        start_command_on_host($coh_id);
        header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'cmd_id'=>$cmd_id, 'gid'=>$gid)));
    } else {
        $hostname = $_POST["hostname"];
        $uuid = $_POST["uuid"];
        $coh_id = $_POST["coh_id"];
        start_command_on_host($coh_id);
        header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname)));
    }
} else {
    /* Form displaying */
    $from = $_GET['from'];
    $hostname = $_GET["hostname"];
    $uuid = $_GET["uuid"];
    $cmd_id = $_GET["cmd_id"];
    $coh_id = $_GET["coh_id"];
    $gid = $_GET["gid"];
    $cmd = command_detail($cmd_id);
    $name = $cmd['title'];

    $f = new PopupForm(sprintf(_T("Start action %s on host %s", 'msc'), $name, $hostname));
    $f->add(new HiddenTpl("name"),      array("value" => $hostname, "hide" => True));
    $f->add(new HiddenTpl("from"),      array("value" => $from,     "hide" => True));
    $f->add(new HiddenTpl("cmd_id"),    array("value" => $cmd_id,   "hide" => True));
    $f->add(new HiddenTpl("coh_id"),    array("value" => $coh_id,   "hide" => True));
    $f->add(new HiddenTpl("uuid"),      array("value" => $uuid,     "hide" => True));
    $f->add(new HiddenTpl("gid"),       array("value" => $gid,      "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}


?>
