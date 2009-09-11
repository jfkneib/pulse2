<?php
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

require_once("modules/dyngroup/includes/includes.php");

if ($edition) {
    $target = 'computersgroupedit';
} else {
    $target = 'computersgroupcreator';
}
$subedition = false;
if (strlen($_GET['subedition']) && $_GET['subedition'] == '1') { $subedition = true; }

// getting request and id parameters
$id = idGet();
$group = new Group($id, true);
$request = quickGet('request');
if (strlen($request)) {
    $r = new Request();
    $r->parse($request);
    $request = $r;
} elseif (strlen($id)) {
   $r = new Request();
   $r->parse($group->getRequest());
   $request = $r;
} else {
    $request = new Request();
}

// a part of the request has to be removed 
if ($_GET['action'] == 'computersgroupsubedit' || $_GET['action'] == 'computersgroupcreatesubedit') {
    if (strlen(quickGet('sub_id'))) {
        $sub = $request->getSub(quickGet('sub_id'));
        quickSet('req', $sub->module);
        quickSet('add_param', $sub->crit);
        quickSet('value', $sub->val);
        $request->removeSub(quickGet('sub_id'));
    }
}
if ($_GET['action'] == 'computersgroupsubdel' || $_GET['action'] == 'computersgroupcreatesubdel') {
    $request->removeSub(quickGet('sub_id'));
}

// a new part has to be added to the request
if (quickGet('req') && quickGet('param')) {
    $sub = new SubRequest(quickGet('req'), quickGet('param'), quickGet('value'), quickGet('value2'));
    $request->addSub($sub);
}

// select the module in which a part of the request must be launch
//TODO put in class
$modules = getPossiblesModules();
if (count($modules) == 1) {
    quickSet('add_req', $modules[0]);
} else {
    $add_req = quickget('add_req');
    if (!isset($add_req) || count($add_req) == 0 || $add_req == '') {
        $default = getDefaultModule();
        quickSet('add_req', $default);
    }
    
    print "<table><tr><td>"._T("Choose the module you want to query : ", "dyngroup")."</td>";
    
    foreach ($modules as $name) {
        if ($name == quickGet('add_req')) {
            print "<td>$name</td>";
        } else {
            print "<td><a href='".
                urlStr("base/computers/$target", array(
                                                    'add_req'=>$name,
                                                    'request'=>$request->toURL(),
                                                    'id'=>$id
                )).
                "'>$name</a></td>";
        }
    }
    print "</tr></table>";
}

// criterion selection
//TODO put in class
if (quickGet('add_req')) {
    $criterion = getPossiblesCriterionsInModule(quickGet('add_req'));
    if (count($criterion) == 1) {
        quickSet('req', quickGet('add_req'));
        quickSet('add_param', $criterion[0]);
    } else {
        print "<table><tr><td>"._T("Choose your field : ", "dyngroup")."</td>";
        $modulo = 0;
        $field_per_line = 4;
        $multiline = -1;
        foreach ($criterion as $param_name) {
            if ($modulo%$field_per_line==0) {
                $multiline += 1;
                if ($multiline) { print "</tr><tr><td>&nbsp;</td>"; }
            }
            if ($param_name == quickGet('add_param')) {
                print "<td>$param_name</td>";
            } else {
                print "<td><a href='".
                    urlStr("base/computers/$target", array( 'req'=>quickGet('add_req'), 'add_param'=>$param_name, 'request'=>$request->toURL(), 'id'=>$id )).
                    "'>$param_name</a></td>";
            }
            $modulo += 1;
        }
        while ($multiline && $modulo%$field_per_line <= ($field_per_line-1) && $modulo%$field_per_line != 0) {
            print "<td>&nbsp;</td>";
            $modulo += 1;
        }
        print "</tr></table>";
    }
}

// allow to select/write a value for the criterion
//TODO put in class
if (quickGet('add_param')) {
    print "<form action='".  urlStr("base/computers/$target", array()).  "' method='POST'><table>";
    // need to be changed in getCriterionType (we don't use the second part of the array...
    $type = getTypeForCriterionInModule(quickGet('req'), quickGet('add_param'));
    print "<tr><td>".quickGet('req')." > ".quickGet('add_param')."</td><td>";
    switch ($type) { #$param[0]) {
        case 'string':
            print "<input name='value' type='text'></input>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
        case 'list':
            $module = clean(quickGet('req'));
            $criterion = clean(quickGet('add_param'));
            include("modules/dyngroup/includes/autocomplete.php");
            $auto = new Autocomplete($module, $criterion, quickGet('value'), $subedition);
            $auto->display();
            break;
        case 'double':
            $module = clean(quickGet('req'));
            $criterion = clean(quickGet('add_param'));
            include("modules/dyngroup/includes/double.php");
            $auto = new DoubleAutocomplete($module, $criterion, quickGet('value'), $subedition);
            $auto->display();
            break;
        case 'halfstatic':
            $module = clean(quickGet('req'));
            $criterion = clean(quickGet('add_param'));
            include("modules/dyngroup/includes/autocomplete.php");
            $auto = new Autocomplete($module, $criterion, quickGet('value'), $subedition);
            $auto->display();
            break;
        case 'bool':
            $b_label = _T("Add", "dyngroup");
            if ($subedition) {
                $b_label = _T("Modify", "dyngroup");
            }
            print "<select name='value'>";
            print "<option name='True' value='True'>"._T("Yes", "dyngroup")."</option>";
            print "<option name='False' value='False'>"._T("No", "dyngroup")."</option>";
            print "</select>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
        case 'true':
            print "<input type='hidden' value='True' name='value'/><input type='text' readonly value='"._T("Yes", "dyngroup")."'/>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
    } 
    print "</td><td>";
    print "<input type='hidden' name='req' value='".quickGet('req')."'/>";
    print "<input type='hidden' name='param' value='".quickGet('add_param')."'/>";
    print "<input type='hidden' name='request' value='".$request->toURL()."'/>";
    print "<input type='hidden' name='id' value='$id'/>";
    print "</td></tr>";
    print "</table></form>";
}

// display the request in detail
if (!$request->isEmpty()) {
    print "<hr/>";
    print "<h3>"._T("The request is : ", "dyngroup")."</h3>";
    if ($edition) {
        $request->displayReqListInfos(true, array('id'=>$id, 'gid'=>$id, 'target'=>$target, 'target_edit'=>'computersgroupsubedit', 'target_del'=>'computersgroupsubdel', 'request'=>$request->toS()));
    } else {
        $request->displayReqListInfos(true, array('id'=>$id, 'gid'=>$id, 'target'=>$target, 'target_edit'=>'computersgroupcreatesubedit', 'target_del'=>'computersgroupcreatesubdel', 'request'=>$request->toS(), 'tab'=>'tabdyn'));
    }
}

// display action buttons in the bottom
//TODO put in class
if (!$request->isEmpty())  {  # TODO check ACLs....
    print "<hr/>";
    print "<table>";
    print "<tr><td>";
    
    $b = new Button('base', 'computers', 'creator_step2');
    $url = urlStr("base/computers/creator_step2", array('id'=>$id, 'request'=>$request->toS()));
    print $b->getOnClickButton(_T("Go to save step", "dyngroup"), $url);

    print "</td><td>";
    print "</td></tr>";
    print "</table>";
}
?>
<style>
li.delete a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/delete.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>
