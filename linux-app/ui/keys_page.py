#!/usr/bin/env python3
"""
SamVivan MacroPad - Halaman konfigurasi tombol.

Grid visual 8 keycap + switch mode + inspector aksi per trigger.
"""

from typing import Any, Dict, List, Optional

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango  # noqa: E402

import config as config_module
import state
from ui.action_editor import ActionEditor
from ui import util


class KeysPage(Gtk.Box):
    def __init__(self, window) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add_css_class("mp-page")
        self.window = window
        self._syncing = False
        self.cards: List[Dict[str, Any]] = []

        self.append(self._build_header())

        panes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        panes.set_vexpand(True)

        grid_host = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        grid_host.set_hexpand(True)
        grid_host.set_valign(Gtk.Align.CENTER)
        grid_host.set_halign(Gtk.Align.CENTER)
        grid_host.add_css_class("mp-chassis")

        self.grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        self.grid.set_halign(Gtk.Align.CENTER)
        for index in range(8):
            card = self._build_card(index)
            self.cards.append(card)
            self.grid.attach(card["widget"], index % 4, index // 4, 1, 1)
        grid_host.append(self.grid)
        panes.append(grid_host)

        self.inspector = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.inspector.set_size_request(380, -1)
        self.inspector.add_css_class("mp-inspector")
        inspector_scroll = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
        inspector_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        inspector_scroll.set_child(self.inspector)
        inspector_scroll.add_css_class("mp-panel")
        inspector_scroll.set_size_request(390, -1)
        panes.append(inspector_scroll)

        self.append(panes)

        state.subscribe(self._on_state_event)
        self._sync_mode_switch()
        self.refresh_grid()
        self.rebuild_inspector()

    # ------------------------------------------------------------------
    # Header: mode switch + timing
    # ------------------------------------------------------------------
    def _build_header(self) -> Gtk.Widget:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        self.mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.mode_box.set_css_classes(["linked", "mp-mode-switch"])
        self.mode_buttons: List[Gtk.ToggleButton] = []
        for index, name in enumerate(["Desktop Mode", "Home Assistant Mode"]):
            button = Gtk.ToggleButton(label=name)
            button.set_active(index == state.mode_index)
            if index > 0:
                button.set_group(self.mode_buttons[0])
            button.connect("toggled", self._on_mode_toggled, index)
            self.mode_buttons.append(button)
            self.mode_box.append(button)
        row.append(self.mode_box)

        self.timing_label = util.label(self._timing_text(), css=["mp-hint"])
        self.timing_label.set_hexpand(True)
        self.timing_label.set_halign(Gtk.Align.END)
        row.append(self.timing_label)
        return row

    @staticmethod
    def _timing_text() -> str:
        cfg = state.cfg
        return (f"Debounce {cfg['debounceMs']} ms  ·  "
                f"Click {cfg['clickTimeoutMs']} ms  ·  "
                f"Hold {cfg['holdTimeoutMs']} ms")

    def _on_mode_toggled(self, button: Gtk.ToggleButton, index: int) -> None:
        if self._syncing or not button.get_active():
            return
        state.set_mode(index)

    def _sync_mode_switch(self) -> None:
        self._syncing = True
        self.mode_buttons[state.mode_index].set_active(True)
        self._syncing = False

    # ------------------------------------------------------------------
    # Kartu tombol
    # ------------------------------------------------------------------
    def _build_card(self, index: int) -> Dict[str, Any]:
        button = Gtk.Button()
        button.set_css_classes(["mp-key"])
        button.set_has_frame(False)
        button.set_size_request(150, 118)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        iden = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        index_label = util.label(f"B{index + 1}", css=["mp-key-index"])
        index_label.set_xalign(0.0)
        iden.append(index_label)
        pin_label = util.label(f"GPIO {config_module.PINOUT[index]}", css=["mp-key-pin"])
        pin_label.set_xalign(0.0)
        iden.append(pin_label)
        head.append(iden)

        name_label = util.label("—", css=["mp-key-label"])
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.set_xalign(0.0)
        name_label.set_hexpand(True)
        head.append(name_label)
        body.append(head)

        chip_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        chip_labels: List[Gtk.Label] = []
        for trig, _ in config_module.TRIGGERS:
            chip = util.label("-", css=["mp-chip"])
            chip.set_ellipsize(Pango.EllipsizeMode.END)
            chip.set_xalign(0.0)
            chip_row.append(chip)
            chip_labels.append(chip)
        body.append(chip_row)

        button.set_child(body)
        button.connect("clicked", self._on_card_clicked, index)

        return {"widget": button, "name": name_label, "chips": chip_labels, "index": index}
    def _on_card_clicked(self, _button, index: int) -> None:
        state.select_button(index)

    def refresh_grid(self) -> None:
        for position, card in enumerate(self.cards):
            button_cfg = config_module.get_button(state.cfg, state.mode_index, position)
            card["name"].set_text(button_cfg.get("label", f"B{position + 1}"))
            for trigger, chip in zip(("single", "double", "hold"), card["chips"]):
                action = button_cfg.get(trigger) or {"type": "none"}
                summary = config_module.action_summary(action)
                prefix = {"single": "1x", "double": "2x", "hold": "H"}[trigger]
                chip.set_text(f"{prefix}: {summary}")
                if action.get("type", "none") == "none":
                    chip.set_css_classes(["mp-chip"])
                else:
                    chip.set_css_classes(["mp-chip", "mp-chip-armed"])

            widget: Gtk.Widget = card["widget"]
            active = position == state.selected_index
            classes = ["mp-key"] + (["mp-key-active"] if active else [])
            widget.set_css_classes(classes)

    # ------------------------------------------------------------------
    # Inspector
    # ------------------------------------------------------------------
    def rebuild_inspector(self) -> None:
        child = self.inspector.get_first_child()
        while child is not None:
            following = child.get_next_sibling()
            self.inspector.remove(child)
            child = following

        button_cfg = state.current_button()
        mode_name = state.cfg["modes"][state.mode_index].get("name", "")

        head = util.horizontal(spacing=8)
        badge = util.label(f"B{state.selected_index + 1}", css=["mp-pill", "mp-key-active"])
        head.append(badge)
        head.append(util.label(mode_name, css=["mp-hint"]))
        self.inspector.append(head)

        label_entry = Gtk.Entry()
        label_entry.set_text(button_cfg.get("label", ""))
        label_entry.set_placeholder_text("Nama tombol…")
        label_entry.set_hexpand(True)
        label_entry.connect("changed", self._on_label_changed)
        self.inspector.append(label_entry)

        self.editors: List[ActionEditor] = []
        for position, (trigger, trigger_label) in enumerate(config_module.TRIGGERS):
            if position > 0:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                separator.set_margin_top(6)
                separator.set_margin_bottom(6)
                self.inspector.append(separator)
            editor = ActionEditor(self.window, trigger, trigger_label)
            self.editors.append(editor)
            self.inspector.append(editor)

    def _on_label_changed(self, entry: Gtk.Entry) -> None:
        if state.current_button().get("label") == entry.get_text():
            return
        state.set_label(entry.get_text())

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------
    def _on_state_event(self, event: str, **data: Any) -> None:
        if event in ("mode-changed", "config-replaced"):
            self._sync_mode_switch()
            self.refresh_grid()
            self.rebuild_inspector()
            self.timing_label.set_text(self._timing_text())
        elif event == "selection-changed":
            self.refresh_grid()
            self.rebuild_inspector()
        elif event == "button-changed":
            self.refresh_grid()
        elif event == "timing-changed":
            self.timing_label.set_text(self._timing_text())
        elif event == "ha-entities-changed":
            self.rebuild_inspector()
        elif event == "hardware-event":
            self.flash(int(data.get("index", -1)))

    # ------------------------------------------------------------------
    def flash(self, index: int) -> None:
        """Animasi “tertekan” saat tombol fisik ditekan."""
        if not 0 <= index < len(self.cards):
            return
        widget = self.cards[index]["widget"]
        widget.add_css_class("mp-key-pressed")

        def release() -> bool:
            widget.remove_css_class("mp-key-pressed")
            return False

        GLib.timeout_add(180, release)
