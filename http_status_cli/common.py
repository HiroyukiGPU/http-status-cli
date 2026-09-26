import argparse
import functools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error


def entry(fn):
    @functools.wraps(fn)
    def wrapped():
        try:
            return fn()
        except KeyboardInterrupt:
            return 130
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            print(f'エラー: {exc}', file=sys.stderr)
            return 2
    return wrapped


def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--version', action='version', version='1.0.0')
    return p


def data_dir(name):
    p = Path(os.environ.get('CLI_TOOLS_DATA_HOME', Path.home() / '.local/share')) / name
    p.mkdir(parents=True, exist_ok=True, mode=0o700)
    return p


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def tls_context():
    import ssl
    context = ssl.create_default_context()
    try:
        import certifi
        context.load_verify_locations(certifi.where())
    except ImportError:
        pass
    return context


def fetch(url, timeout=20):
    if not url.startswith(('https://', 'http://')):
        raise ValueError('HTTP(S) URLを指定してください')
    req = urllib.request.Request(url, headers={'User-Agent': 'HiroyukiGPU-CLI/1.0'})
    with urllib.request.urlopen(req, timeout=timeout, context=tls_context()) as r:
        body = r.read(10_000_001)
        if len(body) > 10_000_000:
            raise ValueError('レスポンスが10 MBを超えています')
        return body


def get_json(url):
    return json.loads(fetch(url))


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def positive(value):
    n = float(value)
    if n <= 0:
        raise argparse.ArgumentTypeError('0より大きい数を指定してください')
    return n


def human(n):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(n) < 1024 or unit == 'TiB':
            return f'{n:.1f} {unit}'
        n /= 1024
