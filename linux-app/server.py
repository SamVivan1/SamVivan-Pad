#!/usr/bin/env python3
"""
SamVivan MacroPad - Local Embedded Server & REST API for Native Desktop App
Serves the GUI assets and handles system calls while the desktop app is open.
"""

import os
import sys
import json
import time
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from typing import List, Optional

from app_scanner import get_installed_apps, launch_app
from system_actions import SYSTEM_ACTION_PRESETS, execute_action
from serial_listener import SerialDaemonListener

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web-configurator'))
PORT = 8080
recent_logs: List[str] = []
MAX_LOGS = 100

_httpd: Optional[ThreadingHTTPServer] = None
_server_thread: Optional[threading.Thread] = None
serial_daemon: Optional[SerialDaemonListener] = None

def append_log(msg: str):
    timestamp = time.strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {msg}"
    recent_logs.append(log_entry)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop(0)

class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/status':
            is_connected = bool(serial_daemon and serial_daemon.ser and serial_daemon.ser.is_open)
            self.send_json({
                "status": "online",
                "app": "SamVivan MacroPad Native",
                "version": "2.5",
                "serialConnected": is_connected,
                "port": serial_daemon.last_connected_port if serial_daemon else None,
                "currentMode": serial_daemon.current_mode if serial_daemon else "desktop",
                "appsCount": len(get_installed_apps())
            })
            return

        elif path == '/api/apps':
            apps = get_installed_apps()
            self.send_json({"count": len(apps), "apps": apps})
            return

        elif path == '/api/system-actions':
            self.send_json({"actions": SYSTEM_ACTION_PRESETS})
            return

        elif path == '/api/ports':
            ports = serial_daemon.list_available_ports() if serial_daemon else []
            curr = serial_daemon.last_connected_port if serial_daemon else None
            self.send_json({"ports": ports, "current": curr})
            return

        elif path == '/api/config':
            cfg = serial_daemon.config if serial_daemon else {}
            self.send_json(cfg)
            return

        elif path == '/api/logs':
            self.send_json({"logs": recent_logs})
            return

        elif path == '/api/ha/status':
            # Default: instan dari cache (tanpa jaringan). ?ping=1 -> cek live.
            from home_assistant import ha_client
            ping = 'ping=1' in (parsed.query or '')
            self.send_json(ha_client.get_status(ping=ping))
            return

        elif path == '/api/ha/entities':
            from home_assistant import ha_client
            force = 'refresh=1' in (parsed.query or '')
            entities = ha_client.get_entities(force_refresh=force)
            domains: dict = {}
            for ent in entities:
                domains[ent["domain"]] = domains.get(ent["domain"], 0) + 1
            self.send_json({
                "count": len(entities),
                "entities": entities,
                "domains": domains,
                "url": ha_client.url,
                "configured": ha_client.is_configured(),
                # live = hasil scan ke HA saat itu juga; False = baca cache/disk
                "live": bool(entities) and ha_client._last_scan_live
            })
            return

        elif path == '/api/ha/config':
            from home_assistant import ha_client
            self.send_json({
                "configured": ha_client.is_configured(),
                "url": ha_client.url,
                "tokenSet": bool(ha_client.token)
            })
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.read_body_json()

        if path == '/api/ha/test':
            from home_assistant import ha_client
            url = body.get('url', '')
            token = body.get('token', '')
            ok, msg = ha_client.check_connection(url or None, token or None)
            append_log(f"HA Test: {msg}")
            self.send_json({"success": ok, "message": msg})
            return

        if path == '/api/ha/call':
            from home_assistant import ha_client
            domain = body.get('domain', '')
            service = body.get('service', 'toggle')
            entity_id = body.get('entityId') or body.get('entity_id', '')
            data = body.get('data') or {}
            if not domain and '.' in entity_id:
                domain = entity_id.split('.')[0]
            ok, msg = ha_client.call_service(domain, service, entity_id, data)
            append_log(f"HA Call '{domain}.{service}' -> {entity_id}: {msg}")
            self.send_json({"success": ok, "message": msg})
            return

        elif path == '/api/ha/config':
            from home_assistant import ha_client
            url = (body.get('url') or '').strip()
            token = (body.get('token') or '').strip() or (ha_client.token or '')
            if not url or not url.startswith(('http://', 'https://')):
                self.send_json({"success": False, "message": "URL tidak valid (harus diawali http:// atau https://)"})
                return
            if not token:
                self.send_json({"success": False, "message": "Token kosong — buat Long-Lived Access Token di Home Assistant"})
                return
            saved = ha_client.save_config(url, token)
            append_log(f"HA configuration updated: {url}")
            self.send_json({"success": saved, "url": ha_client.url,
                            "message": "Koneksi Home Assistant tersimpan" if saved else "Gagal menulis file konfigurasi"})
            return

        elif path == '/api/apps/launch':
            desktop_id = body.get('desktopId', '')
            ok, msg = launch_app(desktop_id)
            append_log(f"Launch App '{desktop_id}': {msg}")
            self.send_json({"success": ok, "message": msg})
            return

        elif path == '/api/system-actions/execute':
            preset_id = body.get('presetId', '')
            ok, msg = execute_action('system_action', {'presetId': preset_id})
            append_log(f"Action '{preset_id}': {msg}")
            self.send_json({"success": ok, "message": msg})
            return

        elif path == '/api/config':
            if not body or not isinstance(body, dict):
                self.send_json({"success": False, "message": "Invalid JSON"}, status=400)
                return
            saved = serial_daemon.save_config(body) if serial_daemon else False
            append_log("Configuration saved to disk.")
            self.send_json({"success": saved, "message": "Configuration saved"})
            return

        elif path == '/api/ports/connect':
            target_port = body.get('port')
            if serial_daemon:
                serial_daemon.stop()
                time.sleep(0.3)
                serial_daemon.start(preferred_port=target_port)
            self.send_json({"success": True, "port": target_port})
            return

        self.send_json({"error": "Endpoint not found"}, status=404)

    def read_body_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        try:
            raw = self.rfile.read(content_length).decode('utf-8')
            return json.loads(raw)
        except Exception:
            return {}

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def start_backend(port: int = PORT) -> int:
    """Start serial listener and local HTTP server in background thread."""
    global _httpd, _server_thread, serial_daemon

    # Start serial hardware listener
    serial_daemon = SerialDaemonListener(on_event_callback=append_log)
    serial_daemon.start()

    # Pre-cache installed applications
    get_installed_apps()

    # Start HTTP server
    for candidate_port in [port, 8081, 8082, 54321, 54322]:
        try:
            server_address = ('127.0.0.1', candidate_port)
            _httpd = ThreadingHTTPServer(server_address, AppRequestHandler)
            actual_port = candidate_port
            break
        except OSError:
            continue

    _server_thread = threading.Thread(target=_httpd.serve_forever, daemon=True)
    _server_thread.start()
    print(f"[*] Local peripheral server running on http://127.0.0.1:{actual_port}")
    return actual_port

def stop_backend():
    """Clean up and shutdown background threads."""
    global _httpd, serial_daemon
    if serial_daemon:
        serial_daemon.stop()
        serial_daemon = None
    if _httpd:
        _httpd.shutdown()
        _httpd.server_close()
        _httpd = None
    print("[*] Local peripheral server stopped.")

if __name__ == '__main__':
    port = start_backend(PORT)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_backend()
