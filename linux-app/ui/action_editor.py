#!/usr/bin/env python3
"""
SamVivan MacroPad - Editor aksi per trigger (Single / Double / Hold).

Satu ActionEditor menampilkan pemilih tipe aksi + form sesuai tipe yang
dipilih. Semua perubahan langsung menulis ke state dan memancarkan event.
"""

from typing import Any, Dict, List, Optional

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango  # noqa: E402

import config as config_module
import state
from system_actions import SYSTEM_ACTION_PRESETS, execute_action
from ui import util


def _copy_action(action: Dict[str, Any]) -> Dict[str, Any]:
    import copy
    return copy.deepcopy(action)


class ActionEditor(Gtk.Box):
    """Editor satu trigger untuk tombol yang sedang dipilih."""

    def __init__(self, window, trigger: str, trigger_label: str) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.window = window
        self.trigger = trigger
        self._syncing = False

        head = util.horizontal(spacing=8)
        title = util.label(trigger_label, css=["mp-trigger-title"])
        title.set_hexpand(True)
        self.type_combo = Gtk.DropDown.new_from_strings(
            [label for _, label in config_module.ACTION_TYPES]
        )
        self.type_combo.connect("notify::selected", self._on_type_changed)
        head.append(title)
        head.append(self.type_combo)
        self.append(head)

        self.content = util.vertical(spacing=8)
        self.append(self.content)

        self.refresh()

    # ------------------------------------------------------------------
    def action(self) -> Dict[str, Any]:
        return state.current_button()[self.trigger]

    def _type_ids(self) -> List[str]:
        return [type_id for type_id, _ in config_module.ACTION_TYPES]

    def _current_index(self) -> int:
        action = self.action()
        try:
            return self._type_ids().index(action.get("type", "none"))
        except ValueError:
            return 0

    def _on_type_changed(self, *_args) -> None:
        if self._syncing:
            return
        type_id = self._type_ids()[self.type_combo.get_selected()]
        if self.action().get("type") == type_id:
            return
        state.set_action(self.trigger, config_module.default_action(type_id))
        self._rebuild()

    def refresh(self) -> None:
        self._syncing = True
        self.type_combo.set_selected(self._current_index())
        self._syncing = False
        self._rebuild()

    def _rebuild(self) -> None:
        child = self.content.get_first_child()
        while child is not None:
            following = child.get_next_sibling()
            self.content.remove(child)
            child = following

        action = self.action()
        builder = getattr(self, f"_build_{action.get('type', 'none')}", None)
        if builder is None:
            builder = self._build_none
        widget = builder(action)
        if widget is not None:
            self.content.append(widget)

    # ------------------------------------------------------------------
    # Test action (selalu di thread, hasil -> toast)
    # ------------------------------------------------------------------
    def _test_action(self, _btn=None) -> None:
        action = _copy_action(self.action())
        util.run_async(
            lambda: execute_action(action.get("type", "none"), action),
            lambda result: util.toast_result(self.window, result, "Test: "),
        )

    def _test_button(self) -> Gtk.Widget:
        return util.button("Test", "media-playback-start-symbolic",
                           css=["suggested-action", "flat"],
                           on_clicked=self._test_action)

    # ------------------------------------------------------------------
    # Builders per tipe aksi
    # ------------------------------------------------------------------
    def _build_none(self, _action) -> Gtk.Widget:
        return util.hint("Tidak ada aksi pada trigger ini — tombol diabaikan.")

    def _build_mode_toggle(self, _action) -> Gtk.Widget:
        return util.hint(
            "Mengganti layer antara Desktop Mode dan Home Assistant Mode. "
            "Layer diatur oleh firmware macropad (LED status)."
        )

    def _build_shortcut(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=8)

        mods = action.setdefault("modifiers", [])
        mod_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        mod_box.set_css_classes(["linked"])
        for modifier in config_module.MODIFIERS:
            toggle = Gtk.ToggleButton(label=modifier.upper())
            toggle.set_active(modifier in mods)
            toggle.connect("toggled", self._on_modifier_toggle, modifier, action)
            mod_box.append(toggle)
        box.append(mod_box)

        keys: List[str] = []
        for _group_name, group_keys in config_module.KEY_GROUPS:
            keys.extend(group_keys)
        combo = Gtk.DropDown.new_from_strings(keys)
        try:
            combo.set_selected(keys.index(action.get("key", "A")))
        except ValueError:
            combo.set_selected(0)
        combo.connect("notify::selected",
                      lambda w, *_: self._set_field(action, "key", keys[w.get_selected()]))

        row = util.horizontal(spacing=8)
        row.append(util.label("Target Key:", css=["mp-hint"]))
        row.append(combo)
        box.append(row)

        test_row = util.horizontal(spacing=8)
        test_row.append(self._test_button())
        box.append(test_row)
        return box

    def _on_modifier_toggle(self, button: Gtk.ToggleButton, modifier: str,
                            action: Dict[str, Any]) -> None:
        modifiers = list(action.get("modifiers", []))
        if button.get_active():
            if modifier not in modifiers:
                modifiers.append(modifier)
        elif modifier in modifiers:
            modifiers.remove(modifier)
        action["modifiers"] = [m for m in config_module.MODIFIERS if m in modifiers]
        state.mark_dirty()
        state.emit("button-changed", index=state.selected_index)

    def _build_text(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=6)
        view = Gtk.TextView(editable=True, wrap_mode=Gtk.WrapMode.CHAR, monospace=True)
        view.set_css_classes(["mp-console"])
        view.get_buffer().set_text(action.get("text", ""))
        view.get_buffer().connect("changed", self._on_text_changed, action)
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scroll.set_min_content_height(64)
        scroll.set_child(view)
        box.append(scroll)

        row = util.horizontal(spacing=8)
        row.append(self._test_button())
        box.append(row)
        return box

    def _on_text_changed(self, buffer, action: Dict[str, Any]) -> None:
        start, end = buffer.get_bounds()
        action["text"] = buffer.get_text(start, end, True)
        state.mark_dirty()
        state.emit("button-changed", index=state.selected_index)

    def _build_media(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=8)
        media_ids = [media_id for media_id, _ in config_module.MEDIA_ACTIONS]
        combo = Gtk.DropDown.new_from_strings(
            [label for _, label in config_module.MEDIA_ACTIONS]
        )
        try:
            combo.set_selected(media_ids.index(action.get("mediaKey", "VOL_UP")))
        except ValueError:
            combo.set_selected(0)
        combo.connect("notify::selected", lambda w, *_: self._set_field(
            action, "mediaKey", media_ids[w.get_selected()]))
        box.append(combo)

        row = util.horizontal(spacing=8)
        row.append(self._test_button())
        box.append(row)
        box.append(util.hint("Volume memakai wpctl/pactl; pemutar musik memakai playerctl."))
        return box

    def _build_launch_app(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=8)

        name = action.get("appName") or action.get("desktopId") or "Belum dipilih"
        row = util.horizontal(spacing=8)
        label_widget = util.label(name)
        label_widget.set_hexpand(True)
        label_widget.set_ellipsize(Pango.EllipsizeMode.END)
        row.append(label_widget)
        row.append(util.button("Pilih…", "view-more-symbolic", None,
                               self._pick_app, action))
        row.append(self._test_button())
        box.append(row)

        if action.get("desktopId"):
            box.append(util.hint(f"Desktop entry: {action['desktopId']}"))
        else:
            box.append(util.hint("Belum ada aplikasi dipilih."))
        return box

    def _pick_app(self, _btn, action: Dict[str, Any]) -> None:
        from ui.app_picker import AppPickerDialog

        def on_pick(app: Dict[str, str]) -> None:
            action["desktopId"] = app.get("id") or app.get("path", "")
            action["appName"] = app.get("name", "")
            state.mark_dirty()
            state.emit("button-changed", index=state.selected_index)
            self.refresh()

        AppPickerDialog(self.window, on_pick).present()

    def _build_system_action(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=8)
        presets = SYSTEM_ACTION_PRESETS
        preset_ids = [preset["id"] for preset in presets]
        combo = Gtk.DropDown.new_from_strings(
            [f"{preset['name']}  ·  {preset['category']}" for preset in presets]
        )
        try:
            combo.set_selected(preset_ids.index(action.get("presetId", "")))
        except ValueError:
            combo.set_selected(0)

        description = util.hint("")
        box.append(combo)
        box.append(description)

        def on_selected(widget, *_args) -> None:
            preset = presets[widget.get_selected()]
            action["presetId"] = preset["id"]
            action["presetName"] = preset["name"]
            description.set_text(preset["description"])
            state.mark_dirty()
            state.emit("button-changed", index=state.selected_index)

        combo.connect("notify::selected", on_selected)
        selected = combo.get_selected()
        if 0 <= selected < len(presets):
            description.set_text(presets[selected]["description"])

        row = util.horizontal(spacing=8)
        row.append(self._test_button())
        box.append(row)
        return box

    def _build_bash_script(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=6)
        view = Gtk.TextView(editable=True, wrap_mode=Gtk.WrapMode.CHAR, monospace=True)
        view.set_css_classes(["mp-console"])
        view.get_buffer().set_text(action.get("script", ""))
        view.get_buffer().connect("changed", self._on_script_changed, action)
        scroll = Gtk.ScrolledWindow(hexpand=True)
        scroll.set_min_content_height(72)
        scroll.set_child(view)
        box.append(scroll)

        row = util.horizontal(spacing=8)
        row.append(self._test_button())
        box.append(row)
        box.append(util.hint("Dijalankan dengan /bin/bash di background."))
        return box

    def _on_script_changed(self, buffer, action: Dict[str, Any]) -> None:
        start, end = buffer.get_bounds()
        action["script"] = buffer.get_text(start, end, True)
        state.mark_dirty()
        state.emit("button-changed", index=state.selected_index)

    def _build_ha_webhook(self, action: Dict[str, Any]) -> Gtk.Widget:
        box = util.vertical(spacing=6)
        entry = Gtk.Entry(placeholder_text="http://homeassistant.local:8123/api/webhook/my_macro")
        entry.set_text(action.get("url", ""))
        entry.set_hexpand(True)
        entry.connect("changed", lambda w: self._set_field(action, "url", w.get_text()))
        box.append(entry)

        row = util.horizontal(spacing=8)
        row.append(self._test_button())
        box.append(row)
        box.append(util.hint("POST JSON kosong (bisa diisi lewat payload) ke URL webhook HA."))
        return box

    def _build_home_assistant(self, action: Dict[str, Any]) -> Gtk.Widget:
        from home_assistant import ha_client

        box = util.vertical(spacing=8)
        theme = Gtk.IconTheme.get_for_display(self.window.get_display())

        entity_id = action.get("entityId", "")
        if not ha_client.is_configured():
            warning = util.horizontal(spacing=6)
            warning.set_css_classes(["mp-pill", "mp-warn"])
            warning.append(Gtk.Image.new_from_icon_name("dialog-warning-symbolic"))
            warning.append(util.label(
                "Home Assistant belum dikonfigurasi — atur koneksi dulu."
            ))
            box.append(warning)
        elif entity_id:
            head = util.horizontal(spacing=8)
            domain = entity_id.split(".")[0] if "." in entity_id else ""
            head.append(Gtk.Image.new_from_icon_name(util.domain_icon(domain, theme)))
            name_label = util.label(action.get("friendlyName") or entity_id,
                                    css=["mp-entity-name"])
            name_label.set_hexpand(True)
            head.append(name_label)
            head.append(util.label(f"Domain: {domain}", css=["mp-hint"]))
            box.append(head)
            box.append(util.hint(entity_id))
        else:
            box.append(util.hint("Belum ada entity dipilih."))

        buttons = util.horizontal(spacing=8)
        buttons.append(util.button("Pilih Entity", "view-list-symbolic",
                                   on_clicked=self._pick_entity))
        buttons.append(util.button("Koneksi…", "network-server-symbolic",
                                   on_clicked=self._open_ha_connection))
        box.append(buttons)

        selected = next((e for e in state.ha_entities
                         if e.get("entity_id") == entity_id), None)
        services = list((selected or {}).get("services") or ["toggle", "turn_on", "turn_off"])
        if action.get("service") not in services and action.get("entityId"):
            action["service"] = services[0]

        row = util.horizontal(spacing=8)
        row.append(util.label("Service:", css=["mp-hint"]))
        service_combo = Gtk.DropDown.new_from_strings(services)
        if action.get("service") in services:
            service_combo.set_selected(services.index(action["service"]))
        service_combo.connect(
            "notify::selected",
            lambda w, *_: self._set_field(action, "service", services[w.get_selected()]),
        )
        row.append(service_combo)

        can_test = bool(entity_id) and bool(action.get("service"))
        test_btn = self._test_button()
        test_btn.set_sensitive(can_test)
        row.append(test_btn)
        box.append(row)

        if not entity_id:
            box.append(util.hint("Klik “Pilih Entity” untuk memindai semua entity interaktif "
                                 "dari /api/states."))
        return box

    def _pick_entity(self, _btn) -> None:
        from ui.ha_dialogs import EntityPickerDialog

        def on_pick(entity: Dict[str, Any]) -> None:
            action = self.action()
            action["entityId"] = entity.get("entity_id", "")
            action["friendlyName"] = entity.get("friendly_name", "")
            action["domain"] = entity.get("domain", "")
            services = entity.get("services") or ["toggle", "turn_on", "turn_off"]
            action["service"] = services[0]
            state.mark_dirty()
            state.emit("button-changed", index=state.selected_index)
            self.refresh()

        EntityPickerDialog(self.window, on_pick).present()

    def _open_ha_connection(self, _btn) -> None:
        from ui.ha_dialogs import HaConnectionDialog
        HaConnectionDialog(self.window).present()

    # ------------------------------------------------------------------
    @staticmethod
    def _set_field(action: Dict[str, Any], field: str, value: Any) -> None:
        if action.get(field) == value:
            return
        action[field] = value
        state.mark_dirty()
        state.emit("button-changed", index=state.selected_index)
