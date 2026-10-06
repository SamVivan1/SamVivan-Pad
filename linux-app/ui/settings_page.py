#!/usr/bin/env python3
"""SamVivan MacroPad - Halaman Profil (import/export/preset) dan Pengaturan."""

from typing import Any, Dict, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib  # noqa: E402

import config as config_module
import state
from ui import util


def _json_filter() -> Gtk.FileFilter:
    file_filter = Gtk.FileFilter()
    file_filter.set_name("Profil JSON (*.json)")
    file_filter.add_pattern("*.json")
    return file_filter


def _finish_open(dialog, result, on_text) -> None:
    try:
        file = dialog.open_finish(result)
    except GLib.Error:
        return
    if file is None:
        return
    path = file.get_path()
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as handle:
            on_text(handle.read(), path)
    except Exception as exc:  # noqa: BLE001
        on_text(None, str(exc))


class ProfilesPage(Gtk.Box):
    def __init__(self, window) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window = window

        page = Adw.PreferencesPage()
        page.set_title("Profil")
        page.set_icon_name("document-open-symbolic")

        # --- Profil saat ini -------------------------------------------
        current = Adw.PreferencesGroup(title="Profil Saat Ini")
        self.path_row = Adw.ActionRow(
            title="File konfigurasi",
            subtitle=config_module.CONFIG_FILE,
        )
        current.add(self.path_row)

        self.state_row = Adw.ActionRow(title="Perubahan", subtitle="Tersimpan")
        self.save_button = util.button("Simpan", "document-save-symbolic",
                                       css=["suggested-action"],
                                       on_clicked=self._on_save)
        self.save_button.set_valign(Gtk.Align.CENTER)
        self.state_row.add_suffix(self.save_button)
        current.add(self.state_row)

        io_row = Adw.ActionRow(
            title="Impor / Ekspor",
            subtitle="Simpan profil sebagai file JSON atau muat profil lama.",
        )
        import_button = util.button("Impor…", "document-open-symbolic",
                                    on_clicked=self._on_import)
        export_button = util.button("Ekspor…", "document-save-as-symbolic",
                                    on_clicked=self._on_export)
        for widget in (import_button, export_button):
            widget.set_valign(Gtk.Align.CENTER)
            io_row.add_suffix(widget)
        current.add(io_row)
        page.add(current)

        # --- Preset -----------------------------------------------------
        presets_group = Adw.PreferencesGroup(
            title="Preset Bawaan",
            description="Mengganti seluruh pemetaan tombol — simpan setelah cocok.",
        )
        for key, title, subtitle in config_module.PRESET_ITEMS:
            row = Adw.ActionRow(title=title, subtitle=subtitle, activatable=True)
            apply_button = util.button(
                "Terapkan", "emblem-default-symbolic", None,
                self._on_apply_preset, key)
            apply_button.set_valign(Gtk.Align.CENTER)
            row.add_suffix(apply_button)
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            row.connect("activated", self._on_apply_preset, key)
            presets_group.add(row)
        page.add(presets_group)

        info = Adw.PreferencesGroup(title="Tentang")
        info.add(Adw.ActionRow(
            title="SamVivan MacroPad v2.5",
            subtitle="Aplikasi native GTK4 untuk Ubuntu / GNOME — 8 tombol, "
                     "Home Assistant REST, tanpa script.",
        ))
        page.add(info)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(page)
        self.append(scroll)

        state.subscribe(self._on_state_event)
        self._sync_state()

    # ------------------------------------------------------------------
    def _sync_state(self) -> None:
        if state.dirty:
            self.state_row.set_subtitle("Belum disimpan (Ctrl+S untuk simpan)")
            self.save_button.set_sensitive(True)
        else:
            self.state_row.set_subtitle("Tersimpan ke disk")
            self.save_button.set_sensitive(False)

    def _on_state_event(self, event: str, **_data: Any) -> None:
        if event in ("dirty-changed", "config-saved", "config-replaced"):
            self._sync_state()
            if event == "config-replaced":
                self.window.show_toast("Profil dimuat.", "success")

    def _on_save(self, _btn) -> None:
        if state.save():
            self.window.show_toast("Konfigurasi tersimpan permanen di "
                                   f"{config_module.CONFIG_FILE}", "success")
        else:
            self.window.show_toast("Gagal menyimpan konfigurasi.", "error")

    def _on_import(self, _btn) -> None:
        def on_text(text: Optional[str], info: str) -> None:
            if text is None:
                self.window.show_toast(f"Gagal membaca file: {info}", "error")
                return
            import json
            try:
                data: Dict[str, Any] = json.loads(text)
            except Exception as exc:  # noqa: BLE001
                self.window.show_toast(f"JSON tidak valid: {exc}", "error")
                return
            ok, message = config_module.normalize_config(data)
            if not ok:
                self.window.show_toast(f"Format profil tidak valid: {message}", "error")
                return
            state.set_config(data, source="import")
            self.window.show_toast(f"Profil dari {info} dimuat — jangan lupa Simpan.", "success")

        dialog = Gtk.FileDialog(title="Impor Profil MacroPad")
        dialog.set_default_filter(_json_filter())
        dialog.open(self.window, None, lambda d, res: _finish_open(d, res, on_text))

    def _on_export(self, _btn) -> None:
        dialog = Gtk.FileDialog(title="Ekspor Profil MacroPad")
        dialog.set_default_filter(_json_filter())
        dialog.set_initial_name(
            f"samvivan-macropad-profile-{GLib.DateTime.new_now_local().format('%Y-%m-%d')}.json")

        def on_save(dlg, result) -> None:
            try:
                file = dlg.save_finish(result)
            except GLib.Error:
                return
            if file is None or not file.get_path():
                return
            try:
                import json
                with open(file.get_path(), "w", encoding="utf-8") as handle:
                    json.dump(state.cfg, handle, indent=2, ensure_ascii=False)
                self.window.show_toast("Profil berhasil diekspor.", "success")
            except Exception as exc:  # noqa: BLE001
                self.window.show_toast(f"Gagal menulis file: {exc}", "error")

        dialog.save(self.window, None, on_save)

    def _on_apply_preset(self, _widget, key: str) -> None:
        state.set_config(config_module.apply_preset(key), source="preset")
        state.save()
        title = next((t for k, t, _ in config_module.PRESET_ITEMS if k == key), key)
        self.window.show_toast(f"Preset “{title}” diterapkan.", "success")


