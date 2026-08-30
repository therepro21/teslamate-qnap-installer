"""QNAP-local lifecycle manager for an unmodified TeslaMate stack."""
from __future__ import annotations
import io, json, os, platform, secrets, tarfile, time
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
import docker
from docker.errors import DockerException, NotFound

app = Flask(__name__)
DATA = Path("/data")
BACKUPS = Path("/backups")
CONFIG = DATA / "config.json"
SUPPORTED = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
PREFIX = "teslamate-qnap"
VOLUMES = {
    "database": f"{PREFIX}-database",
    "grafana": f"{PREFIX}-grafana",
    "mosquitto-config": f"{PREFIX}-mosquitto-config",
    "mosquitto-data": f"{PREFIX}-mosquitto-data",
    "imports": f"{PREFIX}-imports",
    "config": f"{PREFIX}-manager-config",
    "backups": f"{PREFIX}-backups",
}
DEFAULTS = {
    "teslamate_image": "teslamate/teslamate:4",
    "grafana_image": "teslamate/grafana:4",
    "postgres_image": "postgres:18-trixie",
    "mosquitto_image": "eclipse-mosquitto:2",
    "teslamate_port": 4000,
    "grafana_port": 3000,
    "internal_ip": "",
    "domain": "",
    "https": False,
    "timezone": "Europe/Berlin",
}

def client():
    return docker.from_env(timeout=120)

def load_config():
    if not CONFIG.exists(): return None
    return json.loads(CONFIG.read_text(encoding="utf-8"))

def save_config(cfg):
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(CONFIG)

def architecture():
    return SUPPORTED.get(platform.machine().lower())

def ensure_network_volumes(d):
    try: d.networks.get(PREFIX)
    except NotFound: d.networks.create(PREFIX, driver="bridge", labels={"io.teslamate-qnap.managed":"true"})
    for name in VOLUMES.values():
        try: d.volumes.get(name)
        except NotFound: d.volumes.create(name=name, labels={"io.teslamate-qnap.persistent":"true","io.teslamate-qnap.never-delete":"true"})

def container_specs(cfg):
    common = {"network": PREFIX, "restart_policy":{"Name":"unless-stopped"}, "labels":{"io.teslamate-qnap.managed":"true"}}
    db_env = {"POSTGRES_USER":"teslamate","POSTGRES_PASSWORD":cfg["database_password"],"POSTGRES_DB":"teslamate"}
    app_env = {"DATABASE_USER":"teslamate","DATABASE_PASS":cfg["database_password"],"DATABASE_NAME":"teslamate","DATABASE_HOST":f"{PREFIX}-database","MQTT_HOST":f"{PREFIX}-mosquitto","ENCRYPTION_KEY":cfg["encryption_key"],"TZ":cfg["timezone"]}
    return {
      f"{PREFIX}-database": dict(image=cfg["postgres_image"], environment=db_env, volumes={VOLUMES["database"]:{"bind":"/var/lib/postgresql","mode":"rw"}}, healthcheck={"test":["CMD-SHELL","pg_isready -U teslamate"],"interval":10_000_000_000,"timeout":5_000_000_000,"retries":10}, **common),
      f"{PREFIX}-mosquitto": dict(image=cfg["mosquitto_image"], command="mosquitto -c /mosquitto-no-auth.conf", volumes={VOLUMES["mosquitto-config"]:{"bind":"/mosquitto/config","mode":"rw"},VOLUMES["mosquitto-data"]:{"bind":"/mosquitto/data","mode":"rw"}}, **common),
      f"{PREFIX}-teslamate": dict(image=cfg["teslamate_image"], environment=app_env, ports={"4000/tcp":int(cfg["teslamate_port"])}, volumes={VOLUMES["imports"]:{"bind":"/opt/app/import","mode":"rw"}}, cap_drop=["ALL"], **common),
      f"{PREFIX}-grafana": dict(image=cfg["grafana_image"], environment={"DATABASE_USER":"teslamate","DATABASE_PASS":cfg["database_password"],"DATABASE_NAME":"teslamate","DATABASE_HOST":f"{PREFIX}-database","GF_SECURITY_ADMIN_PASSWORD":cfg["grafana_password"],"TZ":cfg["timezone"]}, ports={"3000/tcp":int(cfg["grafana_port"])}, volumes={VOLUMES["grafana"]:{"bind":"/var/lib/grafana","mode":"rw"}}, **common),
    }

def deploy(cfg, pull=False):
    if not architecture(): raise RuntimeError(f"Nicht unterstützte Architektur: {platform.machine()}")
    d=client(); ensure_network_volumes(d)
    specs=container_specs(cfg)
    order=[f"{PREFIX}-database",f"{PREFIX}-mosquitto",f"{PREFIX}-teslamate",f"{PREFIX}-grafana"]
    for name in order:
        spec=specs[name]
        if pull: d.images.pull(spec["image"])
        try: c=d.containers.get(name); c.remove(force=True)
        except NotFound: pass
        d.containers.run(name=name, detach=True, **spec)
    time.sleep(8)
    return status()

def status():
    d=client(); result={}
    for name in [f"{PREFIX}-database",f"{PREFIX}-mosquitto",f"{PREFIX}-teslamate",f"{PREFIX}-grafana"]:
        try:
            c=d.containers.get(name); c.reload(); result[name]=c.status
        except NotFound: result[name]="fehlt"
    return result

