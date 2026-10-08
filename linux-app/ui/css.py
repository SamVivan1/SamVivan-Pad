#!/usr/bin/env python3
"""
SamVivan MacroPad - Custom CSS (GTK4), minimal native-like.
"""

APP_CSS = """
window {
  background-color: @view_bg_color;
}

.mp-page {
  margin: 14px 24px;
}

.mp-chassis {
  background-color: @card_bg_color;
  border: 1px solid @borders;
  border-radius: 12px;
  padding: 20px;
  box-shadow: none;
}

.mp-panel {
  background-color: @card_bg_color;
  border: 1px solid @borders;
  border-radius: 12px;
  padding: 10px;
}

.mp-key {
  min-height: 92px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid @borders;
  background-color: @view_bg_color;
}

.mp-key:hover {
  background-color: alpha(@view_fg_color, 0.06);
}

.mp-key.mp-key-active {
  border-color: @accent_color;
  background-color: alpha(@accent_color, 0.10);
}

.mp-key:active,
.mp-key.mp-key-pressed {
  background-color: alpha(@success_color, 0.14);
  border-color: @success_color;
}

.mp-key-index {
  font-size: 0.72rem;
  font-weight: 800;
  color: alpha(@view_fg_color, 0.9);
  padding: 1px 8px;
  border-radius: 999px;
  background-color: alpha(@view_fg_color, 0.10);
}

.mp-key-pin {
  font-size: 0.62rem;
  color: alpha(@view_fg_color, 0.38);
}

.mp-key-label {
  font-size: 0.94rem;
  font-weight: 600;
}

.mp-key-chips {
  margin-top: 0;
}

.mp-key-details {
  border-top: 1px solid alpha(@borders, 0.8);
  padding-top: 5px;
  margin-top: 2px;
}

.mp-key-detail-row {
  margin-top: 2px;
  padding: 3px 6px;
  border-radius: 7px;
  background-color: alpha(@view_fg_color, 0.04);
}

.mp-key-detail-row-armed {
  background-color: alpha(@accent_color, 0.10);
}

.mp-key-trigger {
  font-size: 0.66rem;
  font-weight: 800;
  color: alpha(@view_fg_color, 0.50);
  padding: 1px 6px;
  border-radius: 5px;
  background-color: alpha(@view_fg_color, 0.08);
}

.mp-key-detail-row-armed .mp-key-trigger {
  color: @accent_bg_color;
  background-color: alpha(@accent_color, 0.16);
}

.mp-key-summary {
  font-size: 0.72rem;
  color: alpha(@view_fg_color, 0.80);
}

.mp-key-summary-armed {
  color: alpha(@view_fg_color, 0.95);
}

.mp-chip {
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 999px;
  background-color: alpha(@view_fg_color, 0.06);
  color: alpha(@view_fg_color, 0.9);
}

.mp-chip-armed {
  background-color: alpha(@accent_color, 0.18);
}

.navigation-sidebar > row {
  border-radius: 8px;
  margin: 2px 6px;
}

.mp-mode-switch > button:checked {
  background-color: @accent_color;
  color: @accent_fg_color;
}

.mp-inspector {
  padding: 14px;
}

.mp-console {
  font-family: monospace;
  font-size: 0.86rem;
}

.mp-pill {
  border-radius: 999px;
  border: 1px solid alpha(@view_fg_color, 0.18);
  background-color: alpha(@view_fg_color, 0.06);
  color: alpha(@view_fg_color, 0.9);
  padding: 0 10px;
}

.mp-pill-dot {
  font-size: 0.7rem;
}

.mp-ok {
  border-color: alpha(@success_color, 0.55);
  background-color: alpha(@success_color, 0.14);
  color: @success_color;
}

.mp-ok .mp-pill-dot {
  color: @success_color;
}

.mp-warn {
  border-color: alpha(@warning_color, 0.55);
  background-color: alpha(@warning_color, 0.14);
  color: @warning_color;
}

.mp-warn .mp-pill-dot {
  color: @warning_color;
}

.mp-err {
  border-color: alpha(@error_color, 0.55);
  background-color: alpha(@error_color, 0.12);
  color: @error_color;
}

.mp-err .mp-pill-dot {
  color: @error_color;
}

.mp-ae-card {
  background-color: alpha(@view_fg_color, 0.03);
  border: 1px solid alpha(@view_fg_color, 0.09);
  border-radius: 10px;
  padding: 8px;
}

.mp-ae-num {
  font-size: 0.7rem;
  border-radius: 999px;
  border: 1px solid alpha(@accent_color, 0.5);
  background-color: alpha(@accent_color, 0.16);
  color: @accent_color;
  padding: 1px 8px;
}

.mp-move {
  min-width: 24px;
  min-height: 24px;
  padding: 2px;
}

/* Trigger colour coding: Single = blue, Double = green, Hold = orange. ---- */
.mp-trigger-title {
  font-weight: 700;
  font-size: 0.86rem;
}

.mp-trig-single { color: @accent_color; }
.mp-trig-double { color: @success_color; }
.mp-trig-hold { color: @warning_color; }

.mp-ae-num.mp-trig-single {
  border-color: alpha(@accent_color, 0.5);
  background-color: alpha(@accent_color, 0.16);
}
.mp-ae-num.mp-trig-double {
  border-color: alpha(@success_color, 0.5);
  background-color: alpha(@success_color, 0.16);
}
.mp-ae-num.mp-trig-hold {
  border-color: alpha(@warning_color, 0.5);
  background-color: alpha(@warning_color, 0.16);
}

.mp-trig-switch > button {
  font-weight: 600;
}
.mp-trig-switch > button.mp-trig-single:checked {
  background-color: alpha(@accent_color, 0.22);
}
.mp-trig-switch > button.mp-trig-double:checked {
  background-color: alpha(@success_color, 0.22);
}
.mp-trig-switch > button.mp-trig-hold:checked {
  background-color: alpha(@warning_color, 0.22);
}

.mp-key-trigger.mp-trig-single {
  color: @accent_color;
  background-color: alpha(@accent_color, 0.12);
}
.mp-key-trigger.mp-trig-double {
  color: @success_color;
  background-color: alpha(@success_color, 0.12);
}
.mp-key-trigger.mp-trig-hold {
  color: @warning_color;
  background-color: alpha(@warning_color, 0.12);
}

.mp-section-title {
  font-weight: 600;
  font-size: 0.78rem;
  color: alpha(@view_fg_color, 0.75);
  margin-top: 4px;
}

.mp-entity {
  background-color: @card_bg_color;
  border: 1px solid @borders;
  border-radius: 10px;
  padding: 10px 12px;
}
"""


def load_css(display) -> None:
    """Attach the application CSS provider to the given display."""
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk

    provider = Gtk.CssProvider()
    provider.load_from_data(APP_CSS.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
