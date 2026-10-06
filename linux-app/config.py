#!/usr/bin/env python3
"""
SamVivan MacroPad - Konfigurasi tombol (default, preset, load/save).

Sumber kebenaran satu-satunya untuk aplikasi native GTK4:
~/.config/samvivan-macropad/config.json
"""

import copy
import json
import os
from typing import Any, Dict, List, Tuple

CONFIG_DIR = os.path.expanduser("~/.config/samvivan-macropad")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Pinout fisik tombol B1..B8 (sama dengan macropadv2.5.ino)
PINOUT = [20, 9, 2, 1, 21, 10, 3, 0]

TRIGGERS: List[Tuple[str, str]] = [
    ("single", "Single Click (1x)"),
    ("double", "Double Click (2x)"),
    ("hold", "Hold / Long Press"),
]

ACTION_TYPES: List[Tuple[str, str]] = [
    ("none", "Tidak ada / Mati"),
    ("shortcut", "Keyboard Shortcut"),
    ("text", "Teks / String Otomatis"),
    ("media", "Kontrol Media"),
    ("launch_app", "Jalankan Aplikasi"),
    ("system_action", "Aksi Sistem (Preset)"),
    ("bash_script", "Script Bash"),
    ("home_assistant", "Home Assistant (Native)"),
    ("ha_webhook", "HA Webhook"),
    ("mode_toggle", "Ganti Mode (Layer)"),
]

ACTION_TYPE_LABEL: Dict[str, str] = dict(ACTION_TYPES)

MODIFIERS = ["ctrl", "alt", "shift", "super"]

