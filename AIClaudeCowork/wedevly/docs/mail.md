# E-Mail — Dokumentation

Dieses Dokument beschreibt die E-Mail-Infrastruktur für **wedevly.de** und **devprops.de**.

---

## Übersicht

| Eigenschaft | Wert |
|---|---|
| Mailserver | docker-mailserver (Postfix + Dovecot) |
| Server-Pfad | `/opt/mailserver/` |
| Container | `mailserver` |
| IMAP | `mail.wedevly.de`, Port **993** (SSL/TLS) |
| SMTP | `mail.wedevly.de`, Port **587** (STARTTLS) |
| Webzugang | https://cloud.devprops.de/apps/mail |

Die Domains `mail.wedevly.de` und `mail.devprops.de` leiten im Browser direkt zur
Nextcloud-Mail-App weiter. IMAP- und SMTP-Ports (993, 587) sind davon **nicht** betroffen.

---

## E-Mail-Konten

| Adresse | Typ | Person |
|---|---|---|
| `info@wedevly.de` | Postfach | wedevly-Account |
| `frs49@devprops.de` | Postfach | devprops-Account |
| `postmaster@wedevly.de` | Systemadresse | Bounce-/Fehlerempfang |

---

## Neues E-Mail-Konto anlegen

```bash
ssh server
docker exec -it mailserver setup email add neukonto@wedevly.de
# → gibt Passwort-Prompt aus
```

Bei Passwörtern mit Sonderzeichen (`$`, `%`, `&` etc.) **nicht** die Shell benutzen —
stattdessen Python verwenden:

```bash
python3 -c "
import subprocess
subprocess.run([
    'docker','exec','mailserver',
    'setup','email','add','konto@wedevly.de','PASSWORT'
])
"
```

---

## Passwort eines Kontos ändern

```bash
ssh server
docker exec -it mailserver setup email update konto@wedevly.de
```

---

## Konto löschen

```bash
ssh server
docker exec -it mailserver setup email del konto@wedevly.de
```

---

## E-Mail-Konto in Nextcloud Mail einrichten

1. `https://cloud.devprops.de/apps/mail` öffnen (oder über `mail.wedevly.de` / `mail.devprops.de`)
2. Beim ersten Öffnen erscheint automatisch das Setup-Formular
3. Modus **Automatisch** wählen:

| Feld | Wert |
|---|---|
| Name | beliebig |
| E-Mail-Adresse | z.B. `info@wedevly.de` |
| Passwort | das IMAP-Passwort dieses Kontos |

Nextcloud erkennt automatisch IMAP (993) und SMTP (587) auf `mail.wedevly.de`.

---

## Native Apps einrichten (iOS, Android, Thunderbird, Outlook)

Native E-Mail-Apps können direkt — ohne Nextcloud — auf den Mailserver zugreifen:

| Einstellung | Wert |
|---|---|
| IMAP-Server | `mail.wedevly.de` |
| IMAP-Port | `993` |
| IMAP-Sicherheit | SSL/TLS |
| SMTP-Server | `mail.wedevly.de` |
| SMTP-Port | `587` |
| SMTP-Sicherheit | STARTTLS |
| Benutzername | vollständige E-Mail-Adresse |
| Passwort | das IMAP-Passwort |

---

## DNS-Einträge (devprops.de)

Damit E-Mails korrekt zugestellt werden und nicht im Spam landen:

| Record | Typ | Wert |
|---|---|---|
| `devprops.de` | MX | `mail.wedevly.de` |
| `devprops.de` | TXT (SPF) | `v=spf1 mx include:spf.brevo.com ~all` |
| `_dmarc.devprops.de` | TXT (DMARC) | `v=DMARC1; p=reject; rua=mailto:postmaster@devprops.de; adkim=s; aspf=s` |
| `_imaps._tcp.devprops.de` | SRV | `mail.wedevly.de` |
| `_submission._tcp.devprops.de` | SRV | `mail.wedevly.de` |
| `autoconfig.devprops.de` | CNAME | `mail.wedevly.de` |
| `autodiscover.devprops.de` | CNAME | `mail.wedevly.de` |

DKIM-Key für wedevly.de liegt unter `/opt/mailserver/config/opendkim/keys/wedevly.de/`.

---

## Logs

```bash
# Letzte 50 Zeilen Mailserver-Log
ssh server "docker logs mailserver --tail 50"

# Postfix SMTP-Log live verfolgen
ssh server "docker exec mailserver tail -f /var/log/mail/mail.log"
```

---

## Backup

Mailserver-Daten werden täglich um 03:00 Uhr nach OneDrive gesichert:

| Was | Wo auf OneDrive |
|---|---|
| Mailbox-Daten | `Server-Backup/mailserver/mail-data/` |
| Config + DKIM-Keys | `Server-Backup/mailserver/config/` |
