# Install TeslaMate on QNAP — beginner's guide

[Deutsche Version](INSTALLATION.de.md) · [Back to README](../README.md)

This guide requires no SSH, terminal or previous Docker knowledge. Menu names can vary slightly between QTS and QuTS hero versions. German menu names may differ according to your selected QNAP language.

## 1. Check the requirements

You need Container Station 3, roughly 2 GB of free memory, internet access for the NAS, and a supported 64-bit CPU: Intel/AMD (`amd64`, `x86_64`) or 64-bit ARM (`arm64`, `aarch64`). ARMv7/ARMHF 32-bit, x86 32-bit, MIPS and other architectures are not supported. Do not force a template for a different architecture.

## 2. Find the QNAP IP address

1. Open QTS or QuTS hero in your browser.
2. Check the address bar. In `https://192.168.1.20:443`, the NAS IP is `192.168.1.20`.
3. Alternatively open **Control Panel → Network & Virtual Switch → Network → Interfaces**.
4. Use the IPv4 address of the LAN interface through which you reach the NAS.

It commonly starts with `192.168.1`, `192.168.178` or `10.0.0`. Never use a public internet IP. Reserving this address for the NAS in your router is recommended.

## 3. Add the application-template URL

Copy this complete URL without spaces:

`https://raw.githubusercontent.com/therepro21/teslamate-qnap-installer/main/list.json`

1. Open **Container Station**.
2. Select **Preferences** from the left menu.
3. Open **App Templates**.
4. Turn on **Enable custom template**.
5. Paste the complete URL into the URL field.
6. Click **Apply**.
7. If QNAP reports an error, open the URL directly in your browser. You should see JSON text. Also check the NAS internet connection, date/time and DNS configuration.

## 4. Deploy the installer

1. Open **App Templates → Custom Templates**.
2. Select **TeslaMate QNAP Installer**. Container Station should show only the matching AMD64 or ARM64 entry.
3. Click **Deploy**.
4. Leave the image, command, volumes and restart policy unchanged.
5. The default manager host port is `8888`. If it is already occupied, use another free host port such as `8889`; keep the container port at `8888`.
6. Confirm that `/var/run/docker.sock` is present as a bind mount. The manager cannot create the TeslaMate containers without it. This socket grants extensive Docker control.
7. Click **Next**, review the settings and click **Finish**.
8. Wait under **Containers** until the manager is running.

Never expose port 8888—or your replacement manager port—through your router or a public reverse proxy. It is for the trusted local network only.

## 5. Open the setup assistant

Open `http://YOUR-QNAP-IP:8888` on your local network, for example `http://192.168.1.20:8888`. If you selected host port 8889 during deployment, use that port instead.

Every configuration field has a small **?** button. Clicking it opens an explanation in both English and German.

## 6. Which values should I enter?

| Field | Usual beginner value | Where to find it | When to change it |
|---|---|---|---|
| Internal NAS IP | local QNAP IP, e.g. `192.168.1.20` | QTS browser address or Network & Virtual Switch | When the NAS gets a different fixed LAN IP |
| Domain | empty | only from your own configured DNS | Only with an existing DNS and reverse-proxy setup |
| TeslaMate port | `4000` | installer default | If QNAP says 4000 is occupied; use e.g. `4001` |
| Grafana port | `3000` | installer default | If 3000 is occupied; use e.g. `3001` |
| Time zone | your IANA zone, e.g. `Europe/Berlin` | your location | Examples: `Europe/London`, `America/New_York` |
| HTTPS at reverse proxy | off | existing proxy configuration | Enable only after HTTPS and proxy forwarding already work |
| TeslaMate image | `teslamate/teslamate:4` | installer default | Beginners should not change it |
| Grafana image | `teslamate/grafana:4` | installer default | Beginners should not change it |
| PostgreSQL image | `postgres:18-trixie` | installer default | Only with verified upgrade instructions and a backup |
| Mosquitto image | `eclipse-mosquitto:2` | installer default | Normally never |

Click **Save and deploy**. On the first save, the manager automatically generates secure database, encryption and Grafana passwords. You do not need to create or copy any passwords.

## 7. Check the first start

The initial download may take several minutes. Then open:

- TeslaMate: `http://YOUR-QNAP-IP:4000`
- Grafana: `http://YOUR-QNAP-IP:3000`
- Manager: `http://YOUR-QNAP-IP:8888`

Use your chosen numbers if you changed ports. The manager shows container status; `running` means operational. For `exited` or `missing`, wait a few minutes first, then read the manager message and inspect the container logs in Container Station.

## 8. Domain and HTTPS defaults

For most home users, the safest normal setup is an empty domain, HTTPS switch off, access only through the home network or a VPN, and no router port forwarding.

A public domain additionally requires DNS, a valid TLS certificate, a reverse proxy and proper hardening. The manager field does not create these services. The manager port must never become public. After changing the domain, also update the Web App and Dashboards addresses in **TeslaMate → Settings → URLs**.

## 9. Update, backup and restore

- **Create backup** produces a downloadable `.tar.gz` archive.
- **Backup + Update** always creates a backup first, pulls only the configured major versions and replaces containers without deleting volumes.
- **Restore** accepts a manager-created `.tar.gz`; another safety backup is created first.

Keep important backup copies outside the NAS. A volume on the same NAS does not protect against storage-pool failure.

## 10. Never delete these volumes

`teslamate-qnap-database`, `teslamate-qnap-grafana`, `teslamate-qnap-mosquitto-config`, `teslamate-qnap-mosquitto-data`, `teslamate-qnap-imports`, `teslamate-qnap-manager-config`, `teslamate-qnap-backups`.

Containers can be recreated safely. These volumes hold data, configuration, secrets or backups. If QNAP asks whether associated volumes should also be removed, choose **No** unless you intentionally want permanent data destruction after verifying an external backup.
