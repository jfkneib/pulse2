 <?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

// load ZabbixApi
require("modules/monitoring/includes/ZabbixApiAbstract.class.php");
require("modules/monitoring/includes/ZabbixApi.class.php");
require("modules/monitoring/includes/functions.php");
require_once("modules/monitoring/includes/xmlrpc.php");

require("graph/navbar.inc.php");
require("localSidebar.php");

if (isset($_GET['apiId']))
	$apiId = $_GET['apiId'];
else {
	new NotifyWidgetFailure(_T("No api authentification token found!!!", "monitoring"));
	return;
}
if (isset($_GET['hostid']))
	$hostid = $_GET['hostid'];
else {
	new NotifyWidgetFailure(_T("No host id found!!!", "monitoring"));
	return;
}

$p = new PageGenerator(_T("Delete Graph", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();

// Display result
if (isset($_POST['bvalid'])) {
	$graph = $_POST['graph'];

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);
		$graphid = $api->graphDelete(array(
			$graph
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));
	}
	new NotifyWidgetSuccess("Graph deleted");
	redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));

}
// Display field
else {

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);
		$graph = $api->graphGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));
	}

	$f->push(new Table());

	$graphName = array();
	$graphId = array();

	foreach ($graph as $i) {
		$graphName[] = $i->name;
		$graphId[] = $i->graphid;
	}

	$graphs = new SelectItem("graph");
	$graphs->setElements($graphName);
	$graphs->setElementsVal($graphId);

	$f->add(
	    new TrFormElement("Select a Graph", $graphs)
	);
	
	$f->pop();
	$f->addButton("bvalid", _T("Delete"), "monitoring");
	$f->pop();
	$f->display();

} 
