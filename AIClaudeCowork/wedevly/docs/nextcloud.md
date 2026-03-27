# Nextcloud — Dokumentation

Dieses Dokument beschreibt die Nextcloud-Installation für **cloud.devprops.de**.

---

## Übersicht

| Eigenschaft | Wert |
|---|---|
| URL | https://cloud.devprops.de |
| Server-Pfad | `/opt/mailserver/` |
| Container | `nextcloud` + `nextcloud-db` (MariaDB 10.11) |
| Interner Port | `8087` |
| Daten | `./nextcloud-data/`, `./nextcloud-db/` |
| Admin-Konto | `admin` (nur für Server-Verwaltung) |

Enthaltene Apps: **Mail**, **Kalender**, **Kontakte**, **Dateien**

---

## Benutzer

Jede Person hat einen eigenen Nextcloud-Login. Der Admin-Account hat **keine** Mailkonten.

| Nextcloud-Login | Mailkonto | Passwort |
|---|---|---|
| `frs49@devprops.de` | frs49@devprops.de | IMAP-Passwort (identisch) |
| `info@wedevly.de` | info@wedevly.de | IMAP-Passwort (identisch) |
| `admin` | — | nur Admin-Verwaltung |

---

## Zugang

| Dienst | URL |
|---|---|
| Nextcloud | https://cloud.devprops.de |
| Mail-App direkt | https://cloud.devprops.de/apps/mail |
| Kalender | https://cloud.devprops.de/apps/calendar |
| Kontakte | https://cloud.devprops.de/apps/contacts |

`mail.wedevly.de` und `mail.devprops.de` leiten direkt zur Mail-App weiter.

---

## CalDAV / CardDAV (Kalender & Kontakte sync)

| Protokoll | URL |
|---|---|
| CalDAV | `https://cloud.devprops.de/remote.php/dav` |
| CardDAV | `https://cloud.devprops.de/remote.php/dav` |

iOS und Android finden die Adresse automatisch via `.well-known` — einfach
`cloud.devprops.de` mit Login + Passwort eingeben.

---

## Benutzer verwalten (Admin)

### Neuen Benutzer anlegen

```bash
ssh server

# Passwort ohne Sonderzeichen:
OC_PASS='PASSWORT' docker exec --user www-data -e OC_PASS nextcloud \
  php occ user:add LOGIN --display-name="Anzeigename" --password-from-env

# Passwort MIT Sonderzeichen ($, %, &, ...):
python3 -c "
import subprocess, os, base64
pw = base64.b64decode('BASE64_DES_PASSWORTS').decode()
env = {**os.environ, 'OC_PASS': pw}
subprocess.run([
    'docker','exec','--user','www-data',
    '-e','OC_PASS','nextcloud','php','occ',
    'user:add','LOGIN',
    '--display-name=Anzeigename',
    '--password-from-env'
], env=env)
"
```

Base64 eines Passworts berechnen:
```bash
echo -n 'MeinPasswort!' | base64
```

### Benutzer auflisten

```bash
docker exec --user www-data nextcloud php occ user:list
```

### Passwort ändern

```bash
docker exec --user www-data nextcloud php occ user:resetpassword LOGIN
```

---

## Mailkonto in Nextcloud Mail einrichten

1. Als Benutzer einloggen → Mail-App öffnen (oder `mail.wedevly.de`)
2. Formular „Konto verbinden" erscheint automatisch beim ersten Mal
3. **Automatisch**-Modus:

| Feld | Wert |
|---|---|
| Name | beliebig |
| E-Mail-Adresse | z.B. `info@wedevly.de` |
| Passwort | IMAP-Passwort |

Nextcloud verbindet automatisch mit `mail.wedevly.de` auf Port 993 (IMAP) und 587 (SMTP).

---

## Nextcloud-Konfiguration anpassen

Nextcloud-Config liegt unter `./nextcloud-data/config/config.php` (auf dem Server).
Wichtige gesetzte Werte:

```bash
# Hinter nginx-Proxy — wichtig für korrekte URLs
docker exec --user www-data nextcloud php occ config:system:set overwriteprotocol --value='https'
docker exec --user www-data nextcloud php occ config:system:set overwrite.cli.url --value='https://cloud.devprops.de'
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 0 --value='127.0.0.1'

# Mail-App als Standard-Startseite (damit mail.wedevly.de direkt in der Mail-App landet)
docker exec --user www-data nextcloud php occ config:system:set defaultapp --value='mail'
```

---

## Apps installieren / aktivieren

```bash
# Verfügbare Apps suchen
docker exec --user www-data nextcloud php occ app:list

# App aktivieren
docker exec --user www-data nextcloud php occ app:enable APPNAME
```

---

## Nützliche Befehle

```bash
# Nextcloud-Logs
ssh server "docker logs nextcloud --tail 50"

# occ-Befehlsliste
ssh server "docker exec --user www-data nextcloud php occ list"

# Nextcloud neu starten
ssh server "docker restart nextcloud"

# Wartungsmodus ein/aus
docker exec --user www-data nextcloud php occ maintenance:mode --on
docker exec --user www-data nextcloud php occ maintenance:mode --off
```

---

## Sicherheit

### 2FA (Zwei-Faktor-Authentifizierung)

**Status: aktiv — 2FA ist für alle Benutzer erzwungen.**

Nextcloud nutzt TOTP (z.B. Bitwarden Authenticator, Aegis, Google Authenticator).
Beim nächsten Login erscheint automatisch ein QR-Code zum Einrichten.

```bash
# TOTP-App aktivieren (bereits aktiv)
docker exec --user www-data nextcloud php occ app:enable twofactor_totp

# 2FA für alle erzwingen (bereits gesetzt)
docker exec --user www-data nextcloud php occ twofactorauth:enforce --on

# 2FA deaktivieren (falls nötig)
docker exec --user www-data nextcloud php occ twofactorauth:enforce --off
```

### Brute-Force-Schutz

Zwei Schutzschichten sind aktiv:

1. **Nextcloud eingebaut** (`bruteforcesettings`-App): drosselt Login-Versuche pro IP automatisch.
2. **Fail2ban** (`/etc/fail2ban/jail.d/nextcloud.conf`): sperrt IPs nach 5 fehlgeschlagenen Logins
   für 1 Stunde auf Firewall-Ebene (nftables).

```bash
# Status prüfen
fail2ban-client status nextcloud

# Gesperrte IPs anzeigen
fail2ban-client status nextcloud | grep "Banned IP"

# IP manuell entsperren
fail2ban-client unban <IP>
```

Fail2ban-Config: `maxretry=5`, `findtime=600s`, `bantime=3600s`

---

## Backup

Nextcloud-Daten werden täglich um 03:00 Uhr nach OneDrive gesichert:

| Was | Wo auf OneDrive |
|---|---|
| Nextcloud-Daten | `Server-Backup/nextcloud-data/` |
| Datenbank | `Server-Backup/nextcloud-db/` |
