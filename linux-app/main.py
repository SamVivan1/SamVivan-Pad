#!/usr/bin/env python3
"""
SamVivan MacroPad - Aplikasi native Linux (GTK4 + Libadwaita).

Semua fitur dijalankan langsung dari Python: listener serial, eksekusi aksi,
pemetaan tombol, dan Home Assistant REST — tanpa server HTTP dan tanpa web.
"""

import re
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk  # noqa: E402

_BUTTON_RE = re.compile(
    r"\[(DESKTOP|HA)\]\s+Button\s+(\d+)\s+->\s+(SINGLE|DOUBLE|HOLD)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Event serial (dipanggil dari thread listener → pindah ke main loop GTK)
# ---------------------------------------------------------------------------
def _handle_serial_line(line: str) -> bool:
    import state

    state.emit("serial-log", line=line)

    upper = line.upper()
    if "MODE: HOME ASSISTANT" in upper:
        state.set_mode(1)
    elif "MODE: DESKTOP" in upper:
        state.set_mode(0)

    match = _BUTTON_RE.search(line)
    if match:
        firmware_mode = 1 if match.group(1).upper() == "HA" else 0
        if firmware_mode != state.mode_index:
            state.set_mode(firmware_mode)
        state.emit("hardware-event",
                   index=int(match.group(2)) - 1,
                   trigger=match.group(3).lower())
    return False


def _on_serial_line(line: str) -> None:
    GLib.idle_add(_handle_serial_line, line)


# ---------------------------------------------------------------------------
# Pramuat data di background (tidak pernah memblokir main loop)
# ---------------------------------------------------------------------------
def _refresh_ha_status() -> None:
    from home_assistant import ha_client
    import state
    from ui import util

    status = ha_client.get_status(ping=False)
    if isinstance(status, dict):
        state.set_ha_status(bool(status.get("connected")),
                            str(status.get("message", "")))

    def done(result) -> None:
        if isinstance(result, dict):
            state.set_ha_status(bool(result.get("connected")),
                                str(result.get("message", "")))

    util.run_async(lambda: ha_client.get_status(ping=True), done)


def _preload_apps() -> None:
    from app_scanner import get_installed_apps
    import state
    from ui import util

    def done(result) -> None:
        state.set_apps(result if isinstance(result, list) else [])

    util.run_async(get_installed_apps, done)


# ---------------------------------------------------------------------------
# Aplikasi
# ---------------------------------------------------------------------------
class MacroPadApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id="com.samvivan.macropad",
                         flags=0)
        self.listener = None

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)

        from ui.css import load_css
        Adw.StyleManager.get_default().set_color_scheme(
            Adw.ColorScheme.FORCE_DARK)
        display = Gdk.Display.get_default()
        if display is not None:
            load_css(display)

        self.set_accels_for_action("win.save", ["<Control>s"])
        self.set_accels_for_action("app.quit", ["<Control>q"])
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)

        from serial_listener import SerialDaemonListener
        import state

        self.listener = SerialDaemonListener(on_event_callback=_on_serial_line)
        state.listener = self.listener
        self.listener.start()

        _refresh_ha_status()
        _preload_apps()

    def do_activate(self) -> None:
        if not getattr(self, "_css_loaded", False):
            from ui.css import load_css
            display = Gdk.DisplayManager.get().get_default_display()
            if display is not None:
                load_css(display)
            self._css_loaded = True
        from ui.window import MacroPadWindow
        window = self.get_active_window()
        if window is None:
            window = MacroPadWindow(self)
        window.present()

    def do_shutdown(self) -> None:
        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception as exc:  # noqa: BLE001
                print(f"[APP] Gagal menghentikan listener: {exc}")
        Adw.Application.do_shutdown(self)


def main() -> int:
    return MacroPadApplication().run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
