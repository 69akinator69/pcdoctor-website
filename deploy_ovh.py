#!/usr/bin/env python3
"""
Script de synchronisation et déploiement FTP pour pcdoctor.tn (OVH Cloud)
Auteur : Mohamed Aissaoui (PCDOCTOR / Formateur IT)
"""
import ftplib
import base64
import os
import sys

HOST = 'ftp.cluster129.hosting.ovh.net'
USER = 'pcdoctj'
PASSWORD = base64.b64decode('TWVkYWtpbmF0b3IyMzY5').decode('utf-8')
LOCAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'online'))

print(f"Connexion au serveur FTP OVH ({HOST})...")

try:
    ftp = ftplib.FTP(HOST, timeout=30)
    ftp.login(USER, PASSWORD)
    ftp.set_pasv(True)
    print("✓ Connexion établie avec succès !")
except Exception as e:
    print(f"❌ Impossible de se connecter au FTP : {e}")
    print("Vérifiez votre connexion réseau (les réseaux universitaires/WiFi publics peuvent bloquer le port 21).")
    sys.exit(1)

def sync_folder(local_path, remote_path):
    try:
        ftp.cwd(remote_path)
    except Exception:
        print(f"+ Création dossier distant : {remote_path}")
        try:
            ftp.mkd(remote_path)
        except Exception:
            pass
        ftp.cwd(remote_path)

    remote_items = {}
    try:
        for name, facts in ftp.mlsd():
            remote_items[name] = facts
    except Exception:
        pass

    for item in sorted(os.listdir(local_path)):
        l_item = os.path.join(local_path, item)
        r_item = f"{remote_path}/{item}"

        if os.path.isdir(l_item):
            sync_folder(l_item, r_item)
            ftp.cwd(remote_path)
        elif os.path.isfile(l_item):
            l_sz = os.path.getsize(l_item)
            r_sz = None
            if item in remote_items and 'size' in remote_items[item]:
                try:
                    r_sz = int(remote_items[item]['size'])
                except Exception:
                    pass

            if r_sz == l_sz:
                continue

            print(f"  → Téléversement : {item} ({l_sz} octets)...")
            with open(l_item, 'rb') as fp:
                ftp.storbinary(f"STOR {item}", fp)
            print(f"  ✓ {item} synchronisé.")

print("\n--- DÉBUT DE LA SYNCHRONISATION VERS /www ---")
sync_folder(LOCAL_DIR, '/www')
ftp.quit()
print("\n✓ Déploiement terminé avec succès sur https://pcdoctor.tn !")
