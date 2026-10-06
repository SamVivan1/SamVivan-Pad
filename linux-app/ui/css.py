#!/usr/bin/env python3
"""
SamVivan MacroPad - Custom CSS (GTK4), tema studio gelap "SamVivan Studio".

Palet mengikuti web studio lama (style.css):
  bg #0b0f19, panel #111827, border #1f293d, card #172033,
  key-body #192237, key-top #222d45, key-shadow #0c1220,
  accent #3b82f6, sukses #10b981, warning #f59e0b, danger #ef4444.
"""

APP_CSS = """
/* ------------------------------------------------------------------ */
/* Latar aplikasi & header                                             */
/* ------------------------------------------------------------------ */
window {
  background-color: #0b0f19;
}

headerbar {
  background-color: #0d1320;
}

/* ------------------------------------------------------------------ */
/* Sidebar navigation                                                  */
/* ------------------------------------------------------------------ */
.navigation-sidebar {
  background-color: #0d1320;
}

.navigation-sidebar > row {
  border-radius: 10px;
  margin: 2px 8px;
}

.navigation-sidebar > row:hover {
  background-color: #1a2438;
}

.navigation-sidebar > row:selected {
  background-color: rgba(59, 130, 246, 0.18);
  color: #f3f4f6;
}

/* ------------------------------------------------------------------ */
/* Kartu tombol macropad — keycap 3D taktil ala web studio            */
/* ------------------------------------------------------------------ */
.mp-key {
  min-width: 154px;
  min-height: 118px;
  border-radius: 14px;
  border: 1px solid #2c3a5c;
  padding: 10px 12px;
  background-image: linear-gradient(180deg, #24304d 0%, #1b2540 48%, #131c2f 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.10),
    inset 0 -5px 10px rgba(0, 0, 0, 0.35),
    0 6px 0 #0a0f1c,
    0 12px 18px rgba(0, 0, 0, 0.45);
}

.mp-key:hover {
  background-image: linear-gradient(180deg, #2c3a5c 0%, #22304d 48%, #17223a 100%);
  border-color: #3b82f6;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.14),
    inset 0 -5px 10px rgba(0, 0, 0, 0.30),
    0 7px 0 #0a0f1c,
    0 16px 20px rgba(0, 0, 0, 0.50),
    0 0 18px rgba(59, 130, 246, 0.18);
}

.mp-key.mp-key-active {
  border-color: #3b82f6;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    inset 0 -5px 10px rgba(0, 0, 0, 0.30),
    0 6px 0 #0a0f1c,
    0 12px 18px rgba(0, 0, 0, 0.45),
    0 0 22px rgba(59, 130, 246, 0.40);
}

.mp-key:active,
.mp-key.mp-key-pressed {
  background-image: linear-gradient(180deg, #1a2336 0%, #151e30 100%);
  border-color: #10b981;
  box-shadow:
    inset 0 5px 12px rgba(0, 0, 0, 0.65),
    0 2px 0 #0a0f1c,
    0 4px 8px rgba(0, 0, 0, 0.55),
    0 0 16px rgba(16, 185, 129, 0.35);
}

.mp-key-index {
  font-size: 0.72rem;
  font-weight: 800;
  color: #64748b;
  font-family: "JetBrains Mono", monospace;
  letter-spacing: 1px;
}

.mp-key-pin {
  font-size: 0.66rem;
  color: #475569;
  font-family: "JetBrains Mono", monospace;
}

.mp-key-label {
  font-size: 0.96rem;
  font-weight: 700;
  color: #f3f4f6;
}

.mp-key-chips {
  margin-top: 6px;
}

/* ------------------------------------------------------------------ */
/* Chip aksi pada kartu tombol                                        */
/* ------------------------------------------------------------------ */
.mp-chip {
  font-size: 0.66rem;
  padding: 2px 9px;
  border-radius: 999px;
  background-color: rgba(148, 163, 184, 0.10);
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #cbd5e1;
}

.mp-chip-armed {
  background-color: rgba(59, 130, 246, 0.20);
  border-color: rgba(59, 130, 246, 0.45);
  color: #93c5fd;
}

/* ------------------------------------------------------------------ */
/* Chassis panel (area tombol) & panel umum                           */
/* ------------------------------------------------------------------ */
.mp-chassis {
  background-image: linear-gradient(180deg, #131c2d 0%, #0d1320 100%);
  border: 2px solid #23314c;
  border-radius: 20px;
  padding: 22px;
  box-shadow:
    inset 0 2px 4px rgba(255, 255, 255, 0.05),
    0 12px 32px rgba(0, 0, 0, 0.45);
}

.mp-panel {
  background-color: #111827;
  border: 1px solid #1f293d;
  border-radius: 16px;
}

.mp-panel.mp-inspector {
  padding: 14px;
}

.mp-page {
  margin: 12px;
}

/* ------------------------------------------------------------------ */
/* Pill status (header bar)                                           */
/* ------------------------------------------------------------------ */
.mp-pill {
  border-radius: 999px;
  padding: 3px 13px;
  font-size: 0.80rem;
  font-weight: 600;
  background-color: #0d1322;
  border: 1px solid #1f293d;
  color: #cbd5e1;
}

.mp-pill.mp-ok {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.45);
  background-color: rgba(16, 185, 129, 0.12);
}

.mp-pill.mp-warn {
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.45);
  background-color: rgba(245, 158, 11, 0.12);
}

.mp-pill.mp-err {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.45);
  background-color: rgba(239, 68, 68, 0.12);
}

/* ------------------------------------------------------------------ */
/* Mode switch (Desktop / Home Assistant)                             */
/* ------------------------------------------------------------------ */
.mp-mode-switch {
  background-color: #0d1322;
  border: 1px solid #1f293d;
  border-radius: 999px;
}

.mp-mode-switch > button {
  border-radius: 999px;
  padding: 6px 18px;
  background-color: transparent;
  color: #94a3b8;
}

.mp-mode-switch > button:checked {
  background-image: linear-gradient(180deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
}

/* ------------------------------------------------------------------ */
/* Teks bantu & judul                                                 */
/* ------------------------------------------------------------------ */
.mp-trigger-title {
  font-weight: 700;
  font-size: 0.92rem;
  color: #f8fafc;
}

.mp-section-title {
  font-weight: 800;
  font-size: 0.74rem;
  letter-spacing: 1px;
  color: #64748b;
  margin-top: 10px;
}

.mp-hint {
  font-size: 0.80rem;
  color: #94a3b8;
}

.mp-muted {
  color: #64748b;
}

/* ------------------------------------------------------------------ */
/* Console serial                                                      */
/* ------------------------------------------------------------------ */
textview.mp-console {
  background: #0d1322;
  color: #d1d5db;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.85rem;
  border-radius: 12px;
}

.mp-console {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.85rem;
}

/* ------------------------------------------------------------------ */
/* Kartu entity Home Assistant                                        */
/* ------------------------------------------------------------------ */
.mp-entity {
  min-width: 200px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid #1f293d;
  background-color: #172033;
}

.mp-entity:hover {
  background-color: #1e293b;
  border-color: #3b82f6;
}

.mp-entity-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: #f3f4f6;
}

.mp-entity-id {
  font-size: 0.72rem;
  color: #64748b;
  font-family: "JetBrains Mono", monospace;
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