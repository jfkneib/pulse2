<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id: mail-xmlrpc.php 75 2007-09-10 12:34:33Z cedric $
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

function getPublicImagesList() {
    return xmlCall("imaging.getPublicImagesList", null);
}

function getPublicImageInfos($imagename) {
    return xmlCall("imaging.getPublicImageInfos", array($imagename));
}

function delPublicImage($imagename) {
    return xmlCall("imaging.deletePublicImage", array($imagename));
}

function dupPublicImage($imagename, $newimagename) {
    if (!xmlCall("imaging.getPublicImageInfos", array($imagename))) {
        return xmlCall("imaging.duplicatePublicImage", array($imagename, $newimagename));
    } else { # the image already exists FIXME: should handle exception a better way
        return False;
    }
        
}

?>
