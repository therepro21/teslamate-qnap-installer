"""Initialize local credentials before starting Gunicorn."""
import os
from app import DATA, manager_password

if not (DATA / 'manager-password').exists():
    print('Manager login (admin):', manager_password(), flush=True)

os.execvp('gunicorn', ['gunicorn', '--bind=0.0.0.0:8888', '--workers=1',
                       '--threads=4', '--timeout=120', 'app:app'])
