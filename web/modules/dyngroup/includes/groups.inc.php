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

function drawGroupShare($nonmemb, $members, $listOfMembers, $diff, $gid, $name) {
?>
<form action="<? echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<input name="name" value="<?= $name ?>" type="hidden" />
<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?= _T("All share entities", "dyngroup");?></h3>
    <select multiple size="15" class="list" name="nonmemb[]">
    <?php
    foreach ($diff as $idx => $user) {
        if ($user == "") { unset($nonmemb[$idx]); continue; }
        $style = '';
        $ma = preg_split("/##/", $idx);
        if ($ma[0] == 1) { $style = ' style="background-color: #eedd00;"'; }
        echo "<option$style value=\"".$idx."\">".$user."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="bdeluser" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
   <input type="image" name="badduser" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?= _T("Group share", "dyngroup"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
    <?php
    foreach ($members as $idx => $member) {
        if ($member == "") { unset($members[$idx]); continue; }
        $style = '';
        $ma = preg_split("/##/", $idx);
        if ($ma[0] == 1) { $style = ' style="background-color: #eedd00;"'; }
        echo "<option$style value=\"".$idx."\">".$member."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
  <div class="clearer"></div>
 </td>
</tr>
</table>
</div>

<input type="hidden" name="lnonmemb" value="<?php echo base64_encode(serialize($nonmemb)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
<input type="hidden" name="id" value="<?= $gid ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?= _("Cancel"); ?>" />
</form>

<style type="text/css">
<!--
#grouplist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 5px 5px 10px;
        margin: 0 5px 20px 0;
        width: 632px;
}

#grouplist div.list
{
        float: left;
}

select.list
{
        width: 250px;
}
-->
</style>

<?php
}

function drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $gid, $name, $filter = '', $type = 0) {
    if ($type == 0) {
        $label_name = _T('Group name', 'dyngroup');
        $label_visible = _T('Is the group visible', 'dyngroup');
        $label_members = _T("Group members", "dyngroup");
    } else {
        $label_name = _T('Profile name', 'dyngroup');
        $label_visible = _T('Is the profile visible', 'dyngroup');
        $label_members = _T("Profile members", "dyngroup");
    }
?>

<form action="<? echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<table style="border: none;" cellspacing="0">
<tr><td><?= $label_name; ?></td><td></td><td><input name="name" value="<?= $name ?>" type="text"/></td></tr>
<tr><td><?= $label_visible; ?></td><td></td><td>
    <input name='visible' value='show' <? if ($visibility == 'show') { echo 'checked'; }?> type='radio'/><?= _T('Yes', 'dyngroup') ?>, 
    <input name='visible' value='hide' <? if ($visibility != 'show') { echo 'checked'; }?> type='radio'/><?= _T('No', 'dyngroup') ?>
</td></tr>
<!-- add all group inupts -->
</table>

<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?= _T("All machines", "dyngroup");?></h3>
    <input name='filter' type='text' value='<?= $filter ?>'/>
    <input type="image" name="bfiltmachine" style="padding: 5px;" src="img/common/icn_show.gif" value = "-->"/>
    <br/><br/>
    <select multiple size="13" class="list" name="machines[]">
    <?php
    foreach ($diff as $idx => $machine) {
        if ($machine == "") { unset($machines[$idx]); continue; }
        echo "<option value=\"".$idx."\">".$machine."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="bdelmachine" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
   <input type="image" name="baddmachine" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?= $label_members; ?></h3>
    <select multiple size="15" class="list" name="members[]">
    <?php
    foreach ($members as $idx => $member) {
        if ($member == "") { unset($members[$idx]); continue; }
        echo "<option value=\"".$idx."\">".$member."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
  <div class="clearer"></div>
 </td>
</tr>
</table>
</div>

<input type="hidden" name="type" value="<?= $type; ?>" />
<input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($machines)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
<input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
<input type="hidden" name="id" value="<?= $gid ?>" />
<input type="submit" name="bconfirm" class="btnPrimary" value="<?= _("Confirm"); ?>" />
<input type="submit" name="breset" class="btnSecondary" value="<?= _("Cancel"); ?>" />
</form>

<style type="text/css">
<!--
#grouplist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 5px 5px 10px;
        margin: 0 5px 20px 0;
        width: 632px;
}

#grouplist div.list
{
        float: left;
}

select.list
{
        width: 250px;
}
-->
</style>

<?php
}
?>

