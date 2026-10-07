#!/usr/bin/env python3
"""
SamVivan MacroPad - State runtime aplikasi (tanpa dependensi GTK).

Semua UI berlangganan perubahan lewat subscribe(); modul ini tidak mengimpor
gi/Gtk agar bisa dipakai dari mana pun (termasuk unit test).
"""

from typing import Any, Callable, Dict, List, Optional

import copy

import config as config_module

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
cfg: Dict[str, Any] = config_module.load_config()
mode_index: int = 0          # 0 = Desktop, 1 = Home Assistant
selected_index: int = 0      # tombol B1..B8 yang sedang diedit (0-7)
dirty: bool = False          # ada perubahan belum disimpan
active_preset: Optional[str] = cfg.get("activePreset")

installed_apps: List[Dict[str, str]] = []
system_presets: List[Dict[str, Any]] = []
ha_entities: List[Dict[str, Any]] = []
ha_entity_source: str = "empty"   # "live" | "cache" | "empty"
ha_connected: bool = False
ha_message: str = ""

serial_port: Optional[str] = None
serial_connected: bool = False

listener: Any = None         # SerialDaemonListener (diisi main.py)

_subscribers: List[Callable[..., None]] = []


# ---------------------------------------------------------------------------
# Bus sederhana
# ---------------------------------------------------------------------------
def subscribe(callback: Callable[..., None]) -> Callable[..., None]:
    _subscribers.append(callback)
    return callback


def emit(event: str, **data: Any) -> None:
    for callback in list(_subscribers):
        try:
            callback(event, **data)
        except Exception as exc:  # UI tidak boleh mematikan listener
            print(f"[STATE] subscriber {callback} gagal: {exc}")


# ---------------------------------------------------------------------------
# Mutator
# ---------------------------------------------------------------------------
def current_mode() -> Dict[str, Any]:
    return cfg["modes"][mode_index]


def current_button() -> Dict[str, Any]:
    return config_module.get_button(cfg, mode_index, selected_index)


def mark_dirty() -> None:
    global dirty
    dirty = True
    emit("dirty-changed", dirty=dirty)


def set_config(new_config: Dict[str, Any], source: str = "editor") -> None:
    """Ganti seluruh konfigurasi (import/preset/reset) lalu terapkan."""
    global cfg, dirty
    cfg = new_config
    dirty = True
    if listener is not None:
        try:
            listener.config = cfg
        except Exception as exc:
            print(f"[STATE] gagal menerapkan config ke listener: {exc}")
    emit("config-replaced", source=source)


def set_label(text: str) -> None:
    current_button()["label"] = text
    mark_dirty()
    emit("button-changed", index=selected_index)


def set_action(trigger: str, index: int, action: Dict[str, Any]) -> None:
    """Ganti satu aksi pada posisi `index` di slot trigger (diposisi lama bila kosong)."""
    actions = get_actions(trigger)
    if index < len(actions):
        actions[index] = action
    else:
        actions.append(action)
    current_button()[trigger] = actions
    mark_dirty()
    emit("button-changed", index=selected_index)


def add_action(trigger: str, action: Optional[Dict[str, Any]] = None) -> None:
    """Tambahkan aksi baru ke slot trigger (default: 'none', bisa diubah via editor)."""
    actions = get_actions(trigger)
    actions.append(action if isinstance(action, dict)
                   else config_module.default_action("none"))
    current_button()[trigger] = actions
    mark_dirty()
    emit("button-changed", index=selected_index)


def remove_action(trigger: str, index: int) -> None:
    """Hapus aksi dari slot trigger; pastikan selalu ada minimal satu slot."""
    actions = get_actions(trigger)
    if index < len(actions):
        del actions[index]
    if not actions:
        actions = [config_module.default_action("none")]
    current_button()[trigger] = actions
    mark_dirty()
    emit("button-changed", index=selected_index)


def get_actions(trigger: str) -> List[Dict[str, Any]]:
    """Daftar aksi pada slot trigger (dict lama dinormalisasi jadi list)."""
    return config_module.actions_list(current_button().get(trigger))


def set_timing(field: str, value: int) -> None:
    cfg[field] = value
    mark_dirty()
    emit("timing-changed", field=field, value=value)


def set_mode(index: int) -> None:
    global mode_index
    if index == mode_index:
        return
    mode_index = index
    cfg["activeModeIndex"] = index
    emit("mode-changed", mode_index=index)


def select_button(index: int) -> None:
    global selected_index
    if index == selected_index:
        return
    selected_index = index
    emit("selection-changed", index=index)


def save() -> bool:
    """Simpan ke disk dan aktifkan listener (jalur eksekusi aksi)."""
    global dirty
    ok = config_module.save_config(cfg)
    if ok:
        dirty = False
        if listener is not None:
            try:
                listener.config = cfg
            except Exception as exc:
                print(f"[STATE] gagal sinkron ke listener: {exc}")
        emit("config-saved", ok=True)
    else:
        emit("config-saved", ok=False)
    return ok


def save_preset(name: str, overwrite: bool = False) -> bool:
    """Simpan konfigurasi sebagai preset pengguna.

    overwrite=True memakai nama preset aktif (name diabaikan).
    Berkebalikan dengan save(), di sini juga terbentuk snapshot preset baru.
    """
    global dirty, active_preset
    if overwrite:
        if not active_preset:
            emit("config-saved", ok=False)
            return False
        preset_name = active_preset
    else:
        preset_name = config_module.preset_slug(name)
    snapshot = copy.deepcopy(cfg)
    snapshot.pop("activePreset", None)
    ok = config_module.save_preset(preset_name, snapshot)
    if ok:
        active_preset = preset_name
        cfg["activePreset"] = preset_name
        config_module.save_config(cfg)
        dirty = False
        if listener is not None:
            try:
                listener.config = cfg
            except Exception as exc:
                print(f"[STATE] gagal sinkron ke listener: {exc}")
        emit("config-saved", ok=True, preset=preset_name)
    else:
        emit("config-saved", ok=False)
    return ok


def apply_user_preset(name: str) -> bool:
    """Muat preset pengguna ke editor (menandai konfigurasi berubah)."""
    global active_preset
    data = config_module.load_preset(name)
    if data is None:
        return False
    data["activePreset"] = name
    set_config(data, source="preset")
    active_preset = name
    return True


def delete_user_preset(name: str) -> bool:
    """Hapus preset pengguna (bila aktif, lepaskan status aktif)."""
    global active_preset
    ok = config_module.delete_preset(name)
    if ok and active_preset == name:
        active_preset = None
        cfg.pop("activePreset", None)
        config_module.save_config(cfg)
    return ok


def set_apps(apps: List[Dict[str, str]]) -> None:
    global installed_apps
    installed_apps = apps
    emit("apps-changed", count=len(apps))


def set_ha_entities(entities: List[Dict[str, Any]], source: str) -> None:
    global ha_entities, ha_entity_source
    ha_entities = entities
    ha_entity_source = source
    emit("ha-entities-changed", count=len(entities), source=source)


def set_ha_status(connected: bool, message: str) -> None:
    global ha_connected, ha_message
    ha_connected = connected
    ha_message = message
    emit("ha-status-changed", connected=connected, message=message)


def set_serial_status(connected: bool, port: Optional[str]) -> None:
    global serial_connected, serial_port
    if connected == serial_connected and port == serial_port:
        return
    serial_connected = connected
    serial_port = port
    emit("serial-status-changed", connected=connected, port=port)
