#!/usr/bin/env python3
"""SamVivan MacroPad - Halaman console serial (log hardware + kirim perintah)."""

from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango  # noqa: E402

import state
from ui import util


class ConsolePage(Gtk.Box):
    def __init__(self, window) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add_css_class("mp-page")
        self.window = window
        self._line_count = 0

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.status_label = util.label("Serial: memeriksa…", css=["mp-hint"])
        self.status_label.set_hexpand(True)
        top.append(self.status_label)
        top.append(util.button("Bersihkan", "edit-clear-symbolic",
                               on_clicked=self._on_clear))
        self.append(top)

        self.view = Gtk.TextView(editable=False, cursor_visible=False,
                                 wrap_mode=Gtk.WrapMode.CHAR, monospace=True)
        self.view.set_css_classes(["mp-console"])
        self.view.set_top_margin(6)
        self.view.set_bottom_margin(6)
        self.view.set_left_margin(8)
        self.view.set_right_margin(8)
        buffer_ = self.view.get_buffer()
        self._install_tags(buffer_)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.view)
        scroll.set_min_content_height(240)
        scroll.add_css_class("mp-panel")
        self.append(scroll)

        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry = Gtk.Entry(placeholder_text="Kirim perintah ke macropad (mis. CMD:PING)…")
        self.entry.set_hexpand(True)
        self.entry.connect("activate", self._on_send)
        bottom.append(self.entry)
        bottom.append(util.button("Kirim", "mail-send-symbolic",
                                  css=["suggested-action"],
                                  on_clicked=self._on_send))
        self.append(bottom)

        state.subscribe(self._on_state_event)
        self._sync_status()
        self._append_line("[SYSTEM] Console serial siap — log hardware muncul di sini.", "system")

    # ------------------------------------------------------------------
    def _install_tags(self, buffer_) -> None:
        table = buffer_.get_tag_table()
        specs = {
            "system": {"foreground": "#8ff0a4"},
            "action": {"foreground": "#99c1f1"},
            "error": {"foreground": "#f66151"},
            "tx": {"foreground": "#f9f06b"},
            "time": {"foreground": "#9a9996"},
        }
        self._tags = {}
        for name, props in specs.items():
            tag = Gtk.TextTag(name=name)
            for key, value in props.items():
                tag.set_property(key, value)
            table.add(tag)
            self._tags[name] = tag

    def _classify(self, line: str) -> str:
        upper = line.upper()
        if "[ERROR" in upper or " FAIL]" in upper or "GAGAL" in upper:
            return "error"
        if "[ACTION]" in upper:
            return "action"
        if upper.startswith("[TX]") or line.startswith("> "):
            return "tx"
        return "system"

    def _append_line(self, text: str, kind: Optional[str] = None) -> None:
        buffer_ = self.view.get_buffer()
        kind = kind or self._classify(text)
        end = buffer_.get_end_iter()
        tags = getattr(self, "_tags", {})

        stamp = GLib.DateTime.new_now_local().format("%H:%M:%S")
        buffer_.insert_with_tags_by_name(end, f"[{stamp}] ", "time")
        end = buffer_.get_end_iter()
        buffer_.insert_with_tags_by_name(end, text + "\n", kind)

        self._line_count += 1
        if self._line_count > 1500:
            self._trim(buffer_)
        self.view.scroll_to_iter(buffer_.get_end_iter(), 0.0, False, 0.0, 1.0)

    @staticmethod
    def _trim(buffer_) -> None:
        start = buffer_.get_start_iter()
        limit = buffer_.get_iter_at_line_offset(0, 0)
        end = buffer_.get_iter_at_line(200)
        buffer_.delete(start, end)

    # ------------------------------------------------------------------
    def _on_clear(self, _btn) -> None:
        self.view.get_buffer().set_text("")
        self._line_count = 0

    def _on_send(self, *_args) -> None:
        text = self.entry.get_text().strip()
        if not text:
            return
        listener = state.listener
        ok = False
        if listener is not None:
            try:
                ok = bool(listener.send_command(text))
            except Exception as exc:  # noqa: BLE001
                self.window.show_toast(f"Gagal mengirim: {exc}", "error")
        if ok:
            self.entry.set_text("")
            self._append_line(f"> {text}", "tx")
        else:
            self.window.show_toast("Port serial belum terbuka — colok macropad dulu.", "error")

    # ------------------------------------------------------------------
    def _sync_status(self) -> None:
        if state.serial_connected:
            self.status_label.set_text(
                f"Serial: terhubung di {state.serial_port or '?'} (115200 Baud)")
        else:
            self.status_label.set_text("Serial: menunggu macropad tercolok…")

    def _on_state_event(self, event: str, **data) -> None:
        if event == "serial-log":
            self._append_line(str(data.get("line", "")))
        elif event == "serial-status-changed":
            self._sync_status()
            if data.get("connected"):
                self._append_line(
                    f"[HARDWARE] Terhubung di {data.get('port') or '?'}", "system")
