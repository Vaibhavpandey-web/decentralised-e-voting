"""Controlled startup independent of hosting-provider command quoting."""
import os
import subprocess
import sys

if os.getenv('RUN_STARTUP_TESTS', '1') == '1':
    test_env = dict(os.environ)
    test_env['TEST_DATABASE_URL'] = os.environ.get('DATABASE_URL', '')
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q', '--tb=no'], env=test_env)
    if result.returncode:
        raise SystemExit(result.returncode)
os.execvp('gunicorn', ['gunicorn', '--config', 'gunicorn.conf.py', 'app:app'])
