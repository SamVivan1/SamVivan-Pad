#!/usr/bin/env python3
"""
SamVivan MacroPad - Ubuntu System Actions & Automation Engine
Handles audio controls, desktop window management, screenshots, bash scripts, and Home Assistant webhooks.
"""

import subprocess
import shutil
import urllib.request
import urllib.parse
import json
from typing import Dict, Any, Tuple, List

# List of predefined interactive actions that require no coding
SYSTEM_ACTION_PRESETS = [
    {
        "id": "mic_toggle_mute",
        "name": "Toggle Microphone Mute",
        "category": "Audio",
        "description": "Mute/Unmute mikrofon saat ini (Meeting/Discord)"
    },
    {
        "id": "volume_up_5",
        "name": "Volume Up (+5%)",
        "category": "Audio",
        "description": "Naikkan volume suara 5%"
    },
    {
        "id": "volume_down_5",
        "name": "Volume Down (-5%)",
        "category": "Audio",
        "description": "Turunkan volume suara 5%"
    },
    {
        "id": "volume_toggle_mute",
        "name": "Toggle Speaker Mute",
        "category": "Audio",
        "description": "Mute/Unmute speaker audio output"
    },
    {
        "id": "lock_screen",
        "name": "Lock Ubuntu Session",
        "category": "System",
        "description": "Kunci layar desktop Ubuntu seketika"
    },
    {
        "id": "open_terminal",
        "name": "Open New Terminal",
        "category": "System",
        "description": "Buka jendela terminal baru"
    },
    {
        "id": "screenshot_interactive",
        "name": "Interactive Screenshot (Area)",
        "category": "System",
        "description": "Ambil screenshot area layar terpilih"
    },
    {
        "id": "media_play_pause",
        "name": "Media Play / Pause",
        "category": "Media",
        "description": "Play atau pause pemutar musik / YouTube via playerctl"
    },
    {
        "id": "media_next",
        "name": "Media Next Track",
        "category": "Media",
        "description": "Lagu berikutnya via playerctl"
    },
    {
        "id": "media_prev",
        "name": "Media Previous Track",
        "category": "Media",
        "description": "Lagu sebelumnya via playerctl"
    }
]

def execute_action(action_type: str, action_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Execute a configured action based on its type and payload."""
    try:
        # 1. Launch native desktop application
        if action_type == 'launch_app':
            from app_scanner import launch_app
            desktop_id = action_data.get('desktopId') or action_data.get('path')
            return launch_app(desktop_id)

        # 2. Preset system actions (Mic, Audio, Lock, etc.)
        elif action_type == 'system_action':
            preset_id = action_data.get('presetId')
            return _execute_system_preset(preset_id)

        # 3. Custom Bash Script execution
        elif action_type == 'bash_script':
            script_text = action_data.get('script', '').strip()
            if not script_text:
                return False, "Script content is empty"
            subprocess.Popen(script_text, shell=True, executable='/bin/bash', start_new_session=True)
            return True, "Bash script dispatched in background"

        # 4. Home Assistant Webhook / REST Call
        elif action_type == 'ha_webhook':
            url = action_data.get('url', '').strip()
            payload = action_data.get('payload', {})
            if not url:
                return False, "Home Assistant Webhook URL is empty"
            
            data_bytes = json.dumps(payload).encode('utf-8') if payload else b'{}'
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                status = response.status
            return True, f"Webhook sent to Home Assistant (HTTP {status})"

        # 5. Native Home Assistant Service Call (No Bash scripts needed!)
        elif action_type in ['home_assistant', 'ha_service']:
            from home_assistant import ha_client
            domain = action_data.get('domain', '')
            service = action_data.get('service', 'toggle')
            entity_id = action_data.get('entityId') or action_data.get('entity_id', '')
            data = action_data.get('data') or {}

            if not domain and '.' in entity_id:
                domain = entity_id.split('.')[0]

            if not domain or not service:
                return False, "Home Assistant domain atau service belum disetel"

            return ha_client.call_service(domain, service, entity_id, data)

        return False, f"Unknown action type: {action_type}"

    except Exception as e:
        return False, f"Action execution error: {str(e)}"

def _execute_system_preset(preset_id: str) -> Tuple[bool, str]:
    """Execute built-in hardware & OS automation commands."""
    has_wpctl = bool(shutil.which('wpctl'))
    has_pactl = bool(shutil.which('pactl'))
    has_playerctl = bool(shutil.which('playerctl'))

    # Microphone Mute Toggle
    if preset_id == 'mic_toggle_mute':
        if has_wpctl:
            subprocess.run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SOURCE@', 'toggle'], check=False)
            return True, "Toggled mic mute via wpctl"
        elif has_pactl:
            subprocess.run(['pactl', 'set-source-mute', '@DEFAULT_SOURCE@', 'toggle'], check=False)
            return True, "Toggled mic mute via pactl"
        else:
            subprocess.run(['amixer', 'set', 'Capture', 'toggle'], check=False)
            return True, "Toggled mic mute via amixer"

    # Speaker Mute Toggle
    elif preset_id == 'volume_toggle_mute':
        if has_wpctl:
            subprocess.run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle'], check=False)
            return True, "Toggled speaker mute via wpctl"
        elif has_pactl:
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'], check=False)
            return True, "Toggled speaker mute via pactl"

    # Volume Up 5%
    elif preset_id == 'volume_up_5':
        if has_wpctl:
            subprocess.run(['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%+'], check=False)
            return True, "Volume +5% via wpctl"
        elif has_pactl:
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'], check=False)
            return True, "Volume +5% via pactl"

    # Volume Down 5%
    elif preset_id == 'volume_down_5':
        if has_wpctl:
            subprocess.run(['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%-'], check=False)
            return True, "Volume -5% via wpctl"
        elif has_pactl:
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'], check=False)
            return True, "Volume -5% via pactl"

    # Lock Screen
    elif preset_id == 'lock_screen':
        if shutil.which('loginctl'):
            subprocess.run(['loginctl', 'lock-session'], check=False)
            return True, "Locked screen via loginctl"
        elif shutil.which('xdg-screensaver'):
            subprocess.run(['xdg-screensaver', 'lock'], check=False)
            return True, "Locked screen via xdg-screensaver"

    # Open Terminal
    elif preset_id == 'open_terminal':
        terms = ['gnome-terminal', 'x-terminal-emulator', 'alacritty', 'kitty', 'konsole', 'xfce4-terminal']
        for t in terms:
            if shutil.which(t):
                subprocess.Popen([t], start_new_session=True)
                return True, f"Opened terminal: {t}"

    # Screenshot
    elif preset_id == 'screenshot_interactive':
        if shutil.which('gnome-screenshot'):
            subprocess.Popen(['gnome-screenshot', '-a'], start_new_session=True)
            return True, "Triggered interactive screenshot"
        else:
            # Trigger via keyboard simulation or notify
            subprocess.Popen(['notify-send', 'MacroPad', 'Gunakan PrintScreen untuk screenshot'], start_new_session=True)
            return True, "Screenshot requested"

    # Media Controls via playerctl
    elif preset_id in ['media_play_pause', 'media_next', 'media_prev']:
        if has_playerctl:
            cmd = 'play-pause' if preset_id == 'media_play_pause' else ('next' if preset_id == 'media_next' else 'previous')
            subprocess.run(['playerctl', cmd], check=False)
            return True, f"playerctl {cmd}"
        else:
            return False, "playerctl not installed (sudo apt install playerctl)"

    return False, f"Unknown preset: {preset_id}"
