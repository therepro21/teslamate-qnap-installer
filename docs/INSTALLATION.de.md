# TeslaMate auf QNAP installieren – Anleitung für Einsteiger

[English version](INSTALLATION.en.md) · [Zurück zur README](../README.md)

Diese Anleitung setzt kein SSH, kein Terminal und keine Docker-Vorkenntnisse voraus. Je nach QTS-/QuTS-hero-Version können einzelne Menünamen leicht abweichen. Englische Menünamen stehen in Klammern.

## 1. Vorher prüfen

Du benötigst:

- ein QNAP mit **Container Station 3**;
- mindestens etwa 2 GB freien Arbeitsspeicher;
- eine unterstützte 64-Bit-CPU: Intel/AMD (`amd64`, `x86_64`) oder 64-Bit ARM (`arm64`, `aarch64`);
- Internetzugang des NAS, damit Container-Images und Tesla-Daten geladen werden können.

Nicht unterstützt sind ARMv7/ARMHF mit 32 Bit, x86 mit 32 Bit, MIPS und andere Architekturen. Wenn Container Station keine passende Vorlage zeigt, nicht irgendeine andere Architektur erzwingen.

## 2. Die QNAP-IP-Adresse finden

Du brauchst später die lokale IP deines NAS.

1. Öffne QTS oder QuTS hero im Browser.
2. Sieh in die Adresszeile. Bei `https://192.168.178.20:443` ist `192.168.178.20` die NAS-IP.
3. Alternativ: **Systemsteuerung → Netzwerk & virtueller Switch → Netzwerk → Schnittstellen** (`Control Panel → Network & Virtual Switch → Network → Interfaces`).
4. Nimm die IPv4-Adresse der LAN-Schnittstelle, über die du das NAS erreichst.

Typisch ist `192.168.1.x`, `192.168.178.x` oder `10.0.0.x`. Keine öffentliche Internet-IP verwenden. Empfehlenswert ist eine DHCP-Reservierung im Router, damit sich die NAS-IP nicht ändert.

## 3. Anwendungsvorlage eintragen

Kopiere diese URL exakt und ohne Leerzeichen:

`https://raw.githubusercontent.com/therepro21/teslamate-qnap-installer/main/list.json`

1. Öffne **Container Station**.
2. Klicke links auf **Präferenzen** oder **Einstellungen** (`Preferences`).
3. Öffne **Anwendungsvorlagen** (`App Templates`).
4. Aktiviere **Benutzerdefinierte Vorlage aktivieren** (`Enable custom template`).
5. Füge die komplette URL in das URL-Feld ein.
6. Klicke **Anwenden** (`Apply`).
7. Falls eine Fehlermeldung erscheint, öffne die URL testweise direkt im Browser. Du solltest JSON-Text sehen. Prüfe außerdem Internetzugang, Datum/Uhrzeit und DNS des NAS.

## 4. Installer bereitstellen

1. Öffne links **Anwendungsvorlagen** (`App Templates`).
2. Wechsle zu **Benutzerdefiniert** (`Custom Templates`).
3. Wähle **TeslaMate QNAP Installer**. Container Station sollte nur die passende AMD64- oder ARM64-Variante zeigen.
4. Klicke **Bereitstellen** (`Deploy`).
5. Lass Image, Befehl, Volumes und Neustartrichtlinie unverändert.
6. Der Host-Port des Managers ist standardmäßig `8888`. Ist er bereits belegt, kannst du im Bereitstellungsdialog einen anderen freien Host-Port wie `8889` verwenden. Der Container-Port bleibt `8888`.
7. Prüfe, dass `/var/run/docker.sock` als Bind-Mount vorhanden ist. Ohne diesen Mount kann der Manager die TeslaMate-Container nicht erstellen. Der Socket gibt dem Manager weitreichende Docker-Rechte.
8. Klicke **Weiter** und danach **Fertigstellen** (`Next`, `Finish`).
9. Warte in **Container** (`Containers`), bis der Manager als laufend angezeigt wird.

Wichtig: Port 8888 beziehungsweise dein Ersatzport darf nur im lokalen Netzwerk erreichbar sein. Keine Router-Portweiterleitung und keinen öffentlichen Reverse Proxy für den Manager anlegen.

## 5. Browser-Assistent öffnen

Öffne im lokalen Netzwerk:

`http://DEINE-QNAP-IP:8888`

Beispiel: `http://192.168.178.20:8888`

Hast du beim Deploy den Host-Port auf 8889 geändert, verwende `http://DEINE-QNAP-IP:8889`.

Neben jedem Feld befindet sich ein kleines **?**. Ein Klick öffnet eine Erklärung auf Deutsch und Englisch.

