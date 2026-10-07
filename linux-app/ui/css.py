#!/usr/bin/env python3
"""
SamVivan MacroPad - Custom CSS (GTK4), minimal native-like.
"""

APP_CSS = """
window {
  background-color: @view_bg_color;
}

.mp-page {
  margin: 12px 16px;
}

.mp-chassis {
  background-color: @card_bg_color;
  border: 1px solid @borders;
  border-radius: 12px;
  padding: 16px;
  box-shadow: none;
}

.mp-panel {
  background-color: @card_bg_color;
  border: 1px solid @borders;
  border-radius: 12px;
}

.mp-key {
  min-height: 92px;
  padding: 10px 12px;
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
  padding: 10px;
}

.mp-console {
  font-family: monospace;
  font-size: 0.86rem;
}
"""


def load_css(display) -> None:
    """Pasang provider CSS aplikasi pada display yang diberikan."""
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk

    provider = Gtk.CssProvider()
    provider.load_from_data(APP_CSS.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