def backup(cfg):
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path=BACKUPS/f"teslamate-qnap-{stamp}.tar.gz"
    d=client(); db=d.containers.get(f"{PREFIX}-database")
    code,out=db.exec_run(["pg_dump","-U","teslamate","-Fc","-d","teslamate"])
    if code: raise RuntimeError(out.decode(errors="replace"))
    safe={k:v for k,v in cfg.items() if k not in ("database_password","encryption_key","grafana_password")}
    with tarfile.open(path,"w:gz") as t:
        for name,data in (("database.dump",out),("config-public.json",json.dumps(safe,indent=2).encode())):
            info=tarfile.TarInfo(name); info.size=len(data); info.mtime=int(time.time()); t.addfile(info,io.BytesIO(data))
        for key in ("grafana","mosquitto-config","mosquitto-data","imports"):
            helper=d.containers.run("alpine:3.22",["tar","-C","/source","-cf","/backup/data.tar","."],detach=True,remove=False,volumes={VOLUMES[key]:{"bind":"/source","mode":"ro"},VOLUMES["backups"]:{"bind":"/backup","mode":"rw"}})
            rc=helper.wait()["StatusCode"]; helper.remove()
            if rc: raise RuntimeError(f"Volume-Backup fehlgeschlagen: {key}")
            volfile=BACKUPS/"data.tar"; t.add(volfile,arcname=f"volumes/{key}.tar"); volfile.unlink()
    return path.name

@app.route("/health")
def health():
    try: client().ping(); return {"ok":True,"architecture":architecture()}
    except Exception as e: return {"ok":False,"error":str(e)},503

@app.route("/", methods=["GET","POST"])
def index():
    cfg=load_config()
    if request.method=="POST":
        if not cfg:
            cfg={**DEFAULTS,"database_password":secrets.token_urlsafe(36),"encryption_key":secrets.token_urlsafe(48),"grafana_password":secrets.token_urlsafe(24)}
        for k in ("internal_ip","domain","timezone","teslamate_image","grafana_image","postgres_image","mosquitto_image"):
            if k in request.form: cfg[k]=request.form[k].strip()
        for k in ("teslamate_port","grafana_port"): cfg[k]=int(request.form[k])
        cfg["https"]="https" in request.form
        save_config(cfg)
        try:
            st=deploy(cfg); flash("Bereitstellung abgeschlossen: "+json.dumps(st),"ok")
        except Exception as e: flash(str(e),"error")
        return redirect(url_for("index"))
    try: st=status() if cfg else {}
    except Exception as e: st={"Manager":str(e)}
    return render_template("index.html",cfg=cfg or DEFAULTS,status=st,arch=architecture(),volumes=VOLUMES,backups=sorted([p.name for p in BACKUPS.glob("*.tar.gz")],reverse=True))

@app.post("/update")
def update():
    cfg=load_config()
    try:
        name=backup(cfg); st=deploy(cfg,pull=True); flash(f"Backup {name} erstellt; Update erfolgreich: {st}","ok")
    except Exception as e: flash(f"Update abgebrochen/fehlgeschlagen: {e}","error")
    return redirect(url_for("index"))

@app.post("/backup")
def make_backup():
    try: flash(f"Backup erstellt: {backup(load_config())}","ok")
    except Exception as e: flash(f"Backup fehlgeschlagen: {e}","error")
    return redirect(url_for("index"))

@app.get("/backups/<path:name>")
def download(name): return send_from_directory(BACKUPS,name,as_attachment=True)

@app.post("/restore")
def restore():
    cfg=load_config(); f=request.files.get("backup")
    try:
        if not f or not f.filename.endswith(".tar.gz"): raise RuntimeError("Eine .tar.gz-Sicherung auswählen.")
        before=backup(cfg); d=client()
        with tarfile.open(fileobj=f.stream,mode="r:gz") as t:
            members={m.name:m for m in t.getmembers()}
            dump=t.extractfile(members["database.dump"]).read()
            db=d.containers.get(f"{PREFIX}-database")
            info=tarfile.TarInfo("restore.dump"); info.size=len(dump)
            buf=io.BytesIO()
            with tarfile.open(fileobj=buf,mode="w") as upload: upload.addfile(info,io.BytesIO(dump))
            db.put_archive("/tmp",buf.getvalue())
            code,out=db.exec_run(["pg_restore","-U","teslamate","-d","teslamate","--clean","--if-exists","/tmp/restore.dump"])
            db.exec_run(["rm","-f","/tmp/restore.dump"])
            if code: raise RuntimeError(out.decode(errors="replace"))
            for key in ("grafana","mosquitto-config","mosquitto-data","imports"):
                member=members.get(f"volumes/{key}.tar")
                if not member: continue
                temp=BACKUPS/f"restore-{key}.tar"
                with temp.open("wb") as target: target.write(t.extractfile(member).read())
                helper=d.containers.run("alpine:3.22",["sh","-c",f"find /target -mindepth 1 -maxdepth 1 -exec rm -rf {{}} + && tar -C /target -xf /backup/{temp.name}"],detach=True,remove=False,volumes={VOLUMES[key]:{"bind":"/target","mode":"rw"},VOLUMES["backups"]:{"bind":"/backup","mode":"rw"}})
                rc=helper.wait()["StatusCode"]; logs=helper.logs().decode(errors="replace"); helper.remove(); temp.unlink(missing_ok=True)
                if rc: raise RuntimeError(f"Restore von {key} fehlgeschlagen: {logs}")
        deploy(cfg)
        flash(f"Datenbank wiederhergestellt. Sicherheitsbackup: {before}","ok")
    except Exception as e: flash(f"Restore fehlgeschlagen: {e}","error")
    return redirect(url_for("index"))

app.secret_key=os.environ.get("MANAGER_SESSION_KEY",secrets.token_hex(32))
