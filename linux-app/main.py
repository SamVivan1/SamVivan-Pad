#!/usr/bin/env python3
"""
SamVivan MacroPad - Native Linux Peripheral Desktop Application
Standard standalone Linux desktop application (like Piper, OpenRGB, Vial, Razer Synapse).
"""

import os
import sys
import time
import shutil
import subprocess

from server import start_backend, stop_backend

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, 'samvivan-macropad.svg')

def run_gtk_native_app(url: str):
    """Run native GTK3 + WebKit2 window with Ubuntu desktop integration."""
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.1')
    from gi.repository import Gtk, Gdk, WebKit2, Gio

    # Initialize GTK Application Window
    win = Gtk.Window(title="SamVivan MacroPad")
    win.set_default_size(1180, 780)
    win.set_position(Gtk.WindowPosition.CENTER)
    win.set_wmclass("samvivan-macropad", "SamVivan MacroPad")

    # Set Window Icon
    if os.path.exists(ICON_PATH):
        try:
            win.set_icon_from_file(ICON_PATH)
        except Exception:
            pass

    # WebKit2 Settings
    settings = WebKit2.Settings()
    settings.set_enable_developer_extras(False)
    settings.set_enable_webgl(True)
    settings.set_enable_smooth_scrolling(True)

    webview = WebKit2.WebView.new_with_settings(settings)
    webview.load_uri(url)

    # Scrolled window container
    scrolled = Gtk.ScrolledWindow()
    scrolled.add(webview)
    win.add(scrolled)

    # Clean shutdown on window close
    def on_window_close(*args):
        print("[*] Closing SamVivan MacroPad...")
        stop_backend()
        Gtk.main_quit()
        sys.exit(0)

    win.connect("delete-event", on_window_close)
    win.connect("destroy", on_window_close)

    win.show_all()
    print("[*] Native desktop window opened.")
    Gtk.main()

def run_browser_app_mode(url: str):
    """Fallback: Launch as standalone app window using Brave, Chromium, or Chrome."""
    browsers = ['brave-browser', 'google-chrome', 'chromium-browser']
    for b in browsers:
        if shutil.which(b):
            print(f"[*] Launching standalone window via {b}...")
            p = subprocess.Popen([b, f"--app={url}", "--class=samvivan-macropad"], start_new_session=True)
            p.wait()
            stop_backend()
            sys.exit(0)

    # Generic fallback
    import webbrowser
    print("[*] Launching in default web browser...")
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_backend()

def main():
    print("=" * 60)
    print(" SamVivan MacroPad - Native Linux Application")
    print("=" * 60)

    # 1. Start internal peripheral server
    port = start_backend(8080)
    app_url = f"http://127.0.0.1:{port}"

    # 2. Try native GTK3 + WebKit2 window first
    try:
        run_gtk_native_app(app_url)
    except Exception as e:
        print(f"[!] Native GTK window failed ({e}), falling back to standalone app mode...")
        run_browser_app_mode(app_url)

if __name__ == '__main__':
    main()
