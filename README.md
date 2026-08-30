# TeslaMate QNAP Installer

Eine möglichst einfache, vollständig browserbasierte Installation und Verwaltung des **unveränderten** [TeslaMate](https://github.com/teslamate-org/teslamate)-Stacks auf QNAP Container Station 3.

> **Inoffizielles Community-Projekt; nicht verbunden mit oder unterstützt von den jeweiligen Herstellern.** Tesla, TeslaMate und QNAP werden ausschließlich beschreibend genannt. Es werden keine fremden Logos verwendet. Nutzung ohne Gewährleistung und auf eigenes Risiko.

## Voraussetzungen und Sicherheit

- QNAP mit Container Station 3, mindestens 2 GB freiem RAM und `x86_64/amd64` oder 64-Bit ARMv8/`arm64`.
- Nicht unterstützt: ARMv7/32-Bit (`armhf`), x86/32-Bit, MIPS und andere Architekturen. Der Manager lehnt sie zusätzlich zur QNAP-Plattformfilterung ab.
- Ausgehender Internetzugang zu GHCR, Docker Hub und Tesla-Diensten.
- Der Manager bindet `/var/run/docker.sock` ein. Damit besitzt er technisch Docker-Administratorrechte auf dem NAS. Dies ist für die containerübergreifenden Backup-, Update- und Recreate-Funktionen erforderlich. Das Manager-Image ist klein, läuft ohne `privileged`, verwaltet nur eindeutig mit `teslamate-qnap` benannte/gelabelte Objekte und bietet keine beliebige Kommandoeingabe. **Port 8888 niemals im Router oder Reverse Proxy freigeben.**
- TeslaMate und Grafana nur über VPN oder einen fachgerecht gehärteten HTTPS-Reverse-Proxy ins Internet stellen.

## Installation – nur klicken

Template-URL:

`https://raw.githubusercontent.com/therepro21/teslamate-qnap-installer/main/list.json`

1. QNAP öffnen und **Container Station** starten.
2. Links **Präferenzen/Einstellungen** öffnen und **App Templates/Anwendungsvorlagen** wählen.
3. **Benutzerdefinierte Vorlage aktivieren** einschalten.
4. Die obige Template-URL vollständig einfügen und **Anwenden** klicken.
5. Links **App Templates/Anwendungsvorlagen** öffnen und den Tab **Custom Templates/Benutzerdefiniert** wählen.
6. **TeslaMate QNAP Installer** für die angezeigte NAS-Architektur auswählen. Wird kein passender Eintrag gezeigt, ist das NAS nicht unterstützt.
7. **Deploy/Bereitstellen** klicken, die Vorgaben unverändert lassen und den Assistenten mit **Fertigstellen** abschließen.
8. Warten, bis `teslamate-qnap-manager` läuft. Dann im LAN `http://NAS-IP:8888` öffnen.
9. Interne IP, Ports, Zeitzone sowie optional Domain/HTTPS-Ziel eintragen und **Speichern und bereitstellen** klicken.
10. TeslaMate unter `http://NAS-IP:4000` und Grafana unter `http://NAS-IP:3000` öffnen. Die Ports können im Manager abweichend gewählt werden.

Das CS3-Template folgt QNAPs dokumentiertem Schema (`templates`, Typ 1, `platform`, `image`, `ports`, `volumes`, `restart_policy`).

## Konfiguration und Domainwechsel

Der Manager zeigt interne NAS-IP, TeslaMate-/Grafana-Port, Domain, HTTPS-Status, Zeitzone und alle Image-Tags optisch an. Änderungen jederzeit unter `http://NAS-IP:8888` speichern. Domain und HTTPS sind Ziel-/Dokumentationswerte; TLS und DNS werden bewusst im QNAP-Reverse-Proxy oder einem anderen vorgeschalteten Proxy eingerichtet. Anschließend in TeslaMate unter **Einstellungen → URLs** die Web-App- und Dashboard-URL anpassen.

Secrets (`ENCRYPTION_KEY`, Datenbank- und Grafana-Kennwort) entstehen beim ersten Speichern mit einem kryptografischen Zufallszahlengenerator. Sie werden nur in `teslamate-qnap-manager-config:/data/config.json` mit restriktiven Dateirechten gespeichert, niemals ins Image, Repository oder Backup-Download geschrieben. Das Grafana-Initialkennwort wird absichtlich nicht in der Oberfläche ausgegeben; es kann später in Grafana geändert werden.

## Updates

**Backup + Update** führt in dieser Reihenfolge aus:

1. PostgreSQL-Dump, Konfigurationsmetadaten und Datei-Volumes sichern.
2. Ausschließlich die konfigurierten Images laden.
3. Nur die vier Anwendungscontainer ersetzen.
4. Bestehende Volumes wiederverwenden.
5. Startstatus prüfen und verständlich melden.

TeslaMate/Grafana sind auf Major `4`, PostgreSQL auf Major `18` und Mosquitto auf Major `2` begrenzt. Minor-/Patch-Updates bleiben möglich. Ein Major-Upgrade erfolgt nur, wenn der Nutzer den Image-Tag im Manager bewusst ändert; vorher Upstream-Migrationshinweise lesen und zusätzlich ein extern kopiertes Backup anlegen. Bei einem fehlgeschlagenen Update bleiben Backup und Volumes erhalten; über den vorherigen Image-Tag kann erneut bereitgestellt werden.

## Backup und Restore

**Backup erstellen** erzeugt ein herunterladbares `tar.gz` im persistenten Volume `teslamate-qnap-backups`. Enthalten sind PostgreSQL (`pg_dump`), Grafana-Daten, Mosquitto-Konfiguration/-Daten, Imports und nicht geheime Konfigurationsmetadaten. Downloads erscheinen direkt im Manager. Das Volume kann in Container Station zusätzlich an einen QNAP-Freigabeordner gebunden oder mit einer QNAP-Backup-Aufgabe gesichert werden.

Unter **Restore** eine vom Manager erzeugte `.tar.gz`-Datei auswählen. Vor jedem Restore entsteht automatisch ein weiteres Sicherheitsbackup. Nach einem Restore Erreichbarkeit und Datenbestand prüfen.

## Persistente Volumes – niemals löschen

| Volume | Inhalt |
|---|---|
| `teslamate-qnap-database` | PostgreSQL-Datenbank |
| `teslamate-qnap-grafana` | Grafana-Konfiguration und Zustand |
| `teslamate-qnap-mosquitto-config` | MQTT-Konfiguration |
| `teslamate-qnap-mosquitto-data` | MQTT-Daten |
| `teslamate-qnap-imports` | TeslaMate-Importdateien |
| `teslamate-qnap-manager-config` | lokale Konfiguration und Secrets |
| `teslamate-qnap-backups` | Backups |

Alle werden mit `io.teslamate-qnap.never-delete=true` markiert. Container können gefahrlos neu erstellt werden; Volumes werden nie automatisch entfernt. Der Manager enthält absichtlich keine Löschfunktion.

## Deinstallation

1. Zuerst im Manager ein Backup erstellen, herunterladen und extern prüfen.
2. In Container Station die Container `teslamate-qnap-manager`, `teslamate-qnap-{database,mosquitto,teslamate,grafana}` stoppen und entfernen. Bei Fragen zu Volumes **nicht löschen** wählen.
3. Damit ist die Software entfernt; alle Daten bleiben erhalten und eine Neuinstallation verwendet sie wieder.
4. Nur zur vollständigen, unwiderruflichen Datenlöschung anschließend in **Volumes** jedes oben genannte Volume einzeln auswählen, Namen und Backup erneut prüfen und die zusätzliche QNAP-Löschbestätigung bewusst bestätigen. Dieser Schritt kann nicht rückgängig gemacht werden.

## Architektur, Lizenz und technische Entscheidungen

TeslaMate besteht aus Phoenix/Elixir, PostgreSQL, Grafana und Mosquitto. Upstream veröffentlicht AMD64- und ARM64-Images; ARMv7 wird nicht unterstützt. Der Installer verändert TeslaMate nicht und verteilt es nicht eingebettet, sondern lädt die offiziellen Images. TeslaMate ist AGPL-3.0; der separate Manager steht unter MIT. Details stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Bei Lizenzfragen ist dies keine Rechtsberatung.

GitHub Actions validieren JSON gegen das im Repository dokumentierte CS3-Schema, prüfen beide Compose-Dateien, führen Tests aus, bauen/starten AMD64 und ARM64 unter QEMU und veröffentlichen ein echtes Multi-Arch-Manifest mit SBOM und Provenance in GHCR.

## Bekannte Einschränkungen

- Der Manager muss wegen des Docker-Sockets als root im Container laufen; QNAP verwendet je nach Modell unterschiedliche Socket-Gruppen-IDs.
- QNAPs UI-Texte variieren nach Firmware und Sprache.
- Der Manager konfiguriert keinen QNAP-Reverse-Proxy, DNS, Router oder Zertifikate automatisch.
- Ein automatisches transaktionales Rollback von Datenbankmigrationen ist nicht sicher möglich. Vor Updates wird deshalb zwingend gesichert; der bisherige Image-Tag kann manuell wieder eingetragen werden.
- Backups im Docker-Volume sind noch kein Schutz gegen NAS-/Pool-Ausfall; regelmäßig herunterladen oder in eine QNAP-Backup-Aufgabe aufnehmen.

Copyright © 2026 therepro21 und Mitwirkende. Manager-Code: MIT. Keine Gewährleistung; siehe [LICENSE](LICENSE).
