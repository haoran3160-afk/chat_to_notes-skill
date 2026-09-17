"""Isolated local Chromium session for readiness checks and printing.

Uses websocket-client from the local PDF verification environment, not a service.
"""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import tempfile


class BrowserSession:
    def __init__(self, executable, profile):
        self.executable, self.profile = executable, Path(profile)
        self.process = self.ws = None
        self.temporary = None
        self.sequence = 0

    def __enter__(self):
        try:
            import websocket
        except ImportError as exc:
            raise ValueError('PDF export needs websocket-client in this Python environment.') from exc
        self.temporary = tempfile.TemporaryDirectory(prefix='chromium-',dir=self.profile.parent,ignore_cleanup_errors=True)
        self.profile = Path(self.temporary.name)
        self.process = subprocess.Popen([self.executable,'--headless=new','--disable-gpu','--no-first-run',
            '--disable-extensions','--disable-background-networking','--remote-debugging-port=0',
            f'--user-data-dir={self.profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            active = self.profile/'DevToolsActivePort'
            port = None
            for _ in range(200):
                try:
                    port = active.read_text().splitlines()[0]
                    break
                except (OSError,IndexError): time.sleep(.05)
            if port is None: raise ValueError('Chromium debugging endpoint did not become ready.')
            targets = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json',timeout=5))
            target = next(t for t in targets if t['type']=='page')
            self.ws = websocket.create_connection(target['webSocketDebuggerUrl'],timeout=45,suppress_origin=True)
            self.call('Page.enable')
            self.call('Network.enable')
            self.call('Network.setBlockedURLs',{'urls':['http://*','https://*']})
            return self
        except Exception:
            self.__exit__(None,None,None)
            raise

    def call(self, method, params=None):
        self.sequence += 1
        self.ws.send(json.dumps({'id':self.sequence,'method':method,'params':params or {}}))
        while True:
            result = json.loads(self.ws.recv())
            if result.get('id')==self.sequence:
                if 'error' in result: raise ValueError(str(result['error']))
                return result.get('result',{})

    def evaluate(self, expression):
        response = self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in response: raise ValueError(str(response['exceptionDetails']))
        return response['result'].get('value')

    def navigate(self, url):
        self.call('Page.navigate',{'url':url})
        for _ in range(200):
            if self.evaluate('document.readyState')=='complete': return
            time.sleep(.05)
        raise ValueError('HTML did not finish loading.')

    def __exit__(self,*args):
        if self.ws: self.ws.close()
        if self.process:
            self.process.terminate()
            try: self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=5)
        if self.temporary: self.temporary.cleanup()
