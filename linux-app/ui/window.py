#!/usr/bin/env python3
"""SamVivan MacroPad - Jendela utama (GTK4 + Libadwaita, HIG GNOME)."""

from typing import Any, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib  # noqa: E402

import state
from ui import util
from ui.console_page import ConsolePage
from ui.keys_page import KeysPage
from ui.settings_page import ProfilesPage, SettingsPage

_PAGES = (
    ("keys", "Tombol", "input-keyboard-symbolic"),
    ("console", "Console Serial", "utilities-terminal-symbolic"),
    ("profiles", "Profil", "document-open-symbolic"),
    ("settings", "Pengaturan", "preferences-system-symbolic"),
)


class MacroPadWindow(Adw.ApplicationWindow):
    def __init__(self, app) -> None:
        super().__init__(application=app, title="SamVivan MacroPad")
        self.set_default_size(1180, 780)
        self._sidebar_syncing = False

        # --- halaman ---------------------------------------------------
        self.keys_page = KeysPage(self)
        self.console_page = ConsolePage(self)
        self.profiles_page = ProfilesPage(self)
        self.settings_page = SettingsPage(self)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE,
                               transition_duration=120)
        for name, _title, _icon in _PAGES:
            self.stack.add_named(getattr(self, f"{name}_page"), name)
        self.stack.connect("notify::visible-child", self._on_stack_changed)

        # --- sidebar ---------------------------------------------------
        self._sidebar_expanded = True
        self._expanded_sidebar_width: Optional[int] = None
        self._sidebar_rows = []
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("navigation-sidebar")
        self.sidebar_list.connect("row-selected", self._on_sidebar_selected)
        for name, title, icon in _PAGES:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            image = Gtk.Image.new_from_icon_name(icon)
            label = Gtk.Label(label=title)
            label.set_xalign(0.0)
            box.append(image)
            box.append(label)
            row.set_child(box)
            row.set_activatable(True)
            row._page_name = name  # noqa: SLF001 - penanda internal sederhana
            self.sidebar_list.append(row)
            self._sidebar_rows.append({
                "name": name, "title": title,
                "box": box, "image": image, "label": label, "row": row,
            })

        sidebar_page = Adw.NavigationPage.new(self.sidebar_list, "Navigasi")
        content_page = Adw.NavigationPage.new(self.stack, "SamVivan MacroPad")

        split = Adw.NavigationSplitView()
        split.set_sidebar(sidebar_page)
        split.set_content(content_page)
        split.set_collapsed(False)          # sidebar selalu terlihat (ikon saja saat ciut)
        split.set_min_sidebar_width(160)
        split.set_max_sidebar_width(220)
        self.split = split
        split.connect("notify::collapsed", self._on_collapsed_changed)

        self.connect("map", lambda *_: GLib.idle_add(self._apply_sidebar_mode))

        # --- header bar -------------------------------------------------
        self.title_widget = Adw.WindowTitle.new(
            "SamVivan MacroPad", self._mode_subtitle())

        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_icon_name("open-menu-symbolic")
        self.menu_button.set_menu_model(self._build_menu())
        self.menu_button.set_tooltip_text("Menu")

        # Tombol sidebar: perluas / ciutkan (ikon saja vs ikon+label)
        self.sidebar_toggle = Gtk.ToggleButton()
        self.sidebar_toggle.set_icon_name("pan-start-symbolic")
        self.sidebar_toggle.set_tooltip_text("Ciutkan sidebar (ikon saja)")
        self.sidebar_toggle.set_active(True)
        self.sidebar_toggle.connect("toggled", self._on_sidebar_toggled)

        self.serial_pill = Gtk.Button(label="Serial: memeriksa…")
        self.serial_pill.set_css_classes(["mp-pill", "mp-warn"])
        self.serial_pill.connect("clicked", self._on_serial_pill_clicked)

        self.ha_pill = Gtk.Button(label="HA: memeriksa…")
        self.ha_pill.set_css_classes(["mp-pill", "mp-warn"])
        self.ha_pill.connect("clicked", self._on_ha_pill_clicked)

        self.save_button = util.button("Simpan", "document-save-symbolic",
                                       ["suggested-action"], self._on_save_clicked)

        header = Adw.HeaderBar()
        header.set_title_widget(self.title_widget)
        header.pack_start(self.sidebar_toggle)
        header.pack_start(self.menu_button)
        header.pack_end(self.save_button)
        header.pack_end(self.ha_pill)
        header.pack_end(self.serial_pill)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(split)

        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(toolbar)
        self.set_content(self.toast_overlay)

        # --- aksi -------------------------------------------------------
        self._install_actions()

        # --- event bus --------------------------------------------------
        state.subscribe(self._on_state_event)
        self._sync_pills()
        self._sync_save_button()
        GLib.timeout_add_seconds(3, self._poll_serial)

    # ------------------------------------------------------------------
    # Menu & aksi
    # ------------------------------------------------------------------
    @staticmethod
    def _build_menu() -> Gio.Menu:
        menu = Gio.Menu()

        profile = Gio.Menu()
        profile.append("Impor Profil…", "win.import-profile")
        profile.append("Ekspor Profil…", "win.export-profile")
        menu.append_submenu("Profil", profile)

        presets = Gio.Menu()
        presets.append("Default (Desktop dan Native HA)", "win.preset-default")
        presets.append("Productivity", "win.preset-productivity")
        presets.append("Media", "win.preset-media")
        menu.append_submenu("Preset Bawaan", presets)

        menu.append("Tentang SamVivan MacroPad", "win.about")
        return menu

    def _install_actions(self) -> None:
        def add(name: str, handler) -> None:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", handler)
            self.add_action(action)

        add("save", lambda *_: self._on_save_clicked(None))
        add("import-profile", lambda *_: self.profiles_page._on_import(None))
        add("export-profile", lambda *_: self.profiles_page._on_export(None))
        add("preset-default",
            lambda *_: self.profiles_page._on_apply_preset(None, "default"))
        add("preset-productivity",
            lambda *_: self.profiles_page._on_apply_preset(None, "productivity"))
        add("preset-media",
            lambda *_: self.profiles_page._on_apply_preset(None, "media"))
        add("about", lambda *_: self._show_about())

    def _show_about(self) -> None:
        Adw.AboutWindow(
            transient_for=self,
            application_name="SamVivan MacroPad",
            application_icon="samvivan-macropad",
            version="2.5",
            developer_name="SamVivan",
            developers=["SamVivan"],
            license_type=Gtk.License.MIT_X11,
            comments="Aplikasi native GTK4 untuk makropad 8 tombol "
                     "berbasis serial — Home Assistant REST, pemetaan aksi "
                     "lokal, tanpa server web.",
        ).present()

    # ------------------------------------------------------------------
    # Toast
    # ------------------------------------------------------------------
    def show_toast(self, message: str, kind: str = "info") -> None:
        toast = Adw.Toast(title=message)
        toast.set_timeout(6 if kind == "error" else 4)
        self.toast_overlay.add_toast(toast)

    # ------------------------------------------------------------------
    # Navigasi & sidebar
    # ------------------------------------------------------------------
    @staticmethod
    def _mode_subtitle() -> str:
        return "Home Assistant Mode" if state.mode_index == 1 else "Desktop Mode"

    def _apply_sidebar_mode(self) -> None:
        """Terapkan mode sidebar: expanded (ikon+label, lebar pas teks)
        atau collapsed (ikon saja, sidebar sempit)."""
        expanded = self._sidebar_expanded

        for info in self._sidebar_rows:
            info["label"].set_visible(expanded)
            info["box"].set_halign(Gtk.Align.START if expanded else Gtk.Align.CENTER)
            info["row"].set_tooltip_text(None if expanded else info["title"])

        if expanded and self._expanded_sidebar_width is None:
            natural = self._measure_sidebar_width()
            self._expanded_sidebar_width = max(160, natural + 4)
        width = self._expanded_sidebar_width if expanded else 52

        self.split.set_min_sidebar_width(width)
        self.split.set_max_sidebar_width(width)
        self._sidebar_syncing = True
        self.sidebar_toggle.set_active(expanded)
        self._sidebar_syncing = False
        self.sidebar_toggle.set_icon_name(
            "pan-start-symbolic" if expanded else "pan-end-symbolic")
        self.sidebar_toggle.set_tooltip_text(
            "Ciutkan sidebar (ikon saja)" if expanded
            else "Perluas sidebar (ikon + teks)")

    def _measure_sidebar_width(self) -> int:
        """Lebar alami daftar navigasi (sampai akhir huruf teks)."""
        try:
            return self.sidebar_list.measure(Gtk.Orientation.HORIZONTAL, -1)[1]
        except Exception:  # noqa: BLE001 - ukuran belum siap
            return 180

    def _on_sidebar_selected(self, _listbox, row) -> None:
        if self._sidebar_syncing or row is None:
            return
        self.stack.set_visible_child_name(row._page_name)  # noqa: SLF001
        # bila konten sedang tertutup (mode jendela sempit), buka kontennya
        if self.split.get_collapsed():
            self.split.set_show_content(True)
            self._sidebar_syncing = True
            self.sidebar_toggle.set_active(True)
            self._sidebar_syncing = False

    def _on_collapsed_changed(self, split, *_args) -> None:
        collapsed = split.get_collapsed()
        self._sidebar_syncing = True
        if collapsed:
            self.sidebar_toggle.set_active(split.get_show_content())
        else:
            self.sidebar_toggle.set_active(self._sidebar_expanded)
        self._sidebar_syncing = False

    def _on_sidebar_toggled(self, button: Gtk.ToggleButton) -> None:
        if self._sidebar_syncing:
            return
        if self.split.get_collapsed():
            self.split.set_show_content(button.get_active())
        else:
            self._sidebar_expanded = button.get_active()
            self._apply_sidebar_mode()

    def _on_stack_changed(self, *_args) -> None:
        name = self.stack.get_visible_child_name()
        self._sidebar_syncing = True
        row = self.sidebar_list.get_row_at_index(
            [p[0] for p in _PAGES].index(name) if name else 0)
        if row is not None:
            self.sidebar_list.select_row(row)
        self._sidebar_syncing = False

    def _on_serial_pill_clicked(self, _btn) -> None:
        self.stack.set_visible_child_name("console")

    def _on_ha_pill_clicked(self, _btn) -> None:
        from ui.ha_dialogs import HaConnectionDialog
        HaConnectionDialog(self).present()

    def _on_save_clicked(self, _btn) -> None:
        if state.save():
            self.show_toast("Konfigurasi tersimpan.", "success")
        else:
            self.show_toast("Gagal menyimpan konfigurasi.", "error")

    # ------------------------------------------------------------------
    # Sinkronisasi pill / tombol
    # ------------------------------------------------------------------
    def _sync_pills(self) -> None:
        if state.serial_connected:
            self.serial_pill.set_label(f"Serial: {state.serial_port or '?'}")
            self.serial_pill.set_css_classes(["mp-pill", "mp-ok"])
        else:
            self.serial_pill.set_label("Serial: —")
            self.serial_pill.set_css_classes(["mp-pill", "mp-err"])
        self.serial_pill.set_tooltip_text(
            "Klik untuk membuka console serial" if state.serial_connected
            else "Macropad belum terdeteksi — colok USB lalu buka console")

        if state.ha_connected:
            self.ha_pill.set_label("HA: Terhubung")
            self.ha_pill.set_css_classes(["mp-pill", "mp-ok"])
        elif not state.ha_message:
            self.ha_pill.set_label("HA: memeriksa…")
            self.ha_pill.set_css_classes(["mp-pill", "mp-warn"])
        else:
            self.ha_pill.set_label("HA: terputus")
            self.ha_pill.set_css_classes(["mp-pill", "mp-warn"])
        self.ha_pill.set_tooltip_text(state.ha_message or "Status Home Assistant")

    def _sync_save_button(self) -> None:
        self.save_button.set_sensitive(state.dirty)
        if state.dirty:
            self.save_button.set_tooltip_text("Simpan perubahan (Ctrl+S)")
        else:
            self.save_button.set_tooltip_text("Konfigurasi sudah tersimpan")

    def _poll_serial(self) -> bool:
        listener = state.listener
        if listener is not None:
            open_port = getattr(listener, "ser", None)
            connected = bool(open_port is not None and open_port.is_open)
            port = listener.last_connected_port if connected else None
            state.set_serial_status(connected, port)
        return True

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------
    def _on_state_event(self, event: str, **data: Any) -> None:
        if event == "mode-changed":
            self.title_widget.set_subtitle(self._mode_subtitle())
        elif event in ("serial-status-changed", "ha-status-changed"):
            self._sync_pills()
        elif event in ("dirty-changed", "config-saved"):
            self._sync_save_button()
            if event == "config-saved" and data.get("ok") is False:
                self.show_toast("Gagal menyimpan konfigurasi.", "error")
