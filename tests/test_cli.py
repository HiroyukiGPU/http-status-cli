import unittest
import subprocess
import sys
from http_status_cli import cli

class SmokeTests(unittest.TestCase):
    def test_help(self):
        r = subprocess.run([sys.executable, '-m', 'http_status_cli', '--help'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('usage:', r.stdout)

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class HTTPTests(unittest.TestCase):
    def test_404_and_405_fallback(self):
        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self):
                self.send_response(405 if self.path=='/fallback' else 404); self.end_headers()
            def do_GET(self): self.send_response(200); self.end_headers()
            def log_message(self,*a): pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            base=f'http://127.0.0.1:{server.server_port}'
            self.assertEqual(cli.check(base+'/missing')['status'],404)
            self.assertEqual(cli.check(base+'/fallback')['status'],200)
        finally: server.shutdown(); server.server_close(); thread.join()

