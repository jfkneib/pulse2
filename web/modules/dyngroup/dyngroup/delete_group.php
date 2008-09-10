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

$id = quickGet('gid');
$group = new Group($id, False);

if (quickGet('valid')) {
    $group->delete();
    header("Location: " . urlStrRedirect("base/computers/list" ));
}

?>
<h2><?= _T("Delete group", "dyngroup") ?></h2>
<?php

?>

<form action="<?= urlStr("base/computers/delete_group", array('gid'=>$id)) ?>" method="post">
<p>

<?  
    printf(_T("You will delete group <b>%s</b>.", "dyngroup"), $_GET["groupname"]);
?>

</p>
<input name='valid' type="submit" class="btnPrimary" value="<?= _T("Delete group", "dyngroup"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?= _T("Cancel", "dyngroup"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
    




