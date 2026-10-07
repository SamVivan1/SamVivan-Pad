#!/usr/bin/env python3
"""
firmware_sync - Kirim pemetaan tombol ke firmware ESP32-C3 via serial.

Protokol teks baris-per-baris (cocok dengan parser ringan di macropadv2.5.ino):
    SET d1 2,3,4,5,6,7,8      # array keycode
    SET dh 0,0,0,0,0,0,0
    SAVE                       # simpan ke NVS setelah semua array diterima

Hanya tombol makro (B2..B8 / index 1..7) yang dikirim — tombol mode (B1)
diproses firmware sendiri.
"""

import time
from typing import Any, Dict, List, Optional, Tuple

import config as config_module

# HID keycode (standar keyboard usage) sesuai BLEHIDKeys.h
_NAMED_KEYS: Dict[str, int] = {
    "ENTER": 0x28, "RETURN": 0x28, "ESC": 0x29, "ESCAPE": 0x29,
    "BACKSPACE": 0x2A, "TAB": 0x2B, "SPACE": 0x2C,
    "MINUS": 0x2D, "EQUAL": 0x2E, "PLUS": 0x2E,
    "LEFTBRACE": 0x2F, "[": 0x2F, "RIGHTBRACE": 0x30, "]": 0x30,
    "BACKSLASH": 0x31, "\\": 0x31, "SEMICOLON": 0x33, ";": 0x33,
    "APOSTROPHE": 0x34, "'": 0x34, "GRAVE": 0x35, "`": 0x35,
    "COMMA": 0x36, ",": 0x36, "DOT": 0x37, ".": 0x37,
    "SLASH": 0x38, "/": 0x38, "CAPS_LOCK": 0x39, "SCROLL_LOCK": 0x47,
    "NUM_LOCK": 0x53, "INSERT": 0x49, "DELETE": 0x4C, "DEL": 0x4C,
    "HOME": 0x4A, "END": 0x4D, "PAGE_UP": 0x4B, "PAGEUP": 0x4B,
    "PAGE_DOWN": 0x4E, "PAGEDOWN": 0x4E,
    "LEFT": 0x50, "RIGHT": 0x4F, "UP": 0x52, "DOWN": 0x51,
}

_FUNCTION_KEYS: Dict[str, int] = {
    f"F{i}": (0x3A + (i - 1) if 1 <= i <= 12 else 0x68 + (i - 13))
    for i in range(1, 25)
}
_NAMED_KEYS.update(_FUNCTION_KEYS)

_ARRAY_KEYS = ("d1", "d2", "dh", "h1", "h2", "hh")


def _key_to_code(key: str) -> int:
    key = (key or "").strip().upper()
    if not key:
        return 0
    if key in _NAMED_KEYS:
        return _NAMED_KEYS[key]
    if len(key) == 1:
        if "A" <= key <= "Z":
            return 0x04 + (ord(key) - ord("A"))
        if key.isdigit():
            return 0x27 if key == "0" else 0x1E + (int(key) - 1)
    return 0


def action_keycode(action: Any) -> int:
    """Keycode HID untuk sebuah aksi/slot (0 = tidak ada / tidak bisa dikirim).

    Firmware hanya bisa memetakan satu keycode per slot, jadi untuk slot
    dengan banyak aksi dipilih keycode dari aksi pertama yang bisa dikirim.
    """
    for item in config_module.actions_list(action):
        code = _single_keycode(item)
        if code:
            return code
    return 0


def _single_keycode(action: Optional[Dict[str, Any]]) -> int:
    if not isinstance(action, dict):
        return 0
    kind = action.get("type", "none")
    if kind == "shortcut":
        return _key_to_code(action.get("key", ""))
    if kind == "text":
        text = (action.get("text") or "").strip()
        return _key_to_code(text[0]) if text else 0
    return 0


def build_fw_commands(cfg: Dict[str, Any]) -> List[str]:
    """Bangun perintah serial untuk memetakan array tombol (B2..B8)."""
    commands: List[str] = []

    def arrays_for(mode_id: str) -> Tuple[List[int], List[int], List[int]]:
        single, double, hold = [], [], []
        mode = next((m for m in cfg.get("modes", [])
                     if m.get("id") == mode_id), None)
        if not mode:
            return single, double, hold
        for button in mode.get("buttons", [])[1:8]:
            single.append(action_keycode(button.get("single")))
            double.append(action_keycode(button.get("double")))
            hold.append(action_keycode(button.get("hold")))
        return single, double, hold

    for mode_id, prefix in (("desktop", "d"), ("ha", "h")):
        single, double, hold = arrays_for(mode_id)
        for array_key, values in zip(
                (f"{prefix}1", f"{prefix}2", f"{prefix}h"),
                (single, double, hold)):
            commands.append(f"SET {array_key} {','.join(str(v) for v in values)}")
    commands.append("SAVE")
    return commands


def push_to_firmware(listener: Any, cfg: Dict[str, Any],
                     ) -> Tuple[bool, str]:
    """Kirim pemetaan ke ESP32-C3. Mengembalikan (ok, alasan)."""
    port = getattr(listener, "ser", None)
    if listener is None or port is None or not getattr(port, "is_open", False):
        return False, "no-serial"
    commands = build_fw_commands(cfg)
    for command in commands:
        try:
            if not listener.send_command(command, log=False):
                return False, "gagal-kirim"
        except Exception as exc:
            return False, f"error:{exc}"
        time.sleep(0.06)
    return True, "OK"