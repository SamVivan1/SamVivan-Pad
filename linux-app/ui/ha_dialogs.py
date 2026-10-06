#!/usr/bin/env python3
"""
SamVivan MacroPad - Dialog koneksi Home Assistant & Entity Picker.

Semua panggilan jaringan berjalan di thread terpisah; UI hanya menerima hasil
lewat GLib.idle_add sehingga jendela tidak pernah membeku.
"""

from typing import Any, Callable, Dict, List, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Pango  # noqa: E402

import state
from home_assistant import ha_client
from ui import util


# ---------------------------------------------------------------------------
# Dialog koneksi
# ---------------------------------------------------------------------------
class HaConnectionDialog(Adw.Window):
    def __init__(self, window) -> None:
        super().__init__(transient_for=window, modal=True,
                         title="Koneksi Home Assistant",
                         default_width=520, default_height=440)
        self.window = window
        self._busy = False

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle.new(
            "Koneksi Home Assistant", "REST API langsung — tanpa script"))
        toolbar.add_top_bar(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(10)
        content.set_margin_bottom(12)
        content.set_margin_start(16)
        content.set_margin_end(16)

        content.append(util.label("Home Assistant URL", css=["mp-section-title"]))
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("http://homeassistant.local:8123")
        self.url_entry.set_text(ha_client.url or "")
        content.append(self.url_entry)

        content.append(util.label("Long-Lived Access Token", css=["mp-section-title"]))
        self.token_entry = Gtk.PasswordEntry()
        self.token_entry.set_show_peek_icon(True)
        self.token_entry.set_property(
            "placeholder-text",
            "Token tersimpan (kosongkan untuk mempertahankan)"
            if ha_client.is_configured() else "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        content.append(self.token_entry)

        content.append(util.hint(
            "HA → Profile → Security → Long-Lived Access Tokens → Create."))

        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.set_css_classes(["mp-pill"])
        self.status_icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        self.status_text = util.label("Belum dicek.")
        status_box.append(self.status_icon)
        status_box.append(self.status_text)
        content.append(status_box)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions.set_margin_top(6)
        self.btn_test = util.button("Test Koneksi", "emblem-ok-symbolic",
                                    on_clicked=self._on_test)
        self.btn_reload = util.button("Muat Ulang Entities", "view-refresh-symbolic",
                                      on_clicked=self._on_reload)
        self.btn_save = util.button("Simpan", "document-save-symbolic",
                                    css=["suggested-action"],
                                    on_clicked=self._on_save)
        actions.append(self.btn_test)
        actions.append(self.btn_reload)
        actions.append(self.btn_save)
        content.append(actions)

        self.path_hint = util.hint(
            "Kredensial disimpan di ~/.config/samvivan-macropad/ha_config.json")
        content.append(self.path_hint)

        toolbar.set_content(content)
        self.set_content(toolbar)

        self._set_status("info", "Membaca konfigurasi tersimpan…")
        self._refresh_status(live=True)

    # ------------------------------------------------------------------
    def _set_status(self, kind: str, message: str) -> None:
        icons = {"ok": "emblem-ok-symbolic", "warn": "dialog-warning-symbolic",
                 "err": "dialog-error-symbolic", "info": "dialog-information-symbolic",
                 "busy": "content-loading-symbolic"}
        classes = {"ok": ["mp-pill", "mp-ok"], "warn": ["mp-pill", "mp-warn"],
                   "err": ["mp-pill", "mp-err"], "info": ["mp-pill"],
                   "busy": ["mp-pill", "mp-warn"]}
        self.status_icon.set_from_icon_name(icons.get(kind, "dialog-information-symbolic"))
        self.status_text.set_css_classes(classes.get(kind, ["mp-pill"]))
        self.status_text.set_text(message)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for widget in (self.btn_test, self.btn_reload, self.btn_save):
            widget.set_sensitive(not busy)

    def _credentials(self):
        url = self.url_entry.get_text().strip().rstrip("/")
        token = self.token_entry.get_text().strip()
        if not token and ha_client.is_configured():
            token = ha_client.token or ""
        return url, token

    def _refresh_status(self, live: bool) -> None:
        self._set_status("busy", "Memeriksa koneksi ke Home Assistant…")

        def work():
            status = ha_client.get_status(ping=live)
            return True, status

        def done(result) -> None:
            _ok, status = result if isinstance(result, tuple) and len(result) == 2 else (False, {})
            if not isinstance(status, dict):
                status = {"message": str(status)}
            connected = bool(status.get("connected"))
            message = status.get("message", "")
            if live:
                state.set_ha_status(connected, message)
            self._set_status("ok" if connected else "warn", message)
            entities = ha_client.get_entities()
            state.set_ha_entities(entities, "live" if ha_client._last_scan_live else "cache")

        util.run_async(work, done)

    def _on_test(self, _btn) -> None:
        if self._busy:
            return
        url, token = self._credentials()
        if not url:
            self._set_status("warn", "Isi Home Assistant URL dulu.")
            return
        self._set_busy(True)
        self._set_status("busy", "Menguji koneksi (maks 3 detik)…")

        def done(result) -> None:
            self._set_busy(False)
            ok, message = result if isinstance(result, tuple) else (False, str(result))
            self._set_status("ok" if ok else "err", message)
            state.set_ha_status(bool(ok), message)
            self.window.show_toast(message, "success" if ok else "error")
            if ok:
                self._load_entities(force=True)

        util.run_async(lambda: ha_client.check_connection(url, token), done)

    def _on_reload(self, _btn) -> None:
        if self._busy:
            return
        self._load_entities(force=True)

    def _load_entities(self, force: bool) -> None:
        self._set_busy(True)
        self._set_status("busy", "Memindai entity dari /api/states…")

        def done(result) -> None:
            self._set_busy(False)
            entities = result if isinstance(result, list) else []
            source = "live" if ha_client._last_scan_live else "cache"
            state.set_ha_entities(entities, source)
            self._set_status(
                "ok" if ha_client._last_scan_live else "warn",
                f"{len(entities)} entity interaktif "
                + ("ditemukan." if ha_client._last_scan_live
                   else "dari cache (HA tidak terjangkau)."),
            )
            self.window.show_toast(f"{len(entities)} entity dimuat.", "success")

        util.run_async(lambda: ha_client.get_entities(force_refresh=force), done)

    def _on_save(self, _btn) -> None:
        if self._busy:
            return
        url, token = self._credentials()
        if not url or not token:
            self._set_status("warn", "URL dan token wajib diisi.")
            return
        self._set_busy(True)
        self._set_status("busy", "Menyimpan koneksi dan memindai entity…")

        def done(result) -> None:
            self._set_busy(False)
            ok, message = result if isinstance(result, tuple) else (False, str(result))
            if not ok:
                self._set_status("err", message)
                self.window.show_toast(message, "error")
                return
            entities = ha_client.get_entities()
            state.set_ha_entities(entities, "live" if ha_client._last_scan_live else "cache")
            state.set_ha_status(True, "Tersimpan")
            self._set_status("ok", f"Tersimpan — {len(entities)} entity siap dipilih.")
            self.window.show_toast(
                f"Koneksi tersimpan. {len(entities)} entity ditemukan.", "success")
            self.close()

        util.run_async(lambda: ha_client.save_config(url, token), done)


# ---------------------------------------------------------------------------
# Entity Picker
# ---------------------------------------------------------------------------
class EntityPickerDialog(Adw.Window):
    def __init__(self, window, on_pick: Callable[[Dict[str, Any]], None]) -> None:
        super().__init__(transient_for=window, modal=True,
                         title="Pilih Entity Home Assistant",
                         default_width=760, default_height=560)
        self.window = window
        self.on_pick = on_pick
        self._search = ""
        self._domain = "all"
        self._cards: List[Dict[str, Any]] = []

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        self.title_widget = Adw.WindowTitle.new("Pilih Entity", "Memindai entity…")
        header.set_title_widget(self.title_widget)
        reload_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        reload_btn.set_tooltip_text("Scan ulang ke Home Assistant")
        reload_btn.connect("clicked", self._on_rescan)
        header.pack_end(reload_btn)
        toolbar.add_top_bar(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(6)
        content.set_margin_bottom(10)
        content.set_margin_start(12)
        content.set_margin_end(12)
        self.content_box = content
        self._empty_connect_btn: Optional[Gtk.Widget] = None

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Cari entity (nama, domain, atau entity_id)…")
        self.search.connect("search-changed", self._on_search)
        content.append(self.search)

        self.chips_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.append(self.chips_box)

        self.empty_label = util.hint("")
        content.append(self.empty_label)

        self.flow = Gtk.FlowBox()
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_max_children_per_line(4)
        self.flow.set_min_children_per_line(1)
        self.flow.set_column_spacing(10)
        self.flow.set_row_spacing(10)
        self.flow.set_homogeneous(True)
        self.flow.set_filter_func(self._filter_child)
        self.flow.connect("child-activated", self._on_child_activated)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.flow)
        content.append(scroll)

        toolbar.set_content(content)
        self.set_content(toolbar)

        state.subscribe(self._on_state_event)
        self._rebuild()
        if not state.ha_entities and ha_client.is_configured():
            self._rescan()

    # ------------------------------------------------------------------
    def _on_state_event(self, event: str, **_data: Any) -> None:
        if event in ("ha-entities-changed",):
            self._rebuild()

    def _rebuild(self) -> None:
        for child in list(self._cards):
            self.flow.remove(child["widget"])
        self._cards = []

        entities = state.ha_entities
        source_text = {"live": "scan langsung", "cache": "cache lokal"}.get(
            state.ha_entity_source, "belum ada data")
        self.title_widget.set_subtitle(f"{len(entities)} entity · {source_text}")

        theme = Gtk.IconTheme.get_for_display(self.get_display())
        for entity in entities:
            widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            widget.set_css_classes(["mp-entity"])
            widget.set_margin_top(4)
            widget.set_margin_bottom(4)

            head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            domain = entity.get("domain", "")
            image = Gtk.Image.new_from_icon_name(util.domain_icon(domain, theme))
            image.set_pixel_size(24)
            head.append(image)
            name = util.label(entity.get("friendly_name", entity.get("entity_id", "")),
                              css=["mp-entity-name"])
            name.set_ellipsize(Pango.EllipsizeMode.END)
            name.set_hexpand(True)
            head.append(name)
            widget.append(head)

            widget.append(util.hint(entity.get("entity_id", "")))
            state_row = entity.get("state")
            if state_row is not None:
                widget.append(util.hint(f"State: {state_row}"))

            self.flow.append(widget)
            self._cards.append({"widget": widget, "entity": entity})

        self._rebuild_chips()
        if not entities:
            self.empty_label.set_text(
                "Belum ada entity. Klik tombol refresh di header untuk memindai, "
                "atau periksa koneksi Home Assistant.")
            if not self._empty_connect_btn:
                self._empty_connect_btn = util.button(
                    "Atur Koneksi Home Assistant", "network-server-symbolic",
                    css=["suggested-action"], on_clicked=self._open_connection)
                self.content_box.append(self._empty_connect_btn)
            self._empty_connect_btn.set_visible(True)
        else:
            self.empty_label.set_text("")
            if self._empty_connect_btn:
                self._empty_connect_btn.set_visible(False)

    def _rebuild_chips(self) -> None:
        child = self.chips_box.get_first_child()
        while child is not None:
            following = child.get_next_sibling()
            self.chips_box.remove(child)
            child = following

        domains: List[str] = sorted({e.get("domain", "") for e in state.ha_entities} - {""})
        first: Optional[Gtk.ToggleButton] = None
        for domain in ["all"] + domains:
            button = Gtk.ToggleButton(label="Semua" if domain == "all" else domain)
            button.set_active(domain == self._domain)
            if first is None:
                first = button
            else:
                button.set_group(first)
            button.connect("toggled", self._on_domain_toggled, domain)
            self.chips_box.append(button)

    def _on_domain_toggled(self, button: Gtk.ToggleButton, domain: str) -> None:
        if not button.get_active():
            return
        self._domain = domain
        self.flow.invalidate_filter()

    def _on_search(self, entry: Gtk.SearchEntry) -> None:
        self._search = (entry.get_text() or "").strip().lower()
        self.flow.invalidate_filter()

    def _filter_child(self, child: Gtk.FlowBoxChild) -> bool:
        widget = child.get_child()
        data = next((c for c in self._cards if c["widget"] is widget), None)
        if data is None:
            return False
        entity = data["entity"]
        if self._domain != "all" and entity.get("domain") != self._domain:
            return False
        if not self._search:
            return True
        haystack = " ".join([
            entity.get("friendly_name", ""), entity.get("entity_id", ""),
            entity.get("domain", ""),
        ]).lower()
        return self._search in haystack

    def _on_child_activated(self, _flow, child: Gtk.FlowBoxChild) -> None:
        widget = child.get_child()
        data = next((c for c in self._cards if c["widget"] is widget), None)
        if not data:
            return
        try:
            self.on_pick(data["entity"])
        finally:
            self.close()

    def _open_connection(self, _btn) -> None:
        HaConnectionDialog(self.window).present()

    def _on_rescan(self, _btn) -> None:
        self._rescan()

    def _rescan(self) -> None:
        self.title_widget.set_subtitle("Memindai entity ke Home Assistant…")

        def done(result) -> None:
            entities = result if isinstance(result, list) else []
            source = "live" if ha_client._last_scan_live else "cache"
            state.set_ha_entities(entities, source)
            if not entities:
                self.window.show_toast(
                    "Tidak ada entity — HA tidak terjangkau atau belum terisi "
                    "entitas interaktif.", "error")

        util.run_async(lambda: ha_client.get_entities(force_refresh=True), done)
