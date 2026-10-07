#!/usr/bin/env python3
"""
SamVivan MacroPad - Hardware Serial Event Listener & Action Dispatcher
Monitors USB Serial port, parses button clicks, and executes native Ubuntu actions.
"""

import time
import threading
import glob
import re
import os
import json
import serial
from typing import Optional, Callable, Dict, Any

from system_actions import execute_action
import config as config_module

CONFIG_DIR = os.path.expanduser('~/.config/samvivan-macropad')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

class SerialDaemonListener:
    def __init__(self, on_event_callback: Optional[Callable[[str], None]] = None):
        self.port: Optional[str] = None
        self.baudrate: int = 115200
        self.ser: Optional[serial.Serial] = None
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None
        self.current_mode: str = "desktop"  # "desktop" or "ha"
        self.on_event_callback = on_event_callback
        self.config: Dict[str, Any] = self.load_config()
        self.last_connected_port: Optional[str] = None

    def load_config(self) -> Dict[str, Any]:
        """Load button-to-action configuration from user's config directory."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[DAEMON] Error reading config file: {e}")
        return self._default_config()

    def save_config(self, new_config: Dict[str, Any]) -> bool:
        """Save updated action configuration."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2)
            self.config = new_config
            print("[DAEMON] Configuration successfully saved to disk.")
            return True
        except Exception as e:
            print(f"[DAEMON] Failed to save config: {e}")
            return False

    def _default_config(self) -> Dict[str, Any]:
        """Default fallback configuration."""
        return {
            "version": 2.5,
            "modes": [
                {
                    "id": "desktop",
                    "buttons": [
                        {"index": 0, "single": {"type": "mode_toggle"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 1, "single": {"type": "system_action", "presetId": "open_terminal"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 2, "single": {"type": "system_action", "presetId": "screenshot_interactive"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 3, "single": {"type": "system_action", "presetId": "mic_toggle_mute"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 4, "single": {"type": "system_action", "presetId": "volume_up_5"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 5, "single": {"type": "system_action", "presetId": "volume_down_5"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 6, "single": {"type": "system_action", "presetId": "lock_screen"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 7, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}}
                    ]
                },
                {
                    "id": "ha",
                    "buttons": [
                        {"index": 0, "single": {"type": "mode_toggle"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 1, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 2, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 3, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 4, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 5, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 6, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}},
                        {"index": 7, "single": {"type": "none"}, "double": {"type": "none"}, "hold": {"type": "none"}}
                    ]
                }
            ]
        }

    @staticmethod
    def list_available_ports():
        """Find active serial devices (USB or ACM)."""
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        return sorted(ports)

    def start(self, preferred_port: Optional[str] = None):
        """Start background worker thread."""
        if self.running:
            return
        self.running = True
        self.port = preferred_port
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[DAEMON] Serial background listener started (searching ports)...")

    def stop(self):
        """Stop background worker thread."""
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def send_command(self, command: str, log: bool = True) -> bool:
        """Kirim satu baris perintah teks ke hardware (dipakai konsol UI)."""
        if not self.ser or not self.ser.is_open:
            print("[DAEMON] [ERROR] Serial belum terbuka — perintah tidak terkirim.")
            return False
        try:
            payload = (command.strip() + "\n").encode("utf-8")
            self.ser.write(payload)
            if log and self.on_event_callback:
                self.on_event_callback(f"[TX] {command.strip()}")
            return True
        except Exception as e:
            print(f"[DAEMON] [ERROR] Gagal mengirim perintah: {e}")
            return False

    def _run_loop(self):
        """Continuously listen to serial input and auto-reconnect."""
        pattern = re.compile(r'\[(DESKTOP|HA)\]\s+Button\s+(\d+)\s+->\s+(SINGLE|DOUBLE|HOLD)', re.IGNORECASE)

        while self.running:
            # 1. Connect if not open
            if not self.ser or not self.ser.is_open:
                target_port = self.port
                if not target_port:
                    candidates = self.list_available_ports()
                    if candidates:
                        target_port = candidates[0]

                if not target_port:
                    time.sleep(2)
                    continue

                try:
                    self.ser = serial.Serial(target_port, self.baudrate, timeout=1)
                    self.last_connected_port = target_port
                    msg = f"[CONNECTED] Terhubung ke port hardware: {target_port}"
                    print(f"[DAEMON] {msg}")
                    if self.on_event_callback:
                        self.on_event_callback(msg)
                except Exception as e:
                    time.sleep(2)
                    continue

            # 2. Read incoming line
            try:
                raw_line = self.ser.readline()
                if not raw_line:
                    continue
                line = raw_line.decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                if self.on_event_callback:
                    self.on_event_callback(line)

                # Track mode transitions
                if "MODE: HOME ASSISTANT" in line:
                    self.current_mode = "ha"
                elif "MODE: DESKTOP" in line:
                    self.current_mode = "desktop"

                # Parse button click event
                match = pattern.search(line)
                if match:
                    mode_str = match.group(1).lower()  # "desktop" or "ha"
                    btn_num = int(match.group(2))       # 1-8
                    event_str = match.group(3).lower()  # "single", "double", "hold"

                    self._handle_hardware_trigger(mode_str, btn_num - 1, event_str)

            except Exception as e:
                print(f"[DAEMON] Serial read exception: {e}")
                if self.ser:
                    try:
                        self.ser.close()
                    except Exception:
                        pass
                self.ser = None
                time.sleep(1)

    def _handle_hardware_trigger(self, mode: str, button_index: int, trigger_event: str):
        """Dispatch action based on active configuration."""
        mode_key = "desktop" if mode == "desktop" else "ha"
        modes_list = self.config.get("modes", [])
        active_mode_config = next((m for m in modes_list if m.get("id") == mode_key), None)
        if not active_mode_config:
            return

        buttons = active_mode_config.get("buttons", [])
        if button_index >= len(buttons):
            return

        btn_config = buttons[button_index]
        actions = config_module.actions_list(btn_config.get(trigger_event))
        for action in actions:
            if not isinstance(action, dict) or action.get("type") in ("none", None):
                continue
            action_type = action.get("type")
            print(f"[DAEMON] Executing action for Button {button_index + 1} "
                  f"({trigger_event}) -> Type: {action_type}")
            ok, reason = execute_action(action_type, action)
            log_msg = (f"[ACTION] B{button_index + 1} ({trigger_event.upper()}): "
                       f"{reason} [{'OK' if ok else 'FAIL'}]")
            print(f"[DAEMON] {log_msg}")
            if self.on_event_callback:
                self.on_event_callback(log_msg)
