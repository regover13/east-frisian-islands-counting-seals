# devprops.de — Server-Dokumentation

Diese Datei beschreibt den Server-Aufbau (Contabo VPS, vmd191373).
Sie ist für Claude Code auf einem neuen Rechner gedacht, damit Claude den Kontext kennt.

---

## Einrichtung auf einem neuen Rechner

### 1. SSH-Key einrichten

Den privaten SSH-Key als `deploy-wedevly` speichern:

**Linux/macOS:**
```bash
mkdir -p ~/.ssh
cp deploy-wedevly ~/.ssh/deploy-wedevly
chmod 600 ~/.ssh/deploy-wedevly
```

**Windows (PowerShell):**
```powershell
mkdir "$env:USERPROFILE\.ssh" -Force
copy deploy-wedevly "$env:USERPROFILE\.ssh\deploy-wedevly"
icacls "$env:USERPROFILE\.ssh\deploy-wedevly" /inheritance:r /grant:r "$env:USERNAME:R"
```

Verbindung testen:
```bash
ssh -i ~/.ssh/deploy-wedevly deploy-wedevly@167.86.127.129
```

---

## Server-Übersicht

| Eigenschaft | Wert |
|---|---|
| Hostname | vmd191373 (Contabo VPS) |
| Öffentliche IP | 167.86.127.129 |
| OS | Ubuntu 24.04 LTS |
| Root-SSH | `ssh server` (Alias in Shell konfiguriert) |

---

## Nextcloud (cloud.devprops.de)

| Eigenschaft | Wert |
|---|---|
| URL | https://cloud.devprops.de |
| Admin-User | `admin` |
| Server-Pfad | `/opt/mailserver/` |
| Container | `nextcloud` + `nextcloud-db` (MariaDB) |
| Interner Port | 8087 |
| Daten | `./nextcloud-data/`, `./nextcloud-db/` |

Nextcloud enthält: Mail, Kalender (CalDAV), Kontakte (CardDAV), Dateien.

### CalDAV / CardDAV URLs

- CalDAV + CardDAV: `https://cloud.devprops.de/remote.php/dav`
- iOS/Android findet die URL automatisch via `.well-known`

### IMAP-Konto in Nextcloud Mail einrichten

1. `https://cloud.devprops.de` öffnen → Mail-App
2. Beim ersten Start erscheint „Konto verbinden" automatisch
3. Weiteres Konto: Mail-Einstellungen (unten links) → „Konto hinzufügen"

Eingaben im Formular (Modus: **Auto**):

| Feld | Wert |
|---|---|
| Name | beliebig (z.B. `Tobias`) |
| E-Mail-Adresse | z.B. `frs49@devprops.de` |
| Passwort | das IMAP-Passwort des Kontos |

Nextcloud erkennt automatisch IMAP/SMTP über `mail.devprops.de`.

### Nextcloud-Benutzer

Jede Person hat einen eigenen Nextcloud-Login. Benutzername = E-Mail-Adresse.

| Nextcloud-Login | Mailkonto |
|---|---|
| `frs49@devprops.de` | frs49@devprops.de (devprops.de) |

Admin-Konto (`admin`) hat **keine** Mailkonten — nur für Server-Verwaltung.

#### Neuen Nextcloud-Benutzer anlegen

```bash
ssh server
# Passwort ohne Sonderzeichen:
docker exec --user www-data nextcloud php occ user:add LOGINNAME \
  --display-name="Anzeigename" --password-from-env
# Passwort mit Sonderzeichen ($, %, &, ...):
python3 -c "import subprocess,os,base64; pw=base64.b64decode('BASE64PW').decode(); \
  env={**os.environ,'OC_PASS':pw}; subprocess.run(['docker','exec','--user','www-data', \
  '-e','OC_PASS','nextcloud','php','occ','user:add','LOGINNAME', \
  '--display-name=NAME','--password-from-env'],env=env)"
```

### IMAP/SMTP für native Apps (iOS, Thunderbird, Outlook)

| Einstellung | Wert |
|---|---|
| IMAP-Server | `mail.devprops.de` |
| IMAP-Port | `993` (SSL/TLS) |
| SMTP-Server | `mail.devprops.de` |
| SMTP-Port | `587` (STARTTLS) |
| Benutzername | die vollständige E-Mail-Adresse |
| Passwort | das IMAP-Passwort des Kontos |

Hinweis: `mail.devprops.de` leitet im Browser auf `cloud.devprops.de` weiter — die IMAP/SMTP-Ports (993, 587) sind davon nicht betroffen.

---

## E-Mail-Server (Mailserver)

| Eigenschaft | Wert |
|---|---|
| IMAP | `mail.devprops.de`, Port 993 (SSL) |
| SMTP | `mail.devprops.de`, Port 587 (STARTTLS) |
| Server-Pfad | `/opt/mailserver/` |
| Container | `mailserver` (docker-mailserver) |

### Neues E-Mail-Konto anlegen

```bash
ssh server
docker exec -it mailserver setup email add neuerkonto@devprops.de
```

Passwörter mit Sonderzeichen (`$`, `%`, `&` etc.) sicher setzen:
```bash
python3 -c "import subprocess; subprocess.run(['docker','exec','mailserver','setup','email','add','konto@devprops.de','passwort'])"
```

---

## Backup

Mailserver und Nextcloud werden täglich um 03:00 Uhr automatisch nach OneDrive gesichert.
Das Backup-Script liegt unter `/opt/backup/scripts/backup_onedrive.sh` (Projekt: `server-backup`).

| Was | Wo auf OneDrive |
|---|---|
| Mailserver-Config + DKIM-Keys | `Server-Backup/mailserver/config/` |
| Mailbox-Daten | `Server-Backup/mailserver/mail-data/` |
| Nextcloud DB (mysqldump) | `Server-Backup/nextcloud/nextcloud-db-backup.sql` |
| Nextcloud-Daten | `Server-Backup/nextcloud/data/` |

---

## Nützliche Befehle

```bash
# Mail-Logs
ssh server "docker logs mailserver --tail 50"

# Nextcloud-Logs
ssh server "docker logs nextcloud --tail 50"
```

---

## Netzwerk-Übersicht

```
Internet
  │
  ▼
nginx (auf dem Server)
  ├─ vault.devprops.de   → Passwortmanager von Papa  [kein Zugriff]
  ├─ mcp.devprops.de     → E-Mail-Tool von Papa       [kein Zugriff]
  ├─ tsbot.devprops.de   → TeamSpeak-Bot von Papa     [kein Zugriff]
  ├─ mail.devprops.de    → Redirect → cloud.devprops.de
  └─ cloud.devprops.de   → Nextcloud (Mail, Kalender, Kontakte)
```

---

## SSL-Zertifikate

Werden automatisch von Let's Encrypt verwaltet und erneuern sich alle 90 Tage selbst.
Du musst dich nicht darum kümmern.
