<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
extract($_POST);
?>
<div class="header">
    <h1>Go to package folder</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_pwd_package" />
        <?php
        $packageList = xmpp_packages_list();
        $options = "";

        foreach($packageList as $id=>$package)
        {
            if(isset($packageuuid) && $packageuuid == $package['uuid'])
            {
                $options .= "<option value='".$package['uuid']."' selected>".$package['name']."</option>";
            }
            else
                $options .= "<option value='".$package['uuid']."'>".$package['name']."</option>";
        }
        $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        echo'
        <table>
            <tr>
                <th width="16%">step label : </th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            if(isset($packageuuid))
            {
                echo '<td width="16%">
                    <input type="checkbox" checked 
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />Package uuid
                </td>
                <td width="25%">
                    <select name="packageuuid">'.$options.'</select>
                </td>';
            }
            else{
                echo '<td width="16%">
                    <input type="checkbox" 
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                }" />Package uuid
                    </td>
                    <td width="25%">
                        <select disabled name="packageuuid">'.$options.'</select>
                    </td>';
            }
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>