## 6. Welche Werte soll ich eintragen?

| Feld | Normaler Wert für Einsteiger | Woher kommt der Wert? | Wann ändern? |
|---|---|---|---|
| Interne NAS-IP | lokale QNAP-IP, z. B. `192.168.178.20` | QTS-Adresszeile oder Netzwerk & virtueller Switch | Nur wenn das NAS eine andere feste LAN-IP bekommt |
| Domain | leer | nur eine selbst eingerichtete DNS-Domain | Nur bei vorhandenem Reverse Proxy und DNS |
| TeslaMate-Port | `4000` | vorgegeben | Wenn QNAP meldet, dass 4000 belegt ist, z. B. `4001` |
| Grafana-Port | `3000` | vorgegeben | Wenn 3000 belegt ist, z. B. `3001` |
| Zeitzone | `Europe/Berlin` | Wohnort/Zeitzone | Österreich: `Europe/Vienna`, Schweiz: `Europe/Zurich` |
| HTTPS am Reverse Proxy | aus | vorhandene Proxy-Konfiguration | Nur einschalten, wenn HTTPS und Proxy bereits funktionieren |
| TeslaMate-Image | `teslamate/teslamate:4` | vom Installer | Als Einsteiger nicht ändern |
| Grafana-Image | `teslamate/grafana:4` | vom Installer | Als Einsteiger nicht ändern |
| PostgreSQL-Image | `postgres:18-trixie` | vom Installer | Nur nach geprüfter Upgrade-Anleitung und Backup |
| Mosquitto-Image | `eclipse-mosquitto:2` | vom Installer | Normalerweise nie ändern |

Klicke anschließend **Speichern und bereitstellen**. Beim ersten Mal erzeugt der Manager sichere Datenbank-, Verschlüsselungs- und Grafana-Kennwörter automatisch. Du musst keine Kennwörter erfinden oder kopieren.

## 7. Ersten Start prüfen

Der erste Download kann mehrere Minuten dauern. Danach öffnest du:

- TeslaMate: `http://DEINE-QNAP-IP:4000`
- Grafana: `http://DEINE-QNAP-IP:3000`
- Manager: `http://DEINE-QNAP-IP:8888`

Bei geänderten Ports entsprechend die gewählten Zahlen einsetzen. Der Manager zeigt den Containerstatus. `running` bedeutet laufend. Bei `exited` oder `fehlt` zuerst einige Minuten warten, dann die verständliche Meldung im Manager und die Container-Protokolle in Container Station prüfen.

## 8. Domain und HTTPS – was ist normal?

Für die meisten Heimnutzer ist die sichere Standardlösung:

- Domain leer;
- HTTPS-Schalter aus;
- Zugriff nur im Heimnetz oder über ein VPN;
- keine Portweiterleitung im Router.

Eine öffentliche Domain erfordert zusätzlich DNS, ein gültiges TLS-Zertifikat, einen Reverse Proxy und dessen Absicherung. Das Eingabefeld allein richtet diese Dinge nicht ein. Der Manager-Port 8888 darf auch dann niemals öffentlich werden. Nach einem Domainwechsel außerdem in TeslaMate unter **Einstellungen → URLs** die Web-App- und Dashboard-Adresse anpassen.

## 9. Update, Backup und Restore

- **Backup erstellen**: jederzeit klicken und die erzeugte `.tar.gz`-Datei herunterladen.
- **Backup + Update**: erstellt zwingend zuerst ein Backup, lädt dann nur die konfigurierten Hauptversionen und ersetzt Container ohne Volumes zu löschen.
- **Restore**: eine vom Manager erzeugte `.tar.gz` auswählen. Vor dem Restore wird zusätzlich ein Sicherheitsbackup erstellt.

Speichere wichtige Backups zusätzlich außerhalb des NAS. Ein Backup-Volume auf demselben NAS schützt nicht vor einem Defekt des Speicherpools.

## 10. Diese Volumes niemals löschen

`teslamate-qnap-database`, `teslamate-qnap-grafana`, `teslamate-qnap-mosquitto-config`, `teslamate-qnap-mosquitto-data`, `teslamate-qnap-imports`, `teslamate-qnap-manager-config`, `teslamate-qnap-backups`.

Container dürfen neu erstellt werden. Die genannten Volumes enthalten Daten, Konfiguration, Secrets oder Backups. Bei QNAP-Fragen wie „zugehörige Volumes ebenfalls entfernen?“ immer **Nein** wählen, solange du nicht nach geprüftem externem Backup bewusst alle Daten endgültig löschen möchtest.
