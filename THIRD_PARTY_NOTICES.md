# Hinweise zu Drittsoftware

Dieses Repository enthält ausschließlich den unabhängigen Installer/Manager. Es enthält keinen kopierten TeslaMate-Quellcode und keine fremden Logos.

| Komponente | Verwendung | Lizenz / Quelle |
|---|---|---|
| TeslaMate | unverändertes Laufzeit-Image `teslamate/teslamate:4` | AGPL-3.0, https://github.com/teslamate-org/teslamate |
| TeslaMate Grafana | unverändertes Laufzeit-Image `teslamate/grafana:4` | AGPL-3.0 / Hinweise des Upstreams |
| PostgreSQL 18 | Datenbank-Image | PostgreSQL License, https://www.postgresql.org/about/licence/ |
| Eclipse Mosquitto 2 | MQTT-Broker-Image | EPL-2.0 oder EDL-1.0, https://github.com/eclipse-mosquitto/mosquitto |
| Python | Manager-Basisimage | PSF License, https://www.python.org/psf/license/ |
| Flask | Python-Abhängigkeit | BSD-3-Clause |
| Docker SDK for Python | Python-Abhängigkeit | Apache-2.0 |
| Gunicorn | Python-Abhängigkeit | MIT |

Tesla, TeslaMate, QNAP, Container Station, PostgreSQL, Eclipse und Docker sind Namen bzw. Marken ihrer jeweiligen Inhaber und werden ausschließlich beschreibend verwendet.

**Inoffizielles Community-Projekt; nicht verbunden mit oder unterstützt von den jeweiligen Herstellern.** Es wird keinerlei Gewährleistung übernommen. Die Nutzung erfolgt auf eigenes Risiko. Insbesondere ist der Docker-Socket hochprivilegiert und der Manager darf nicht aus dem Internet erreichbar sein.
