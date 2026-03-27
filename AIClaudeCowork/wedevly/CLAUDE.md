# wedevly.de — Server-Dokumentation

Diese Datei beschreibt den Server-Aufbau für das Projekt **wedevly.de**.
Sie ist für Claude Code auf einem neuen Rechner gedacht, damit Claude den Kontext kennt.

---

## Einrichtung auf einem neuen Rechner

### 1. SSH-Key einrichten

Papa gibt dir die Datei mit dem SSH-Key (privater Schlüssel). Speichere sie als `deploy-wedevly`:

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

### 2. Dieses Repository klonen

```bash
git clone https://github.com/<dein-username>/<dein-repo>.git
cd <dein-repo>
```

### 3. GitHub Actions einrichten

Im GitHub-Repo unter **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Wert |
|---|---|
| `SERVER_HOST` | `167.86.127.129` |
| `SSH_PRIVATE_KEY` | Inhalt der Datei `deploy-wedevly` (komplett, inkl. `-----BEGIN...-----`) |

---

## Server-Übersicht

| Eigenschaft | Wert |
|---|---|
| Hostname | vmd191373 (Contabo VPS) |
| Öffentliche IP | 167.86.127.129 |
| OS | Ubuntu 24.04 LTS |
| Deploy-User | `deploy-wedevly` |
| SSH-Key | `~/.ssh/deploy-wedevly` |

---

## Meine Website

| Eigenschaft | Wert |
|---|---|
| URL | https://wedevly.de |
| Webmail | https://mail.wedevly.de |
| Server-Pfad | `/opt/wedevly/` |
| Container | `wedevly` (nginx:alpine) |
| Interner Port | 8085 |

### Verzeichnisstruktur auf dem Server

```
/opt/wedevly/
├── docker-compose.yml
└── html/                ← Deine Website-Dateien (HTML, CSS, JS, Bilder)
    └── index.html
```

---

## Deployment

### Automatisch via GitHub Actions (empfohlen)

Datei `.github/workflows/deploy.yml` im Repo anlegen:

```yaml
name: Deploy Website

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Dateien auf Server kopieren
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy-wedevly
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          source: "html/*"
          target: /opt/wedevly/html/
          strip_components: 1

      - name: Container neu starten
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy-wedevly
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: sudo /opt/wedevly/restart.sh
```

Bei jedem `git push` auf `main` werden die Dateien automatisch deployed.

### Manuell via SCP

```bash
# Einzelne Datei
scp -i ~/.ssh/deploy-wedevly ./index.html deploy-wedevly@167.86.127.129:/opt/wedevly/html/

# Ganzer Ordner
scp -i ~/.ssh/deploy-wedevly -r ./html/* deploy-wedevly@167.86.127.129:/opt/wedevly/html/
```

### Container neu starten (manuell)

```bash
ssh -i ~/.ssh/deploy-wedevly deploy-wedevly@167.86.127.129 "sudo /opt/wedevly/restart.sh"
```

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

Nextcloud ersetzt Roundcube. Enthält: Mail, Kalender (CalDAV), Kontakte (CardDAV), Dateien.

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

Nextcloud erkennt automatisch IMAP/SMTP über `mail.wedevly.de`.

### Nextcloud-Benutzer

Jede Person hat einen eigenen Nextcloud-Login. Benutzername = E-Mail-Adresse.

| Nextcloud-Login | Mailkonto |
|---|---|
| `frs49@devprops.de` | frs49@devprops.de (devprops.de) |
| `info@wedevly.de` | info@wedevly.de (wedevly.de) |

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

Native E-Mail-Apps können direkt mit dem Mailserver verbunden werden — unabhängig von Nextcloud:

| Einstellung | Wert |
|---|---|
| IMAP-Server | `mail.wedevly.de` |
| IMAP-Port | `993` (SSL/TLS) |
| SMTP-Server | `mail.wedevly.de` |
| SMTP-Port | `587` (STARTTLS) |
| Benutzername | die vollständige E-Mail-Adresse |
| Passwort | das IMAP-Passwort des Kontos |

Hinweis: `mail.wedevly.de` und `mail.devprops.de` leiten im Browser auf `cloud.devprops.de` weiter — die IMAP/SMTP-Ports (993, 587) sind davon nicht betroffen.

---

## E-Mail-Server (Mailserver)

| Eigenschaft | Wert |
|---|---|
| IMAP | `mail.wedevly.de`, Port 993 (SSL) |
| SMTP | `mail.wedevly.de`, Port 587 (STARTTLS) |
| Server-Pfad | `/opt/mailserver/` |
| Container | `mailserver` (docker-mailserver) |

### Neues E-Mail-Konto anlegen

```bash
ssh server
docker exec -it mailserver setup email add neuerkonto@wedevly.de
```

Passwörter mit Sonderzeichen (`$`, `%`, `&` etc.) sicher setzen:
```bash
python3 -c "import subprocess; subprocess.run(['docker','exec','mailserver','setup','email','add','konto@domain.de','passwort'])"
```

---

## Backup

Website und Mailserver werden täglich um 03:00 Uhr automatisch nach OneDrive gesichert.
Das Backup-Script liegt unter `/opt/backup/scripts/backup_onedrive.sh` (Projekt: `server-backup`).

| Was | Wo auf OneDrive |
|---|---|
| Website-Dateien | `Server-Backup/wedevly/html/` |
| docker-compose.yml | `Server-Backup/wedevly/` |
| Mailserver-Config + DKIM-Keys | `Server-Backup/mailserver/config/` |
| Mailbox-Daten | `Server-Backup/mailserver/mail-data/` |
| Nextcloud DB (mysqldump) | `Server-Backup/nextcloud/nextcloud-db-backup.sql` |
| Nextcloud-Daten | `Server-Backup/nextcloud/data/` |

---

## Nützliche Befehle

```bash
# Website-Logs
ssh -i ~/.ssh/deploy-wedevly deploy-wedevly@167.86.127.129 \
  "docker logs wedevly --tail 50"

# Mail-Logs
ssh -i ~/.ssh/deploy-wedevly deploy-wedevly@167.86.127.129 \
  "docker logs mailserver --tail 50"
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
  ├─ wedevly.de          → Deine Website              ← hier arbeitest du
  ├─ mail.wedevly.de     → Redirect → cloud.devprops.de
  ├─ mail.devprops.de   → Redirect → cloud.devprops.de
  └─ cloud.devprops.de  → Nextcloud (Mail, Kalender, Kontakte) ← hier arbeitest du
```

---

## SSL-Zertifikate

Werden automatisch von Let's Encrypt verwaltet und erneuern sich alle 90 Tage selbst.
Du musst dich nicht darum kümmern.