KEY_GROUPS: List[Tuple[str, List[str]]] = [
    ("Alfabet", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")),
    ("Angka", list("0123456789")),
    ("Function Keys", [f"F{i}" for i in range(1, 25)]),
    ("Navigasi dan Kontrol", [
        "ENTER", "ESC", "BACKSPACE", "TAB", "SPACE", "UP", "DOWN", "LEFT",
        "RIGHT", "HOME", "END", "PAGE_UP", "PAGE_DOWN", "DELETE",
    ]),
]

MEDIA_ACTIONS: List[Tuple[str, str]] = [
    ("MUTE", "Mute / Unmute"),
    ("VOL_UP", "Volume Up (+)"),
    ("VOL_DOWN", "Volume Down (-)"),
    ("PLAY_PAUSE", "Play / Pause"),
    ("NEXT_TRACK", "Lagu Berikutnya"),
    ("PREV_TRACK", "Lagu Sebelumnya"),
]

MEDIA_ACTION_LABEL: Dict[str, str] = dict(MEDIA_ACTIONS)

# Label perangkat keras tombol (B1..B8)
DEFAULT_LABELS = [
    "Mode / Passcode",
    "Terminal",
    "Screenshot",
    "Mute Mic",
    "Vol Up",
    "Vol Down",
    "Lock Screen",
    "Macro 7",
]

HA_KEY_LABELS = [f"HA Key {i + 1}" for i in range(7)]


def default_action(action_type: str) -> Dict[str, Any]:
    """Aksi default untuk sebuah tipe — tanpa data hardcode (mis. entity HA)."""
    if action_type == "shortcut":
        return {"type": "shortcut", "modifiers": ["ctrl", "alt", "shift"], "key": "A"}
    if action_type == "text":
        return {"type": "text", "text": "Hello World"}
    if action_type == "media":
        return {"type": "media", "mediaKey": "VOL_UP"}
    if action_type == "launch_app":
        return {"type": "launch_app", "desktopId": "code.desktop", "appName": "Visual Studio Code"}
    if action_type == "system_action":
        return {"type": "system_action", "presetId": "mic_toggle_mute",
                "presetName": "Toggle Microphone Mute"}
    if action_type == "bash_script":
        return {"type": "bash_script", "script": 'notify-send "MacroPad" "Action!"'}
    if action_type == "home_assistant":
        # Tanpa entity bawaan: user memilih lewat Entity Picker.
        return {"type": "home_assistant", "domain": "", "service": "",
                "entityId": "", "friendlyName": ""}
    if action_type == "ha_webhook":
        return {"type": "ha_webhook", "url": ""}
    if action_type == "mode_toggle":
        return {"type": "mode_toggle"}
    return {"type": "none"}


def _button(index: int, label: str, single: Dict[str, Any],
            double: Dict[str, Any] | None = None,
            hold: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "index": index,
        "pin": PINOUT[index],
        "label": label,
        "single": single,
        "double": double or {"type": "none"},
        "hold": hold or {"type": "none"},
    }


def default_config() -> Dict[str, Any]:
    """Konfigurasi bawaan. Mode HA sengaja tanpa entity — user memilih sendiri."""
    desktop_buttons = [
        _button(0, DEFAULT_LABELS[0], {"type": "mode_toggle"}, hold={"type": "text", "text": "031004"}),
        _button(1, DEFAULT_LABELS[1], {"type": "system_action", "presetId": "open_terminal",
                                       "presetName": "Open New Terminal"}),
        _button(2, DEFAULT_LABELS[2], {"type": "system_action", "presetId": "screenshot_interactive",
                                       "presetName": "Interactive Screenshot (Area)"}),
        _button(3, DEFAULT_LABELS[3], {"type": "system_action", "presetId": "mic_toggle_mute",
                                       "presetName": "Toggle Microphone Mute"}),
        _button(4, DEFAULT_LABELS[4], {"type": "system_action", "presetId": "volume_up_5",
                                       "presetName": "Volume Up (+5%)"}),
        _button(5, DEFAULT_LABELS[5], {"type": "system_action", "presetId": "volume_down_5",
                                       "presetName": "Volume Down (-5%)"}),
        _button(6, DEFAULT_LABELS[6], {"type": "system_action", "presetId": "lock_screen",
                                       "presetName": "Lock Ubuntu Session"}),
        _button(7, DEFAULT_LABELS[7],
                {"type": "shortcut", "modifiers": ["ctrl", "alt", "shift"], "key": "8"},
                {"type": "shortcut", "modifiers": ["ctrl", "alt", "shift"], "key": "U"},
                {"type": "shortcut", "modifiers": ["ctrl", "alt", "shift"], "key": "J"}),
    ]
    ha_buttons = [
        _button(0, DEFAULT_LABELS[0], {"type": "mode_toggle"}, hold={"type": "text", "text": "031004"}),
    ]
    for i, label in enumerate(HA_KEY_LABELS):
        ha_buttons.append(_button(i + 1, label, default_action("home_assistant")))

    return {
        "version": 2.5,
        "device": "SamVivan MacroPad",
        "debounceMs": 25,
        "clickTimeoutMs": 250,
        "holdTimeoutMs": 450,
        "activeModeIndex": 0,
        "modes": [
            {"id": "desktop", "name": "Desktop Mode", "ledState": True, "buttons": desktop_buttons},
            {"id": "ha", "name": "Home Assistant Mode", "ledState": False, "buttons": ha_buttons},
        ],
    }


def apply_preset(key: str) -> Dict[str, Any]:
    """Bangun konfigurasi dari preset bawaan ('default' | 'productivity' | 'media')."""
    config = default_config()
    if key == "productivity":
        btns = config["modes"][0]["buttons"]
        btns[1]["label"] = "Terminal"
        btns[1]["single"] = {"type": "system_action", "presetId": "open_terminal",
                             "presetName": "Open New Terminal"}
        btns[2]["label"] = "Screenshot"
        btns[2]["single"] = {"type": "system_action", "presetId": "screenshot_interactive",
                             "presetName": "Interactive Screenshot (Area)"}
        btns[3]["label"] = "Lock Screen"
        btns[3]["single"] = {"type": "system_action", "presetId": "lock_screen",
                             "presetName": "Lock Ubuntu Session"}
        btns[4]["label"] = "VS Code"
        btns[4]["single"] = {"type": "launch_app", "desktopId": "code.desktop",
                             "appName": "Visual Studio Code"}
    elif key == "media":
        btns = config["modes"][0]["buttons"]
        btns[1]["label"] = "Play / Pause"
        btns[1]["single"] = {"type": "media", "mediaKey": "PLAY_PAUSE"}
        btns[2]["label"] = "Vol Down"
        btns[2]["single"] = {"type": "system_action", "presetId": "volume_down_5",
                             "presetName": "Volume Down (-5%)"}
        btns[3]["label"] = "Vol Up"
        btns[3]["single"] = {"type": "system_action", "presetId": "volume_up_5",
                             "presetName": "Volume Up (+5%)"}
        btns[4]["label"] = "Mute"
        btns[4]["single"] = {"type": "system_action", "presetId": "volume_toggle_mute",
                             "presetName": "Toggle Speaker Mute"}
    return config


PRESET_ITEMS: List[Tuple[str, str, str]] = [
    ("default", "Default (Desktop dan Native HA)",
     "Bawaan pabrik: tombol sistem + slot HA kosong untuk dipilih sendiri."),
    ("productivity", "Ubuntu Productivity",
     "Terminal, screenshot, lock screen, dan peluncur VS Code."),
    ("media", "Media dan Streaming",
     "Play/pause, volume, dan mute untuk kontrol musik."),
]


def _merge_button(base: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(template)
    merged.update({k: v for k, v in base.items() if k in ("index", "pin", "label")})
    for trig in ("single", "double", "hold"):
        action = base.get(trig)
        if isinstance(action, dict) and action.get("type"):
            merged[trig] = action
        else:
            merged[trig] = template.get(trig, {"type": "none"})
    return merged


def normalize_config(data: Any) -> Tuple[bool, str]:
    """Validasi struktur profil hasil import. Mengembalikan (ok, pesan)."""
    if not isinstance(data, dict):
        return False, "Bukan objek JSON."
    modes = data.get("modes")
    if not isinstance(modes, list) or len(modes) < 2:
        return False, "Field 'modes' tidak valid (butuh 2 mode)."
    for mode in modes:
        if not isinstance(mode, dict) or not isinstance(mode.get("buttons"), list):
            return False, "Struktur 'modes[].buttons' tidak valid."
        for button in mode["buttons"]:
            if not isinstance(button, dict):
                return False, "Entri tombol tidak valid."
            for trig in ("single", "double", "hold"):
                action = button.get(trig)
                if action is not None and not isinstance(action, dict):
                    return False, f"Aksi '{trig}' tidak valid."
    return True, "OK"


def load_config() -> Dict[str, Any]:
    """Muat konfigurasi pengguna, dilengkapi field default yang hilang."""
    config = default_config()
    if not os.path.exists(CONFIG_FILE):
        return config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
            stored = json.load(handle)
    except Exception as exc:
        print(f"[CONFIG] Gagal membaca {CONFIG_FILE}: {exc}")
        return config
    if not isinstance(stored, dict):
        return config

    for key in ("version", "device", "debounceMs", "clickTimeoutMs", "holdTimeoutMs",
                "activeModeIndex"):
        if key in stored:
            config[key] = stored[key]

    stored_modes = stored.get("modes")
    if isinstance(stored_modes, list) and len(stored_modes) >= 2:
        for slot, stored_mode in enumerate(stored_modes[:2]):
            if not isinstance(stored_mode, dict):
                continue
            mode = config["modes"][slot]
            for key in ("id", "name", "ledState"):
                if key in stored_mode:
                    mode[key] = stored_mode[key]
            stored_buttons = stored_mode.get("buttons")
            if isinstance(stored_buttons, list):
                buttons = []
                for index in range(8):
                    template = mode["buttons"][index]
                    raw = stored_buttons[index] if index < len(stored_buttons) else None
                    if isinstance(raw, dict):
                        buttons.append(_merge_button(raw, template))
                    else:
                        buttons.append(copy.deepcopy(template))
                mode["buttons"] = buttons
    return config


def save_config(config: Dict[str, Any]) -> bool:
    """Simpan konfigurasi ke disk (dipakai listener & aplikasi berikutnya)."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)
        return True
    except Exception as exc:
        print(f"[CONFIG] Gagal menulis {CONFIG_FILE}: {exc}")
        return False


def get_button(config: Dict[str, Any], mode_index: int, index: int) -> Dict[str, Any]:
    return config["modes"][mode_index]["buttons"][index]


def action_summary(action: Dict[str, Any] | None) -> str:
    """Ringkasan singkat sebuah aksi untuk chip/di inspector."""
    if not isinstance(action, dict):
        return "Tidak ada"
    kind = action.get("type", "none")
    if kind == "none":
        return "Tidak ada"
    if kind == "shortcut":
        mods = "+".join(m.upper() for m in action.get("modifiers", []))
        key = action.get("key", "")
        return f"{mods}+{key}" if mods else key
    if kind == "text":
        return f"Teks: {action.get('text', '')}"
    if kind == "media":
        return f"Media: {MEDIA_ACTION_LABEL.get(action.get('mediaKey'), action.get('mediaKey'))}"
    if kind == "launch_app":
        return f"Aplikasi: {action.get('appName') or action.get('desktopId') or '-'}"
    if kind == "system_action":
        return f"Sistem: {action.get('presetName') or action.get('presetId') or '-'}"
    if kind == "bash_script":
        script = (action.get("script") or "").strip().splitlines()
        return f"Script: {script[0] if script else '-'}"
    if kind == "home_assistant":
        name = action.get("friendlyName") or action.get("entityId")
        if not name:
            return "HA: belum pilih entity"
        return f"HA: {name} → {action.get('service', '-')}"
    if kind == "ha_webhook":
        return f"Webhook: {action.get('url') or '-'}"
    if kind == "mode_toggle":
        return "Ganti mode layer"
    return kind
