SET NAMES 'utf8';
charset utf8;

UPDATE BootService SET default_name = "D�marrer normalement" , default_desc = "D�marrage normal" WHERE id = 1;
UPDATE BootService SET default_name = "Enregistrer un poste dans Pulse2", default_desc = "Enregistrer ce poste sur le serveur Pulse2" WHERE id = 2;
UPDATE BootService SET default_name = "Cr�er une sauvegarde", default_desc = "Cr�er une sauvegarde pour cet ordinateur" WHERE id = 3;
UPDATE BootService SET default_name = "Boot sans disque", default_desc = "Charge un environnement sans disque puis donne la main" WHERE id = 4;
UPDATE BootService SET default_name = "Test de la m�moire", default_desc = "D�marre un test complet de la m�moire" WHERE id = 5;

UPDATE Menu SET default_name = "Menu de boot par d�faut", message = "-- Attention! Votre PC est en train d'�tre sauvegard� ou restaur�. Ne red�marrez pas!" WHERE id = 1;
UPDATE Menu SET default_name = "Menu de boot d'inscription", message = "-- Attention! Votre PC est en train d'�tre sauvegard� ou restaur�. Ne red�marrez pas!" WHERE id = 2;

UPDATE PostInstallScript SET default_name = "Date",         default_desc = "�crit la date courante dans le fichier C:\\date.txt" WHERE id = 1;
UPDATE PostInstallScript SET default_name = "Sysprep",      default_desc = "Copie sysprep.inf dans C:\\" WHERE id = 2;
UPDATE PostInstallScript SET default_name = "SID",          default_desc = "Change le SID et le nom Netbios" WHERE id = 3;
UPDATE PostInstallScript SET default_name = "Arr�t",        default_desc = "Arr�te l'ordinateur" WHERE id = 4;
UPDATE PostInstallScript SET default_name = "Debug",        default_desc = "Ouvre un shell de debug" WHERE id = 5;
UPDATE PostInstallScript SET default_name = "Redimensionnement de partition", default_desc = "La premi�re (et seule) partition FAT ou EXT2 sera redimensionn�e pour prendre la totalit� du disque dur." WHERE id = 6;
UPDATE PostInstallScript SET default_name = "Redimensionnement NTFS", default_desc = "La premi�re (et seule) partition NTFS sera redimensionn�e pour prendre la totalit� du disque dur." WHERE id = 7;
UPDATE PostInstallScript SET default_name = "Agent Pack",   default_desc = "Installe l'agent Pulse 2 Agent Pack (VNC, OpenSSH, OCS Inventory et la cl� SSH)." WHERE id = 8;
UPDATE PostInstallScript SET default_name = "ICH 5 sync",   default_desc = "Synchronisation du RAID1 pour les cartes ICH5, duplique le premier disque sur le second." WHERE id = 9;
