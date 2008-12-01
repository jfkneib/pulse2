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

require('modules/msc/includes/commands_xmlrpc.inc.php');

if (strlen($_GET['cmd_id'])) {
    $cmd_id = $_GET['cmd_id'];
    $status = get_command_on_group_status($cmd_id);
    $title = get_command_on_host_title($cmd_id);
    $title = sprintf(_T("Command '%s' state concerning <b>%s</b> computers", "msc"), $title, $status['total']);
} elseif (strlen($_GET['bundle_id'])) {
    $status = get_command_on_bundle_status($_GET['bundle_id']);
    $bdl = bundle_detail($_GET['bundle_id']);
    $cmd_nb = count($bdl[1]);
    $machines_nb = $status['total'] / count($bdl[1]);
    $title = sprintf(_T("Bundle '%s' state concerning <b>%s</b> commands on <b>%s</b> computers", "msc"), $bdl[0]['title'], $cmd_nb, $machines_nb);
} else {
    print _T("error : cmd_id or bundle_id must be given", "msc");
}

if (strlen($_GET['bundle_id']) && !strlen($_GET['cmd_id'])) {
    /* Change labels when displaying a bundle summary */
    $labels = array(
        array('success', array(
            _T("<b>No</b> package installation was successful", "msc"),
            _T("<b>One</b> package installation was successful", "msc"),
            _T('<b>%s</b> packages installation were successful', 'msc')
        )),
        array('stopped', array(
            _T("<b>No</b> package installation is stopped", "msc"),
            _T("<b>One</b> package installation is stopped", "msc"),
            _T('<b>%s</b> packages installation are stopped', 'msc')
        )),
        array('running', array(
            _T("<b>No</b> package installation is being done", "msc"),
            _T("<b>One</b> package installation is being done", "msc"),
            _T('<b>%s</b> packages installation are being done', 'msc')
        )),
        array('failure', array(
            _T('<b>No</b> package installation failed', 'msc'),
            _T('<b>One</b> package installation failed', 'msc'),
            _T('<b>%s</b> packages installation failed', 'msc')
        )),
        );
} else {
    $labels = array(
        array('success', array(
            _T('<b>No</b> computer was successfully deployed', 'msc'),
            _T('<b>One</b> computer was successfully deployed', 'msc'),
            _T('<b>%s</b> computers were successfully deployed', 'msc')
        )),
        array('stopped', array(
            _T('<b>No</b> computer is stopped', 'msc'),
            _T('<b>One</b> computer is stopped', 'msc'),
            _T('<b>%s</b> computers are stopped', 'msc')
        )),
        array('running', array(
            _T('<b>No</b> computer is running a deployement', 'msc'),
            _T('<b>One</b> computer is running a deployement', 'msc'),
            _T('<b>%s</b> computers are running a deployement', 'msc')
        )),
        array('failure', array(
            _T('<b>No</b> computer failed to deploy', 'msc'),
            _T('<b>One</b> computer failed to deploy', 'msc'),
            _T('<b>%s</b> computers failed to deploy', 'msc')
        )),
        );
}

$verbs = array(
    'running'=>array(_T('is', 'msc'), _T('are', 'msc')),
    'failure'=>array(_T('has', 'msc'), _T('have', 'msc'))
);
$slabels = array(
    'success'=>array(),
    'stopped'=>array(),
    'running'=>array(
        array('wait_up', _T('waiting to upload', 'msc'), 'sec_up', _T('(with %s already try)', 'msc')),
        array('run_up', _T('uploading', 'msc')),
        array('wait_ex', _T('waiting to execute', 'msc'), 'sec_ex', _T('(with %s already try)', 'msc')),
        array('run_ex', _T('executing', 'msc')),
        array('wait_rm', _T('waiting to suppress', 'msc'), 'sec_rm', _T('(with %s already try)', 'msc')),
        array('run_rm', _T('suppressing', 'msc'))
    ),
    'failure'=>array(
        array('fail_up', _T('failed during upload', 'msc'), 'conn_up', _T('(with %s beeing unreachable)', 'msc')),
        array('fail_ex', _T('failed during execution', 'msc'), 'conn_ex', _T('(with %s beeing unreachable)', 'msc')),
        array('fail_rm', _T('failed during suppression', 'msc'), 'conn_rm', _T('(with %s beeing unreachable)', 'msc'))
    )

);

?><h3><?= $title?>&nbsp;
<a href='<?= urlStr("base/computers/statuscsv", array('cmd_id'=>$cmd_id, 'bundle_id'=>$_GET['bundle_id'])) ?>'><img src='modules/msc/graph/csv.png' alt='export csv'/></a>
</h3>
 <table width='100%'> <?php

foreach ($labels as $l) {
    $s = $status[$l[0]];
    if ($s['total'][0] == '0') {
        print "<tr><td colspan='3'>".$l[1][0]." (".$s['total'][1]."%)</td></tr>";
    } elseif ($s['total'][0] == '1') {
        print "<tr><td colspan='3'>".$l[1][1]." (".$s['total'][1]."%)</td></tr>";
    } else {
        print "<tr><td colspan='3'>".sprintf($l[1][2], $s['total'][0])." (".$s['total'][1]."%)</td></tr>";
    }

    foreach ($slabels[$l[0]] as $sl) {
        $ss = $status[$l[0]][$sl[0]];
        print "<tr><td>&nbsp;&nbsp;&nbsp;</td><td colspan='2'>";
        if ($ss[0] == '0') {
            print _T('None', 'msc')." ".$verbs[$l[0]][0]." ";
        } elseif ($ss[0] == '1') {
            print _T('One', 'msc')." ".$verbs[$l[0]][0]." ";
        } else {
            print $ss[0]." ".$verbs[$l[0]][1]." ";
        }
        print $sl[1];
        if (count($sl) == 4) {
            print " ".sprintf($sl[3], $status[$l[0]][$sl[2]][0]);
        }
        print " (".$ss[1]."%)";
        print "</td></tr>";
    }
}

?> </table>
