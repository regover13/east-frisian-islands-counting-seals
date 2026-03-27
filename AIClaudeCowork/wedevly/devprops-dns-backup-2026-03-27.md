# devprops.de — DNS Backup vom 2026-03-27

Originalzustand vor der Migration von mail.networklabs.de → mail.wedevly.de.
28 Records insgesamt.

## Alle Records (original)

| Name | Typ | TTL | Daten | Status |
|---|---|---|---|---|
| `_autodiscover._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GELÖSCHT** |
| `_dmarc.devprops.de` | TXT | 86400 | v=DMARC1; p=reject; rua=mailto:postmaster@mail.networklabs.de; ruf=mailto:postmaster@mail.networklabs.de; adkim=s; aspf=s | **GEÄNDERT** |
| `_imap._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GELÖSCHT** |
| `_imaps._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `_pop3._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GELÖSCHT** |
| `_pop3s._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GELÖSCHT** |
| `_submission._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `_submissions._tcp.devprops.de` | SRV | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `autoconfig.devprops.de` | CNAME | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `autodiscover.devprops.de` | CNAME | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `brevo1._domainkey.devprops.de` | CNAME | 86400 | b1.devprops-de.dkim.brevo.com | unverändert |
| `brevo2._domainkey.devprops.de` | CNAME | 86400 | b2.devprops-de.dkim.brevo.com | unverändert |
| `devprops.de` | A | 86400 | 167.86.127.129 | unverändert |
| `devprops.de` | MX | 86400 | mail.networklabs.de | **GEÄNDERT** → mail.wedevly.de |
| `devprops.de` | NS | 86400 | ns1.contabo.net | unverändert |
| `devprops.de` | NS | 86400 | ns2.contabo.net | unverändert |
| `devprops.de` | NS | 86400 | ns3.contabo.net | unverändert |
| `devprops.de` | SOA | 3600 | ns1.contabo.net. hostmaster.contabo.de. 2026032704 10800 3600 604800 3600 | unverändert |
| `devprops.de` | TXT | 86400 | v=spf1 mx a:mail.networklabs.de include:spf.brevo.com ~all | **GEÄNDERT** → v=spf1 mx include:spf.brevo.com ~all |
| `devprops.de` | TXT | 86400 | brevo-code:3854d98d47260198e7e61fad82af1462 | unverändert |
| `devprops.de._report._dmarc.mail.networklabs.de.devprops.de` | TXT | 86400 | v=DMARC1 | **GELÖSCHT** |
| `dkim._domainkey.devprops.de` | TXT | 86400 | k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuwqm6ARHX99l6M8B2S+tlGmepR31qpGKv32s9oT36wuE1zEmGngDCVI13tqLqCJHAiqA5tzS/5JE88FeCToHDwgH2G8J2ivflrGYve+PML/hH4OGXvqN1i7yn0BkKG1sIfJTTghSf8iDSa3ugSOOuggrC9JbOSWI/42MWG4Eknd3xYy55JcLTFXFBqRlptPPq5FeiWx1vbKIRoeDFLxjdRm6tkEQc0eF4x15+k0K+iYsQdOmMt3/J0NIZeZS7rZsYP1PAoaubznVmDmvaWXTignmVgdlZXz4OjUxQW8l1g0iy3nRRBreW2b2VB+458rjKl2gfzir5ZzK1qRJJqDgEQIDAQAB | **GELÖSCHT** (alter networklabs DKIM-Key) |
| `mcp.devprops.de` | A | 3600 | 167.86.127.129 | unverändert |
| `portainer.devprops.de` | A | 3600 | 167.86.127.129 | unverändert |
| `tsbot.devprops.de` | A | 3600 | 167.86.127.129 | unverändert |
| `tsbot.devprops.de` | AAAA | 3600 | 2a02:c207:3019:1373::1 | unverändert |
| `vault.devprops.de` | A | 3600 | 167.86.127.129 | unverändert |
| `www.devprops.de` | CNAME | 86400 | devprops.de | unverändert |

## Durchgeführte Änderungen

### Gelöscht (nicht mehr benötigt)
- `_autodiscover._tcp` SRV → mail.networklabs.de (veraltet, autodiscover CNAME reicht)
- `_imap._tcp` SRV → mail.networklabs.de (veraltet, _imaps reicht)
- `_pop3._tcp` SRV → mail.networklabs.de (POP3 unverschlüsselt, nicht nutzen)
- `_pop3s._tcp` SRV → mail.networklabs.de (POP3 komplett nicht nutzen)
- `devprops.de._report._dmarc.mail.networklabs.de.devprops.de` TXT (verwaister DMARC-Report-Record)
- `dkim._domainkey.devprops.de` TXT (alter DKIM-Key von mail.networklabs.de)

### Geändert (→ mail.wedevly.de)
- MX: mail.networklabs.de → mail.wedevly.de
- SPF: `a:mail.networklabs.de` entfernt, `include:spf.brevo.com` bleibt
- DMARC: postmaster@mail.networklabs.de → postmaster@devprops.de
- SRV `_imaps._tcp`, `_submission._tcp`, `_submissions._tcp` → mail.wedevly.de
- CNAME `autoconfig`, `autodiscover` → mail.wedevly.de

### Unverändert (Brevo + Server-Records)
- brevo1/brevo2 DKIM-CNAMEs (Brevo Transaktionsmails)
- brevo-code TXT
- A-Records (mcp, portainer, tsbot, vault, www)
- NS, SOA Records