# ---------------------------------------------------------------------------
class SettingsPage(Gtk.Box):
    def __init__(self, window) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window = window

        page = Adw.PreferencesPage()
        page.set_title("Pengaturan")
        page.set_icon_name("preferences-system-symbolic")

        # --- Timing -----------------------------------------------------
        timing = Adw.PreferencesGroup(
            title="Parameter Waktu (Timing Engine)",
            description="Nilai bawaan firmware: debounce 25 ms, click 250 ms, "
                        "hold 450 ms.",
        )
        for field, title, minimum, maximum in (
            ("debounceMs", "Debounce Filter (ms)", 0, 200),
            ("clickTimeoutMs", "Click Timeout (ms)", 50, 2000),
            ("holdTimeoutMs", "Hold Timeout (ms)", 100, 3000),
        ):
            row = Adw.SpinRow.new_with_range(minimum, maximum, 5)
            row.set_title(title)
            row.set_value(float(state.cfg.get(field, 0)))
            row.connect("notify::value", self._on_timing, field)
            timing.add(row)
        page.add(timing)

        # --- Home Assistant --------------------------------------------
        ha_group = Adw.PreferencesGroup(title="Home Assistant")
        self.ha_row = Adw.ActionRow(title="Koneksi", subtitle="Memeriksa…")
        ha_button = util.button("Koneksi…", "network-server-symbolic",
                                on_clicked=self._on_ha_connect)
        ha_button.set_valign(Gtk.Align.CENTER)
        self.ha_row.add_suffix(ha_button)
        ha_group.add(self.ha_row)

        self.ha_entity_row = Adw.ActionRow(
            title="Entity tersedia", subtitle=f"{len(state.ha_entities)} entity")
        reload_button = util.button("Muat Ulang", "view-refresh-symbolic",
                                    on_clicked=self._on_ha_reload)
        reload_button.set_valign(Gtk.Align.CENTER)
        self.ha_entity_row.add_suffix(reload_button)
        ha_group.add(self.ha_entity_row)
        page.add(ha_group)

        # --- Aplikasi ---------------------------------------------------
        apps_group = Adw.PreferencesGroup(title="Aplikasi Terpasang")
        self.apps_row = Adw.ActionRow(
            title="Pemindai aplikasi (.desktop)",
            subtitle=f"{len(state.installed_apps)} aplikasi")
        rescan_button = util.button("Pindai Ulang", "view-refresh-symbolic",
                                    on_clicked=self._on_rescan_apps)
        rescan_button.set_valign(Gtk.Align.CENTER)
        self.apps_row.add_suffix(rescan_button)
        apps_group.add(self.apps_row)
        page.add(apps_group)

        # --- Info -------------------------------------------------------
        info = Adw.PreferencesGroup(title="Informasi")
        info.add(Adw.ActionRow(title="Konfigurasi", subtitle=config_module.CONFIG_FILE))
        info.add(Adw.ActionRow(
            title="Kredensial HA",
            subtitle="~/.config/samvivan-macropad/ha_config.json",
        ))
        info.add(Adw.ActionRow(
            title="Runtime",
            subtitle="GTK4 + Libadwaita, listener serial langsung (tanpa server HTTP)",
        ))
        page.add(info)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(page)
        self.append(scroll)

        state.subscribe(self._on_state_event)
        self._sync_ha()

    # ------------------------------------------------------------------
    def _on_timing(self, row, *_args, field: str) -> None:
        value = int(row.get_value())
        if state.cfg.get(field) != value:
            state.set_timing(field, value)

    def _sync_ha(self) -> None:
        if state.ha_connected:
            self.ha_row.set_subtitle(f"Terhubung — {state.ha_message}")
        elif state.ha_message:
            self.ha_row.set_subtitle(state.ha_message)
        else:
            self.ha_row.set_subtitle("Belum dikonfigurasi")
        self.ha_entity_row.set_subtitle(f"{len(state.ha_entities)} entity "
                                        f"({state.ha_entity_source})")

    def _on_state_event(self, event: str, **_data: Any) -> None:
        if event in ("ha-status-changed", "ha-entities-changed"):
            self._sync_ha()
        elif event == "apps-changed":
            self.apps_row.set_subtitle(f"{len(state.installed_apps)} aplikasi")

    def _on_ha_connect(self, _btn) -> None:
        from ui.ha_dialogs import HaConnectionDialog
        HaConnectionDialog(self.window).present()

    def _on_ha_reload(self, _btn) -> None:
        from home_assistant import ha_client
        self.window.show_toast("Memindai entity…", "info")

        def done(result) -> None:
            entities = result if isinstance(result, list) else []
            source = "live" if ha_client._last_scan_live else "cache"
            state.set_ha_entities(entities, source)
            self.window.show_toast(f"{len(entities)} entity dimuat.", "success")

        util.run_async(lambda: ha_client.get_entities(force_refresh=True), done)

    def _on_rescan_apps(self, _btn) -> None:
        from app_scanner import get_installed_apps
        self.window.show_toast("Memindai aplikasi .desktop…", "info")

        def done(result) -> None:
            apps = result if isinstance(result, list) else []
            state.set_apps(apps)
            self.window.show_toast(f"{len(apps)} aplikasi ditemukan.", "success")

        util.run_async(lambda: get_installed_apps(force_refresh=True), done)
