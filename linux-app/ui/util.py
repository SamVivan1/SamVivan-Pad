#!/usr/bin/env python3
"""Helper UI: pekerjaan latar belakang, toast, ikon domain, dialog."""

from typing import Any, Callable, List, Optional, Tuple

# Ikon simbolis Adwaita per domain Home Assistant (fallback bila tema tak punya)
DOMAIN_ICONS = {
    "light": "display-brightness-symbolic",
    "switch": "media-playback-start-symbolic",
    "group": "view-grid-symbolic",
    "input_boolean": "media-playback-start-symbolic",
    "fan": "weather-windy-symbolic",
    "cover": "view-grid-symbolic",
    "climate": "weather-few-clouds-symbolic",
    "humidifier": "weather-showers-symbolic",
    "water_heater": "weather-showers-symbolic",
    "lock": "changes-prevent-symbolic",
    "vacuum": "edit-clear-all-symbolic",
    "media_player": "multimedia-player-symbolic",
    "remote": "input-gaming-symbolic",
    "scene": "preferences-desktop-weather-symbolic",
    "script": "text-x-generic-symbolic",
    "automation": "applications-engineering-symbolic",
    "button": "media-skip-forward-symbolic",
    "input_button": "media-skip-forward-symbolic",
    "timer": "alarm-symbolic",
    "number": "view-list-symbolic",
    "input_number": "view-list-symbolic",
    "select": "view-list-symbolic",
    "input_select": "view-list-symbolic",
    "text": "text-x-generic-symbolic",
    "siren": "alarm-symbolic",
    "alarm_control_panel": "changes-prevent-symbolic",
    "update": "software-update-available-symbolic",
    "tts": "audio-volume-high-symbolic",
    "default": "applications-other-symbolic",
}

ACTION_ICONS = {
    "none": "face-sad-symbolic",
    "shortcut": "input-keyboard-symbolic",
    "text": "text-x-generic-symbolic",
    "media": "audio-volume-high-symbolic",
    "launch_app": "system-run-symbolic",
    "system_action": "applications-system-symbolic",
    "bash_script": "utilities-terminal-symbolic",
    "home_assistant": "network-server-symbolic",
    "ha_webhook": "mail-send-symbolic",
    "mode_toggle": "view-grid-symbolic",
}


def domain_icon(domain: str, theme=None) -> str:
    name = DOMAIN_ICONS.get(domain, DOMAIN_ICONS["default"])
    if theme is not None and not theme.has_icon(name):
        return DOMAIN_ICONS["default"]
    return name


def action_icon(action_type: str, theme=None) -> str:
    name = ACTION_ICONS.get(action_type, DOMAIN_ICONS["default"])
    if theme is not None and not theme.has_icon(name):
        return DOMAIN_ICONS["default"]
    return name


def run_async(work: Callable[[], Any],
              on_done: Optional[Callable[[Any], None]] = None) -> None:
    """Jalankan `work` di thread terpisah, hasilnya dikirim balik ke main loop."""
    import threading
    from gi.repository import GLib

    def target() -> None:
        try:
            result = work()
        except Exception as exc:  # noqa: BLE001 - semua error diteruskan ke UI
            result = (False, str(exc))
        GLib.idle_add(_finish, result)

    def _finish(result: Any) -> bool:
        if on_done is not None:
            try:
                on_done(result)
            except Exception as exc:  # noqa: BLE001
                print(f"[UI] callback gagal: {exc}")
        return False

    threading.Thread(target=target, daemon=True).start()


def toast_result(window, result: Any, prefix: str = "") -> None:
    """tampilkan toast dari hasil tuple (ok, pesan)."""
    if isinstance(result, tuple) and len(result) == 2:
        ok, message = result
    else:
        ok, message = bool(result), str(result)
    kind = "success" if ok else "error"
    window.show_toast(f"{prefix}{message}", kind)


def vertical(spacing: int = 8, **kwargs):
    from gi.repository import Gtk
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing, **kwargs)


def horizontal(spacing: int = 8, **kwargs):
    from gi.repository import Gtk
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, **kwargs)


def label(text: str, css: Optional[List[str]] = None, xalign: float = 0.0, wrap: bool = False):
    from gi.repository import Gtk
    widget = Gtk.Label(label=text, xalign=xalign, wrap=wrap, selectable=False)
    if css:
        widget.set_css_classes(css)
    return widget


def hint(text: str):
    from gi.repository import Gtk
    widget = Gtk.Label(label=text, xalign=0.0, wrap=True)
    widget.set_css_classes(["mp-hint"])
    widget.set_selectable(False)
    return widget


def button(text: str, icon_name: Optional[str] = None, css: Optional[List[str]] = None,
           on_clicked: Optional[Callable] = None, *args):
    from gi.repository import Gtk
    if icon_name:
        widget = Gtk.Button()
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.append(Gtk.Image.new_from_icon_name(icon_name))
        content.append(Gtk.Label(label=text))
        widget.set_child(content)
    else:
        widget = Gtk.Button(label=text)
    if css:
        widget.set_css_classes(css)
    if on_clicked is not None:
        widget.connect("clicked", on_clicked, *args)
    return widget
