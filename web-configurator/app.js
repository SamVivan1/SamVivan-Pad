/**
 * SamVivan MacroPad Studio - Web Configurator & Hardware Manager
 * Compatible with ESP32-C3 SuperMini running SamVivan MacroPad Firmware
 * Native Ubuntu Linux & Home Assistant REST API Integration
 */

// Hardware Button Pinout matching macropadv2.5.ino
const PINOUT = [20, 9, 2, 1, 21, 10, 3, 0];

// Predefined available keys
const AVAILABLE_KEYS = [
  { group: 'Standard Alpha', keys: ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'] },
  { group: 'Numbers', keys: ['0','1','2','3','4','5','6','7','8','9'] },
  { group: 'Function Keys (F1-F12)', keys: ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'] },
  { group: 'Extra Macro Keys (F13-F24)', keys: ['F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24'] },
  { group: 'Controls & Navigation', keys: ['ENTER','ESC','BACKSPACE','TAB','SPACE','UP','DOWN','LEFT','RIGHT','HOME','END','PAGE_UP','PAGE_DOWN','DELETE'] }
];

const MEDIA_ACTIONS = [
  { value: 'MUTE', label: 'Mute / Unmute' },
  { value: 'VOL_UP', label: 'Volume Up (+)' },
  { value: 'VOL_DOWN', label: 'Volume Down (-)' },
  { value: 'PLAY_PAUSE', label: 'Play / Pause' },
  { value: 'NEXT_TRACK', label: 'Next Track' },
  { value: 'PREV_TRACK', label: 'Previous Track' }
];

// ============================================================================
// Icon System (Lucide — set ikon yang sama dipakai shadcn/ui)
// Sprite tersimpan sebagai <symbol id="i-..."> di index.html.
// ============================================================================
const ACTION_ICONS = {
  home_assistant: "house",
  launch_app: "rocket",
  system_action: "cpu",
  bash_script: "terminal",
  ha_webhook: "link",
  text: "type",
  media: "music",
  shortcut: "keyboard",
  mode_toggle: "layers",
  none: "x",
};

// Fallback ikon per domain HA (dipakai bila entity tidak membawa icon sendiri)
const DOMAIN_ICONS = {
  light: "lightbulb", switch: "toggle-right", group: "package",
  input_boolean: "toggle-left", fan: "fan", cover: "chevrons-up-down",
  climate: "thermometer", humidifier: "droplets", water_heater: "droplet",
  lock: "lock", vacuum: "bot", media_player: "music", remote: "radio",
  scene: "clapperboard", script: "scroll-text", automation: "settings",
  button: "circle-dot", input_button: "circle-dot", timer: "timer",
  number: "hash", input_number: "hash", select: "list", input_select: "list",
  text: "type", siren: "siren", alarm_control_panel: "shield",
  update: "package", tts: "volume-2",
};

function icon(name, cls = "") {
  const id = /^[a-z0-9-]+$/.test(name || "") ? name : "package";
  return `<svg class="icon ${cls}" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${id}"></use></svg>`;
}

function entityIconName(ent) {
  const raw = ent && ent.icon;
  if (typeof raw === "string" && /^[a-z0-9-]+$/.test(raw)) return raw;
  return (ent && DOMAIN_ICONS[ent.domain]) || "package";
}

function actionIcon(action) {
  return ACTION_ICONS[(action && action.type)] || "package";
}

// Isi elemen statis bertanda data-i="nama-ikon" dengan SVG dari sprite.
function hydrateIcons(root = document) {
  if (!root || !root.querySelectorAll) return;
  root.querySelectorAll("[data-i]").forEach(el => {
    if (el.dataset.iDone) return;
    el.innerHTML = icon(el.dataset.i);
    el.dataset.iDone = "1";
  });
}

// Default configuration — sepenuhnya dinamis:
// Tidak ada IP / entity Home Assistant yang di-hardcode. User mengatur
// koneksi lewat modal HA lalu memilih entity lewat Entity Picker.
const DEFAULT_CONFIG = {
  version: 2.5,
  device: "SamVivan MacroPad",
  debounceMs: 25,
  clickTimeoutMs: 250,
  holdTimeoutMs: 450,
  activeModeIndex: 0,
  modes: [
    {
      id: "desktop",
      name: "Desktop Mode",
      ledState: true,
      buttons: [
        {
          index: 0,
          pin: 20,
          label: "Mode / Passcode",
          single: { type: "mode_toggle" },
          double: { type: "none" },
          hold: { type: "text", text: "031004" }
        },
        {
          index: 1,
          pin: 9,
          label: "Terminal",
          single: { type: "system_action", presetId: "open_terminal" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 2,
          pin: 2,
          label: "Screenshot",
          single: { type: "system_action", presetId: "screenshot_interactive" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 3,
          pin: 1,
          label: "Mute Mic",
          single: { type: "system_action", presetId: "mic_toggle_mute" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 4,
          pin: 21,
          label: "Vol Up",
          single: { type: "system_action", presetId: "volume_up_5" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 5,
          pin: 10,
          label: "Vol Down",
          single: { type: "system_action", presetId: "volume_down_5" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 6,
          pin: 3,
          label: "Lock Screen",
          single: { type: "system_action", presetId: "lock_screen" },
          double: { type: "none" },
          hold: { type: "none" }
        },
        {
          index: 7,
          pin: 0,
          label: "Macro 7",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "8" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "U" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "J" }
        }
      ]
    },
    {
      id: "ha",
      name: "Home Assistant Mode",
      ledState: false,
      buttons: [
        {
          index: 0,
          pin: 20,
          label: "Mode / Passcode",
          single: { type: "mode_toggle" },
          double: { type: "none" },
          hold: { type: "text", text: "031004" }
        },
        // Tombol HA 1-7 sengaja tanpa entity: user memilihnya sendiri lewat
        // "Pilih Entity" setelah mengatur koneksi Home Assistant.
        ...[9, 2, 1, 21, 10, 3, 0].map((pin, i) => ({
          index: i + 1,
          pin,
          label: `HA Key ${i + 1}`,
          single: { type: "home_assistant", domain: "", service: "", entityId: "", friendlyName: "" },
          double: { type: "none" },
          hold: { type: "none" }
        }))
      ]
    }
  ]
};

// Application State
let appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
let selectedButtonIndex = 0;
let currentModeIndex = 0;

// Host & HA State
let daemonAvailable = false;
let installedApps = [];
let systemPresets = [];
let haEntities = [];          // diisi dari scan / cache — bukan data hardcode
let haConfigured = false;
let pendingAppPickerTarget = null;

// Entity Picker (Pilih HA -> Pilih Entity)
let pendingEntityTarget = null;   // trigger ("single"|"double"|"hold") yang sedang diedit
let openPickerAfterSave = false;  // buka picker setelah koneksi HA disimpan
let entityFilterDomain = "all";
let haEntitySource = "empty";     // "live" | "cache" | "empty"
let haRequestPending = false;     // kunci anti-double-click saat request berjalan

// Web Serial Connection State
let serialPort = null;
let serialReader = null;
let serialWriter = null;
let isConnected = false;
let serialBuffer = "";

// ============================================================================
// Initialization & DOM Binding
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
  hydrateIcons();
  initDOM();
  renderKeysGrid();
  loadButtonIntoInspector(selectedButtonIndex);
  setupWebSerialSupport();
  checkUbuntuDaemon();
  checkHomeAssistant();
});

function initDOM() {
  document.getElementById("tabDesktopMode").addEventListener("click", () => switchMode(0));
  document.getElementById("tabHaMode").addEventListener("click", () => switchMode(1));

  document.getElementById("btnConnect").addEventListener("click", handleToggleConnection);

  const consoleDrawer = document.getElementById("consoleDrawer");
  document.getElementById("btnToggleConsole").addEventListener("click", () => {
    consoleDrawer.style.display = (consoleDrawer.style.display === "none") ? "flex" : "none";
  });
  document.getElementById("btnCloseConsole").addEventListener("click", () => {
    consoleDrawer.style.display = "none";
  });
  document.getElementById("btnClearConsole").addEventListener("click", () => {
    document.getElementById("consoleOutput").innerHTML = "";
  });

  document.getElementById("btnSendSerial").addEventListener("click", handleSendCustomSerial);
  document.getElementById("customSerialInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSendCustomSerial();
  });

  const btnProfileMenu = document.getElementById("btnProfileMenu");
  const profileDropdown = document.getElementById("profileDropdown");
  btnProfileMenu.addEventListener("click", (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle("show");
  });
  window.addEventListener("click", () => profileDropdown.classList.remove("show"));

  document.getElementById("btnExportJson").addEventListener("click", exportProfileJson);
  document.getElementById("fileImportJson").addEventListener("change", importProfileJson);

  document.querySelectorAll(".preset-option").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const presetKey = e.currentTarget.dataset.preset;
      applyPreset(presetKey);
    });
  });

  document.getElementById("btnWriteConfig").addEventListener("click", handleSaveAllConfigs);
  document.getElementById("btnReadConfig").addEventListener("click", readConfigFromDevice);

  document.getElementById("inputButtonLabel").addEventListener("input", (e) => {
    const btn = getCurrentButtonConfig();
    btn.label = e.target.value;
    updateKeyVisual(selectedButtonIndex);
  });

  ['single', 'double', 'hold'].forEach(trigger => {
    document.getElementById(`${trigger}ActionType`).addEventListener("change", (e) => {
      const btn = getCurrentButtonConfig();
      const newType = e.target.value;
      btn[trigger] = createDefaultAction(newType);
      renderTriggerSettings(trigger, btn[trigger]);
      updateKeyVisual(selectedButtonIndex);
    });
  });

  ['Debounce', 'ClickTimeout', 'HoldTimeout'].forEach(key => {
    const input = document.getElementById(`input${key}`);
    input.addEventListener("change", () => {
      const field = key === 'Debounce' ? 'debounceMs' : (key === 'ClickTimeout' ? 'clickTimeoutMs' : 'holdTimeoutMs');
      appConfig[field] = parseInt(input.value, 10);
      showToast(`Updated ${field} to ${input.value}ms`, 'info');
    });
  });

  const appModal = document.getElementById("appPickerDialog");
  document.getElementById("btnCloseAppModal").addEventListener("click", () => appModal.close());
  document.getElementById("inputAppSearch").addEventListener("input", (e) => {
    renderFilteredApps(e.target.value);
  });

  // Home Assistant native connection modal
  const haModal = document.getElementById("haConfigDialog");
  document.getElementById("haPill").addEventListener("click", () => openHaConfigDialog());
  document.getElementById("btnCloseHaModal").addEventListener("click", () => haModal.close());
  document.getElementById("btnHaTest").addEventListener("click", testHaConnection);
  document.getElementById("btnHaSave").addEventListener("click", saveHaConnection);
  document.getElementById("btnHaRefreshEntities").addEventListener("click", () => refreshHaEntities());
  document.getElementById("btnToggleHaToken").addEventListener("click", () => {
    const input = document.getElementById("inputHaToken");
    const showing = input.type === "text";
    input.type = showing ? "password" : "text";
    const holder = document.getElementById("btnToggleHaTokenIco");
    if (holder) {
      holder.innerHTML = icon(showing ? "eye" : "eye-off");
      holder.dataset.iDone = "1";
    }
  });

  // Entity picker modal (Pilih HA -> Pilih Entity)
  const entityModal = document.getElementById("entityPickerDialog");
  document.getElementById("btnCloseEntityModal").addEventListener("click", () => entityModal.close());
  document.getElementById("inputEntitySearch").addEventListener("input", renderEntityGrid);
  document.getElementById("btnRescanEntities").addEventListener("click", () => rescanEntities());
  document.getElementById("entityDomainChips").addEventListener("click", (e) => {
    const chip = e.target.closest("[data-domain]");
    if (!chip) return;
    entityFilterDomain = chip.dataset.domain;
    renderEntityChips();
    renderEntityGrid();
  });
}

// ============================================================================
// Ubuntu & Home Assistant Backend Checks
// ============================================================================
async function checkUbuntuDaemon() {
  const hostDot = document.getElementById("hostDot");
  const hostText = document.getElementById("hostText");
  const hostPill = document.getElementById("hostPill");

  try {
    const res = await fetchWithTimeout('/api/status', {}, 2500);
    if (!res.ok) throw new Error("Status check failed");
    const data = await res.json();

    daemonAvailable = true;
    hostPill.classList.add("online");
    hostText.textContent = `Ubuntu: Active (${data.appsCount} Apps)`;
    logSerial(`[DAEMON] Terhubung ke Ubuntu Companion Service v${data.version}.`, "system");

    loadDaemonApps();
    loadDaemonPresets();
    loadDaemonConfig();

  } catch (e) {
    daemonAvailable = false;
    hostPill.classList.remove("online");
    hostText.textContent = "Ubuntu: Standalone";
  }
}

// Fetch dengan timeout manual: AbortSignal.timeout tidak selalu tersedia di
// WebKit2GTK dan bisa membuat request menggantung -> UI terasa freeze.
function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(timer));
}

// Kunci tombol aksi HA selama request berjalan supaya tidak menumpuk.
function setHaButtonsBusy(busy) {
  ["btnHaTest", "btnHaRefreshEntities", "btnHaSave"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.disabled = busy;
  });
}

function applyHaStatusToPill(data) {
  const haDot = document.getElementById("haDot");
  const haText = document.getElementById("haText");
  const haPill = document.getElementById("haPill");
  haConfigured = !!data.configured;
  if (data.connected) {
    haPill.className = "connection-pill ha-pill online";
    haDot.className = "status-indicator connected";
    haText.textContent = "HA: Connected";
  } else {
    haPill.className = "connection-pill ha-pill";
    haDot.className = "status-indicator";
    haText.textContent = haConfigured ? "HA: Offline (LAN)" : "HA: Not Configured";
  }
}

async function checkHomeAssistant(ping = true) {
  try {
    // Default tanpa ping: respons server instan dari cache (tanpa jaringan).
    const res = await fetchWithTimeout(`/api/ha/status${ping ? "?ping=1" : ""}`, {}, ping ? 6000 : 3000);
    if (res.ok) {
      const data = await res.json();
      applyHaStatusToPill(data);
      if (data.connected) logSerial(`[HA] Terhubung ke Home Assistant: ${data.url}`, "system");
    }
    // Ambil entity dari cache server (instan) — scan live hanya saat diminta.
    fetchHaEntities();
  } catch (err) {
    document.getElementById("haPill").className = "connection-pill ha-pill";
    document.getElementById("haText").textContent = haConfigured ? "HA: Offline (LAN)" : "HA: Not Configured";
  }
}

function normalizeHaEntities(list) {
  return (list || []).map(ent => {
    const domain = ent.domain || (ent.entity_id || "").split(".")[0];
    const normalized = {
      ...ent,
      domain,
      state: ent.state ?? null,
      services: Array.isArray(ent.services) && ent.services.length
        ? ent.services
        : ["toggle", "turn_on", "turn_off"],
      default_service: ent.default_service || "toggle",
    };
    normalized.icon = entityIconName(normalized);
    return normalized;
  });
}

async function fetchHaEntities(force = false) {
  try {
    const res = await fetchWithTimeout(`/api/ha/entities${force ? '?refresh=1' : ''}`, {}, force ? 12000 : 4000);
    if (res.ok) {
      const data = await res.json();
      if (data.entities && data.entities.length > 0) {
        haEntities = normalizeHaEntities(data.entities);
        haEntitySource = data.live ? "live" : "cache";
        haConfigured = haConfigured || !!data.configured;
        logSerial(`[HA] ${haEntities.length} entity interaktif${data.url ? " di " + data.url : ""}.`, "system");
        return haEntities.length;
      }
      // Server menjawab tapi tidak ada entity: kosongkan (bukan data hardcode).
      haEntities = [];
      haEntitySource = "empty";
    }
  } catch (e) {}
  return haEntities.length;
}

// ============================================================================
// Home Assistant Connection Setup (Native / Scriptless)
// ============================================================================
function setHaStatus(kind, message) {
  const dot = document.getElementById("haStatusDot");
  const text = document.getElementById("haStatusText");
  dot.className = "status-indicator";
  if (kind === "ok") dot.classList.add("connected");
  if (kind === "busy") dot.classList.add("connecting");
  text.textContent = message;
  text.className = `ha-status-text ha-status-${kind}`;
}

async function openHaConfigDialog(options = {}) {
  const modal = document.getElementById("haConfigDialog");
  openPickerAfterSave = !!options.openPickerAfterSave;
  const tokenInput = document.getElementById("inputHaToken");
  tokenInput.value = "";
  tokenInput.type = "password";

  // Buka dialog SEGERA tanpa menunggu jaringan -> UI tidak pernah terasa freeze.
  setHaStatus("busy", "Membaca konfigurasi tersimpan...");
  if (!modal.open) modal.showModal();

  let configured = false;
  try {
    // Respons server instan (tanpa ping) — hanya untuk mengisi field.
    const res = await fetchWithTimeout('/api/ha/status', {}, 3000);
    const data = await res.json();
    configured = !!data.configured;
    document.getElementById("inputHaUrl").value = data.url || "";
    tokenInput.placeholder = configured
      ? "Token tersimpan (kosongkan untuk mempertahankan)"
      : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
    setHaStatus(data.connected ? "ok" : (configured ? "warn" : "info"),
      data.message || "Belum dikonfigurasi");
  } catch (err) {
    setHaStatus("warn", "Server lokal tidak aktif — buka aplikasi SamVivan MacroPad dulu.");
    return;
  }

  // Cek live di background (maks ~3 dtk) tanpa memblokir dialog yang sudah terbuka.
  if (!configured || !modal.open) return;
  setHaStatus("busy", "Memeriksa koneksi ke Home Assistant...");
  try {
    const res = await fetchWithTimeout('/api/ha/status?ping=1', {}, 6000);
    const data = await res.json();
    if (modal.open) {
      applyHaStatusToPill(data);
      setHaStatus(data.connected ? "ok" : "warn", data.message);
    }
  } catch (e) {}
}

async function testHaConnection() {
  if (haRequestPending) return;
  const url = document.getElementById("inputHaUrl").value.trim();
  const token = document.getElementById("inputHaToken").value.trim();
  if (!url) {
    setHaStatus("warn", "Isi Home Assistant URL dulu.");
    return;
  }
  haRequestPending = true;
  setHaButtonsBusy(true);
  setHaStatus("busy", "Menguji koneksi ke Home Assistant (maks 3 detik)...");
  try {
    const res = await fetchWithTimeout('/api/ha/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, token })
    }, 8000);
    const data = await res.json();
    if (data.success) {
      const count = await fetchHaEntities(true);
      setHaStatus("ok", `${data.message} — ${count} entity interaktif siap dipilih.`);
      showToast(`Terhubung. ${count} entity interaktif ditemukan.`, 'success');
      updateEntityModalSubtitle();
      renderEntityChips();
      renderEntityGrid();
    } else {
      setHaStatus("err", data.message);
      showToast(data.message, 'error');
    }
  } catch (err) {
    setHaStatus("err", `Gagal menghubungi server lokal: ${err.message}`);
  } finally {
    haRequestPending = false;
    setHaButtonsBusy(false);
  }
}

async function saveHaConnection() {
  if (haRequestPending) return;
  const url = document.getElementById("inputHaUrl").value.trim();
  const token = document.getElementById("inputHaToken").value.trim();
  if (!url) {
    setHaStatus("warn", "Isi Home Assistant URL dulu.");
    return;
  }
  haRequestPending = true;
  setHaButtonsBusy(true);
  setHaStatus("busy", "Menyimpan koneksi & memindai entity...");
  try {
    const res = await fetchWithTimeout('/api/ha/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, token })
    }, 8000);
    const data = await res.json();
    if (!data.success) {
      setHaStatus("err", data.message || "Gagal menyimpan konfigurasi");
      return;
    }
    haConfigured = true;
    // Cukup SATU scan di sini — tanpa ping tambahan supaya UI cepat kembali aktif.
    const count = await fetchHaEntities(true);
    setHaStatus("ok", `Tersimpan — ${count} entity interaktif ditemukan.`);
    showToast(`Koneksi HA tersimpan. ${count} entity interaktif siap dipilih.`, 'success');
    document.getElementById("haConfigDialog").close();
    checkHomeAssistant(false);  // perbarui pill dari cache server (instan)

    if (openPickerAfterSave) {
      openPickerAfterSave = false;
      openEntityPicker(pendingEntityTarget);
    } else if (count > 0) {
      showToast("Klik pill HA / tombol Pilih Entity untuk memilih entity.", 'info');
    }
  } catch (err) {
    setHaStatus("err", `Gagal menyimpan: ${err.message}`);
  } finally {
    haRequestPending = false;
    setHaButtonsBusy(false);
  }
}

async function refreshHaEntities(showFeedback = true) {
  if (haRequestPending) return;
  haRequestPending = true;
  setHaButtonsBusy(true);
  if (showFeedback) setHaStatus("busy", "Memuat ulang daftar entities...");
  const count = await fetchHaEntities(true);
  if (showFeedback) {
    setHaStatus("ok", `${count} entity interaktif tersedia.`);
    showToast(`Memuat ulang ${count} entity interaktif.`, 'success');
  }
  updateEntityModalSubtitle();
  renderEntityChips();
  renderEntityGrid();
  if (typeof selectedButtonIndex === "number") loadButtonIntoInspector(selectedButtonIndex);
  haRequestPending = false;
  setHaButtonsBusy(false);
}

// ============================================================================
// Home Assistant Entity Picker (Pilih HA -> Pilih Entity)
// ============================================================================
function openEntityPicker(trigger = null) {
  pendingEntityTarget = trigger ?? pendingEntityTarget;
  entityFilterDomain = "all";
  document.getElementById("inputEntitySearch").value = "";
  updateEntityModalSubtitle();
  renderEntityChips();
  renderEntityGrid();

  const modal = document.getElementById("entityPickerDialog");
  if (!modal.open) modal.showModal();

  if (haConfigured) rescanEntities(false);
  else renderEntityGrid();  // empty-state akan menawarkan tombol koneksi
}

async function rescanEntities(showFeedback = true) {
  const subtitle = document.getElementById("entityModalSubtitle");
  const prev = subtitle.textContent;
  subtitle.innerHTML = `${icon("refresh-cw", "icon-spin")} Memindai entity ke Home Assistant...`;
  const count = await fetchHaEntities(true);
  if (count === 0) subtitle.textContent = prev;
  updateEntityModalSubtitle();
  renderEntityChips();
  renderEntityGrid();
  if (showFeedback) showToast(`Scan selesai: ${count} entity interaktif.`, 'success');
}

function updateEntityModalSubtitle() {
  const subtitle = document.getElementById("entityModalSubtitle");
  if (!haConfigured) {
    subtitle.textContent = "Belum tersambung — atur koneksi Home Assistant dulu.";
    return;
  }
  const source = haEntitySource === "live" ? "data langsung dari Home Assistant" : "cache lokal (HA offline)";
  subtitle.textContent = `${haEntities.length} entity interaktif • ${source}`;
}

function renderEntityChips() {
  const wrap = document.getElementById("entityDomainChips");
  if (!wrap) return;

  const counts = {};
  haEntities.forEach(ent => { counts[ent.domain] = (counts[ent.domain] || 0) + 1; });
  const domains = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
  if (entityFilterDomain !== "all" && !domains.includes(entityFilterDomain)) entityFilterDomain = "all";

  const chips = [`<button class="entity-chip ${entityFilterDomain === "all" ? "active" : ""}" data-domain="all">Semua (${haEntities.length})</button>`];
  domains.forEach(d => {
    const ent = haEntities.find(e => e.domain === d);
    chips.push(`<button class="entity-chip ${entityFilterDomain === d ? "active" : ""}" data-domain="${d}">${icon(entityIconName(ent))} ${d} (${counts[d]})</button>`);
  });
  wrap.innerHTML = chips.join("");
}

function haStateClass(state) {
  const s = String(state || "").toLowerCase();
  if (["on", "active", "open", "unlocked", "home", "playing", "paused"].includes(s)) return "state-on";
  if (["off", "closed", "locked", "idle", "standby"].includes(s)) return "state-off";
  if (["unavailable", "unknown"].includes(s)) return "state-na";
  return "";
}

function renderEntityGrid() {
  const grid = document.getElementById("entityGrid");
  if (!grid) return;

  if (!haConfigured) {
    grid.innerHTML = `
      <div class="entity-empty">
        <p class="entity-empty-icon">${icon("house", "icon-lg")}</p>
        <p>Home Assistant belum dikonfigurasi.</p>
        <p>Masukkan URL & token Home Assistant, lalu sistem akan memindai semua entity yang bisa dikontrol.</p>
        <button type="button" class="btn btn-primary" id="btnEntityEmptyConnect">${icon("settings")} Atur Koneksi Home Assistant</button>
      </div>`;
    grid.querySelector("#btnEntityEmptyConnect").addEventListener("click", () => {
      document.getElementById("entityPickerDialog").close();
      openHaConfigDialog({ openPickerAfterSave: true });
    });
    return;
  }

  const query = (document.getElementById("inputEntitySearch").value || "").toLowerCase().trim();
  const filtered = haEntities.filter(ent => {
    if (entityFilterDomain !== "all" && ent.domain !== entityFilterDomain) return false;
    if (!query) return true;
    return (ent.friendly_name || "").toLowerCase().includes(query)
      || ent.entity_id.toLowerCase().includes(query)
      || ent.domain.toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    grid.innerHTML = `<div class="entity-empty"><p>Tidak ada entity yang cocok dengan pencarian/filter ini.</p></div>`;
    return;
  }

  grid.innerHTML = filtered.map(ent => `
    <button type="button" class="entity-card" data-entity-id="${escapeHtml(ent.entity_id)}">
      <span class="entity-icon">${icon(entityIconName(ent), "icon-md")}</span>
      <span class="entity-body">
        <span class="entity-name">${escapeHtml(ent.friendly_name || ent.entity_id)}</span>
        <span class="entity-id">${escapeHtml(ent.entity_id)}</span>
      </span>
      <span class="entity-state ${haStateClass(ent.state)}">${escapeHtml(ent.state ?? "-")}</span>
    </button>
  `).join("");

  grid.querySelectorAll(".entity-card").forEach(card => {
    card.addEventListener("click", () => selectHaEntity(card.dataset.entityId));
  });
}

function selectHaEntity(entityId) {
  const trigger = pendingEntityTarget;
  const ent = haEntities.find(x => x.entity_id === entityId);
  if (!ent) return;

  document.getElementById("entityPickerDialog").close();
  if (!trigger) return;

  const btn = getCurrentButtonConfig();
  const action = btn[trigger];
  if (!action || action.type !== 'home_assistant') return;

  action.entityId = ent.entity_id;
  action.domain = ent.domain;
  action.friendlyName = ent.friendly_name || ent.entity_id;
  action.services = ent.services;
  action.service = ent.default_service || (ent.services && ent.services[0]) || 'toggle';
  action.icon = ent.icon;

  // Update label tombol jika masih label bawaan
  if (!btn.label || btn.label.startsWith("Button ") || btn.label.startsWith("Macro ") || btn.label.startsWith("HA Key ")) {
    btn.label = (action.friendlyName || ent.entity_id).slice(0, 14);
    document.getElementById("inputButtonLabel").value = btn.label;
  }

  renderTriggerSettings(trigger, action);
  updateKeyVisual(selectedButtonIndex);
  logSerial(`[HA] Entity dipilih: ${ent.entity_id} (${ent.domain}.${action.service})`, "system");
  showToast(`${ent.friendly_name || ent.entity_id} → ${ent.domain}.${action.service}`, 'success');
}

async function loadDaemonApps() {
  try {
    const res = await fetch('/api/apps');
    const data = await res.json();
    installedApps = data.apps || [];
    document.getElementById("modalAppsCount").textContent = `${installedApps.length} aplikasi terpasang di sistem Ubuntu Anda.`;
  } catch (err) {}
}

async function loadDaemonPresets() {
  try {
    const res = await fetch('/api/system-actions');
    const data = await res.json();
    systemPresets = data.actions || [];
  } catch (err) {}
}

async function loadDaemonConfig() {
  try {
    const res = await fetch('/api/config');
    if (res.ok) {
      const serverConfig = await res.json();
      if (serverConfig.modes && serverConfig.modes.length > 0) {
        appConfig = serverConfig;
        renderKeysGrid();
        loadButtonIntoInspector(selectedButtonIndex);
      }
    }
  } catch (e) {}
}

// ============================================================================
// Grid & Visualizer Rendering
// ============================================================================
function renderKeysGrid() {
  const grid = document.getElementById("keysGrid");
  grid.innerHTML = "";

  const currentMode = appConfig.modes[currentModeIndex];

  for (let i = 0; i < 8; i++) {
    const btnConfig = currentMode.buttons[i];
    const pin = PINOUT[i];

    const keyDiv = document.createElement("div");
    keyDiv.className = `key-switch ${i === 0 ? 'is-mode-button' : ''} ${i === selectedButtonIndex ? 'selected' : ''}`;
    keyDiv.id = `keySwitch_${i}`;
    keyDiv.dataset.index = i;

    keyDiv.innerHTML = `
      <div class="key-cap">
        <div class="key-header-tag">
          <span class="key-index">B${i + 1}</span>
          <span class="key-pin">GPIO ${pin}</span>
        </div>
        <div class="key-center-label" id="keyLabel_${i}">${escapeHtml(btnConfig.label || `Button ${i + 1}`)}</div>
        <div class="key-action-preview" id="keyPreview_${i}">
          ${renderActionPreview(btnConfig)}
        </div>
      </div>
    `;

    keyDiv.addEventListener("click", () => {
      selectButton(i);
    });

    grid.appendChild(keyDiv);
  }

  updateBoardLed();
}

function renderActionPreview(btn) {
  const getLabel = (action) => {
    if (!action || action.type === 'none') return 'None';
    if (action.type === 'mode_toggle') return 'Toggle Mode';
    if (action.type === 'home_assistant') return action.friendlyName || action.entityId || 'Belum pilih entity';
    if (action.type === 'launch_app') return action.appName || action.desktopId || 'App';
    if (action.type === 'system_action') return action.presetName || action.presetId || 'Action';
    if (action.type === 'bash_script') return 'Bash Script';
    if (action.type === 'ha_webhook') return 'HA Webhook';
    if (action.type === 'text') return `"${action.text.slice(0, 6)}${action.text.length > 6 ? '..' : ''}"`;
    if (action.type === 'media') return `Media: ${action.mediaKey}`;
    if (action.type === 'shortcut') {
      const mods = (action.modifiers || []).map(m => m[0].toUpperCase()).join('+');
      return mods ? `${mods}+${action.key}` : action.key;
    }
    return action.type;
  };

  const chip = (trigger, label) => {
    const action = btn[trigger];
    const text = `${label}: ${getLabel(action)}`;
    return `<span class="action-chip chip-${trigger}" title="${escapeHtml(text)}">${icon(actionIcon(action), "icon-xs")}<span class="action-chip-text">${escapeHtml(text)}</span></span>`;
  };

  return `
    ${chip("single", "1x")}
    ${chip("double", "2x")}
    ${chip("hold", "H")}
  `;
}

function updateKeyVisual(index) {
  const btnConfig = appConfig.modes[currentModeIndex].buttons[index];
  const labelEl = document.getElementById(`keyLabel_${index}`);
  const previewEl = document.getElementById(`keyPreview_${index}`);
  if (labelEl) labelEl.textContent = btnConfig.label || `Button ${index + 1}`;
  if (previewEl) previewEl.innerHTML = renderActionPreview(btnConfig);
}

function selectButton(index) {
  selectedButtonIndex = index;
  document.querySelectorAll(".key-switch").forEach(el => el.classList.remove("selected"));
  const target = document.getElementById(`keySwitch_${index}`);
  if (target) target.classList.add("selected");
  loadButtonIntoInspector(index);
}

function switchMode(modeIndex) {
  currentModeIndex = modeIndex;
  document.getElementById("tabDesktopMode").classList.toggle("active", modeIndex === 0);
  document.getElementById("tabHaMode").classList.toggle("active", modeIndex === 1);
  renderKeysGrid();
  loadButtonIntoInspector(selectedButtonIndex);
  updateBoardLed();
}

function updateBoardLed() {
  const isDesktop = currentModeIndex === 0;
  const bulb = document.getElementById("boardLedBulb");
  const label = document.getElementById("boardLedLabel");
  if (isDesktop) {
    bulb.classList.remove("off");
    label.textContent = "LED (GPIO 4): ON [Desktop]";
  } else {
    bulb.classList.add("off");
    label.textContent = "LED (GPIO 4): OFF [Home Assistant]";
  }
}

// ============================================================================
// Inspector & Settings Form
// ============================================================================
function getCurrentButtonConfig() {
  return appConfig.modes[currentModeIndex].buttons[selectedButtonIndex];
}

function loadButtonIntoInspector(index) {
  const btn = appConfig.modes[currentModeIndex].buttons[index];
  const pin = PINOUT[index];

  document.getElementById("inspectorTitle").textContent = `Key Inspector: Button ${index + 1}`;
  document.getElementById("inspectorSubtitle").textContent = `Pin: GPIO ${pin} • ${index === 0 ? 'Mode Button' : 'Macro Key'}`;
  document.getElementById("selectedKeyBadge").textContent = `B${index + 1}`;
  document.getElementById("inputButtonLabel").value = btn.label || "";

  ['single', 'double', 'hold'].forEach(trigger => {
    const action = btn[trigger] || { type: 'none' };
    const select = document.getElementById(`${trigger}ActionType`);
    select.value = action.type;
    renderTriggerSettings(trigger, action);
  });
}

function createDefaultAction(type) {
  if (type === 'home_assistant') {
    // Tanpa entity hardcode — user memilih lewat Entity Picker.
    return { type: 'home_assistant', domain: '', service: '', entityId: '', friendlyName: '' };
  }
  if (type === 'launch_app') return { type: 'launch_app', desktopId: 'code.desktop', appName: 'Visual Studio Code' };
  if (type === 'system_action') return { type: 'system_action', presetId: 'mic_toggle_mute', presetName: 'Toggle Microphone Mute' };
  if (type === 'bash_script') return { type: 'bash_script', script: 'notify-send "MacroPad" "Action!"' };
  if (type === 'ha_webhook') return { type: 'ha_webhook', url: '' };
  if (type === 'shortcut') return { type: 'shortcut', modifiers: ['ctrl', 'alt', 'shift'], key: 'A' };
  if (type === 'text') return { type: 'text', text: 'Hello World' };
  if (type === 'media') return { type: 'media', mediaKey: 'VOL_UP' };
  if (type === 'mode_toggle') return { type: 'mode_toggle' };
  return { type: 'none' };
}

function renderTriggerSettings(trigger, action) {
  const container = document.getElementById(`${trigger}SettingsContainer`);
  container.innerHTML = "";

  if (action.type === 'none') {
    container.innerHTML = `<span style="font-size: 0.75rem; color: var(--text-dim);">Aksi ini dinonaktifkan (tidak ada input dikirim).</span>`;
    return;
  }

  if (action.type === 'mode_toggle') {
    container.innerHTML = `<span style="font-size: 0.75rem; color: #8b5cf6;">Mengganti layer antara Desktop Mode dan Home Assistant Mode.</span>`;
    return;
  }

  // 1. Native Home Assistant Service Integration (Zero Scripts!)
  if (action.type === 'home_assistant') {
    const wrap = document.createElement("div");
    wrap.className = "form-group";

    const currentDomain = action.domain || (action.entityId ? action.entityId.split('.')[0] : '');
    const selected = haEntities.find(e => e.entity_id === action.entityId);
    const services = (Array.isArray(action.services) && action.services.length)
      ? action.services
      : (selected && selected.services) || ["toggle", "turn_on", "turn_off"];
    if (action.entityId && !services.includes(action.service)) {
      action.service = services[0] || "";
    }
    const serviceOptions = services.map(s =>
      `<option value="${escapeHtml(s)}" ${action.service === s ? 'selected' : ''}>${escapeHtml(s)}</option>`
    ).join("");
    const stateLabel = selected && selected.state != null ? String(selected.state) : "-";
    const canTest = !!currentDomain && !!action.entityId;

    wrap.innerHTML = `
      <div class="ha-picker-head">
        <label class="form-label">Pilih HA → lalu pilih Entity</label>
        <div class="ha-picker-btns">
          <button type="button" class="btn-test-action btn-pick-entity" title="Scan & pilih entity dari Home Assistant">${icon("repeat")} Pilih Entity</button>
          <button type="button" class="btn-test-action btn-config-ha" title="Atur URL & token Home Assistant">${icon("settings")} Koneksi</button>
        </div>
      </div>
      ${haConfigured ? "" : `<p class="ha-inline-warning">${icon("triangle-alert")} Home Assistant belum dikonfigurasi — klik <b>Koneksi</b> (isi URL + token), sistem otomatis memindai semua entity interaktif.</p>`}
      <div class="ha-selected-box ${action.entityId ? "" : "empty"}">
        <span class="entity-icon">${icon(entityIconName(selected || action), "icon-md")}</span>
        <span class="entity-body">
          <span class="entity-name">${escapeHtml(action.friendlyName || "Belum ada entity dipilih")}</span>
          <span class="entity-id">${escapeHtml(action.entityId || "klik Pilih Entity untuk memindai & memilih")}</span>
        </span>
        <span class="entity-state ${action.entityId ? haStateClass(selected && selected.state) : "state-na"}">${escapeHtml(action.entityId ? stateLabel : "-")}</span>
      </div>
      <div class="ha-service-row">
        <div class="ha-service-field">
          <label class="form-label" style="font-size:0.72rem;">Domain</label>
          <input type="text" class="form-input domain-input" value="${escapeHtml(currentDomain)}" readonly placeholder="-">
        </div>
        <div class="ha-service-field">
          <label class="form-label" style="font-size:0.72rem;">Service Action</label>
          <select class="form-select service-select" ${canTest ? "" : "disabled"}>${serviceOptions}</select>
        </div>
        <button type="button" class="btn-test-action btn-test-ha" title="Eksekusi service sekarang" ${canTest ? "" : "disabled"}>${icon("play")} Test</button>
      </div>
    `;

    wrap.querySelector(".btn-pick-entity").addEventListener("click", () => openEntityPicker(trigger));
    wrap.querySelector(".btn-config-ha").addEventListener("click", () => openHaConfigDialog({ openPickerAfterSave: true }));
    wrap.querySelector(".service-select").addEventListener("change", (e) => {
      action.service = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });
    wrap.querySelector(".btn-test-ha").addEventListener("click", () => {
      testCallHomeAssistant(action.domain, action.service, action.entityId);
    });

    container.appendChild(wrap);
    return;
  }

  // 2. Launch Ubuntu App
  if (action.type === 'launch_app') {
    const wrap = document.createElement("div");
    wrap.className = "form-group";
    wrap.innerHTML = `
      <label class="form-label">Aplikasi Ubuntu Terpilih</label>
      <div class="selected-app-box">
        <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
          ${icon(actionIcon(action), "icon-lg")}
          <div style="overflow:hidden;">
            <div style="font-weight:700; font-size:0.85rem;" id="selectedAppName_${trigger}">
              ${escapeHtml(action.appName || action.desktopId || 'Belum dipilih')}
            </div>
            <div style="font-size:0.68rem; color:var(--text-dim); font-family:var(--font-mono);">
              ${escapeHtml(action.desktopId || '')}
            </div>
          </div>
        </div>
        <div style="display:flex; gap:6px;">
          <button type="button" class="btn btn-xs btn-outline btn-choose-app">Pilih App</button>
          <button type="button" class="btn-test-action btn-test-launch" title="Uji coba jalankan aplikasi sekarang">${icon("play")} Test</button>
        </div>
      </div>
    `;

    wrap.querySelector(".btn-choose-app").addEventListener("click", () => {
      openAppPicker(trigger);
    });

    wrap.querySelector(".btn-test-launch").addEventListener("click", () => {
      testLaunchApp(action.desktopId);
    });

    container.appendChild(wrap);
    return;
  }

  // 3. Preset System Actions
  if (action.type === 'system_action') {
    const wrap = document.createElement("div");
    wrap.className = "form-group";

    const presetsToUse = systemPresets.length > 0 ? systemPresets : [
      { id: "mic_toggle_mute", name: "Toggle Microphone Mute" },
      { id: "volume_up_5", name: "Volume Up (+5%)" },
      { id: "volume_down_5", name: "Volume Down (-5%)" },
      { id: "volume_toggle_mute", name: "Toggle Speaker Mute" },
      { id: "lock_screen", name: "Lock Ubuntu Session" },
      { id: "open_terminal", name: "Open New Terminal" },
      { id: "screenshot_interactive", name: "Interactive Screenshot (Area)" }
    ];

    const options = presetsToUse.map(p => `
      <option value="${p.id}" ${action.presetId === p.id ? 'selected' : ''}>
        ${escapeHtml(p.name)}
      </option>
    `).join("");

    wrap.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label class="form-label">Pilih Otomasi Sistem</label>
        <button type="button" class="btn-test-action btn-test-preset">${icon("play")} Test Aksi</button>
      </div>
      <select class="form-select">${options}</select>
    `;

    const select = wrap.querySelector("select");
    select.addEventListener("change", (e) => {
      action.presetId = e.target.value;
      const selectedPreset = presetsToUse.find(p => p.id === e.target.value);
      action.presetName = selectedPreset ? selectedPreset.name : e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });

    wrap.querySelector(".btn-test-preset").addEventListener("click", () => {
      testExecutePreset(action.presetId);
    });

    container.appendChild(wrap);
    return;
  }

  // 4. Bash Script
  if (action.type === 'bash_script') {
    const wrap = document.createElement("div");
    wrap.className = "form-group";
    wrap.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label class="form-label">Skrip Shell / Bash</label>
        <button type="button" class="btn-test-action btn-test-bash">${icon("play")} Test Jalankan</button>
      </div>
      <textarea class="form-input" rows="3" style="font-family:var(--font-mono); font-size:0.8rem;" placeholder="e.g. notify-send 'MacroPad' 'Pressed!'">${escapeHtml(action.script || '')}</textarea>
    `;
    const textarea = wrap.querySelector("textarea");
    textarea.addEventListener("input", (e) => {
      action.script = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });
    wrap.querySelector(".btn-test-bash").addEventListener("click", () => {
      showToast("Menjalankan script bash...", "info");
    });
    container.appendChild(wrap);
    return;
  }

  // 5. Home Assistant Webhook
  if (action.type === 'ha_webhook') {
    const wrap = document.createElement("div");
    wrap.className = "form-group";
    wrap.innerHTML = `
      <label class="form-label">URL Webhook Home Assistant</label>
      <input type="url" class="form-input" value="${escapeHtml(action.url || '')}" placeholder="http://homeassistant.local:8123/api/webhook/my_macro">
    `;
    const input = wrap.querySelector("input");
    input.addEventListener("input", (e) => {
      action.url = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });
    container.appendChild(wrap);
    return;
  }

  // 6. Text String Macro
  if (action.type === 'text') {
    const group = document.createElement("div");
    group.className = "form-group";
    group.innerHTML = `
      <label class="form-label">Teks yang akan diketik langsung (String)</label>
      <input type="text" class="form-input" value="${escapeHtml(action.text || '')}" placeholder="Masukkan teks / passcode...">
    `;
    const input = group.querySelector("input");
    input.addEventListener("input", (e) => {
      action.text = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });
    container.appendChild(group);
    return;
  }

  // 7. Media Control
  if (action.type === 'media') {
    const group = document.createElement("div");
    group.className = "form-group";
    const options = MEDIA_ACTIONS.map(m => `<option value="${m.value}" ${action.mediaKey === m.value ? 'selected' : ''}>${m.label}</option>`).join("");
    group.innerHTML = `
      <label class="form-label">Media Action</label>
      <select class="form-select">${options}</select>
    `;
    const select = group.querySelector("select");
    select.addEventListener("change", (e) => {
      action.mediaKey = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });
    container.appendChild(group);
    return;
  }

  // 8. Keyboard Shortcut
  if (action.type === 'shortcut') {
    const modifiersDiv = document.createElement("div");
    modifiersDiv.className = "modifier-row";

    const mods = ['ctrl', 'alt', 'shift', 'super'];
    mods.forEach(mod => {
      const isChecked = (action.modifiers || []).includes(mod);
      const label = document.createElement("label");
      label.className = "modifier-checkbox";
      label.innerHTML = `
        <input type="checkbox" value="${mod}" ${isChecked ? 'checked' : ''}>
        <span>${mod.toUpperCase()}</span>
      `;
      label.querySelector("input").addEventListener("change", () => {
        const checkedList = Array.from(modifiersDiv.querySelectorAll("input:checked")).map(cb => cb.value);
        action.modifiers = checkedList;
        updateKeyVisual(selectedButtonIndex);
      });
      modifiersDiv.appendChild(label);
    });

    const keySelectGroup = document.createElement("div");
    keySelectGroup.className = "form-group";
    keySelectGroup.style.marginTop = "6px";

    let optGroups = "";
    AVAILABLE_KEYS.forEach(grp => {
      const opts = grp.keys.map(k => `<option value="${k}" ${action.key === k ? 'selected' : ''}>${k}</option>`).join("");
      optGroups += `<optgroup label="${grp.group}">${opts}</optgroup>`;
    });

    keySelectGroup.innerHTML = `
      <label class="form-label">Target Key Code</label>
      <select class="form-select">${optGroups}</select>
    `;

    keySelectGroup.querySelector("select").addEventListener("change", (e) => {
      action.key = e.target.value;
      updateKeyVisual(selectedButtonIndex);
    });

    container.appendChild(modifiersDiv);
    container.appendChild(keySelectGroup);
  }
}

// ============================================================================
// Native Home Assistant API Calls
// ============================================================================
async function testCallHomeAssistant(domain, service, entityId) {
  showToast(`Memanggil Home Assistant: ${domain}.${service} -> ${entityId}...`, 'info');
  try {
    const res = await fetch('/api/ha/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, service, entityId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Sukses: ${data.message}`, 'success');
    } else {
      showToast(`Gagal: ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Gagal menghubungi server lokal: ${err.message}`, 'error');
  }
}

// ============================================================================
// Interactive Application Picker
// ============================================================================
function openAppPicker(trigger) {
  pendingAppPickerTarget = trigger;
  const modal = document.getElementById("appPickerDialog");
  document.getElementById("inputAppSearch").value = "";
  renderFilteredApps("");
  modal.showModal();
}

function renderFilteredApps(filterText) {
  const grid = document.getElementById("modalAppsGrid");
  grid.innerHTML = "";

  const query = filterText.toLowerCase().trim();
  const filtered = installedApps.filter(app => {
    return !query || app.name.toLowerCase().includes(query) || app.id.toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 30px; color:var(--text-dim);">Tidak ada aplikasi yang cocok dengan "${escapeHtml(filterText)}"</div>`;
    return;
  }

  filtered.forEach(app => {
    const card = document.createElement("div");
    card.className = "app-card";
    card.innerHTML = `
      <div class="app-card-icon">${icon("laptop", "icon-md")}</div>
      <div class="app-card-info">
        <div class="app-card-name">${escapeHtml(app.name)}</div>
        <div class="app-card-id">${escapeHtml(app.id)}</div>
      </div>
    `;

    card.addEventListener("click", () => {
      selectAppForTrigger(app);
    });

    grid.appendChild(card);
  });
}

function selectAppForTrigger(app) {
  if (!pendingAppPickerTarget) return;

  const btn = getCurrentButtonConfig();
  const trigger = pendingAppPickerTarget;
  btn[trigger] = {
    type: 'launch_app',
    desktopId: app.id,
    appName: app.name,
    icon: app.icon
  };

  if (!btn.label || btn.label.startsWith("Button ") || btn.label.startsWith("Macro ")) {
    btn.label = app.name.slice(0, 14);
    document.getElementById("inputButtonLabel").value = btn.label;
  }

  renderTriggerSettings(trigger, btn[trigger]);
  updateKeyVisual(selectedButtonIndex);

  document.getElementById("appPickerDialog").close();
  showToast(`Aplikasi "${app.name}" dipilih untuk Button ${selectedButtonIndex + 1}!`, 'success');
}

async function testLaunchApp(desktopId) {
  try {
    const res = await fetch('/api/apps/launch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ desktopId })
    });
    const data = await res.json();
    showToast(data.message || `Berhasil: ${desktopId}`, data.success ? 'success' : 'error');
  } catch (e) {
    showToast(`Error: ${e.message}`, 'error');
  }
}

async function testExecutePreset(presetId) {
  try {
    const res = await fetch('/api/system-actions/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ presetId })
    });
    const data = await res.json();
    showToast(data.message || "Aksi dieksekusi", data.success ? 'success' : 'error');
  } catch (e) {
    showToast(`Error: ${e.message}`, 'error');
  }
}

// ============================================================================
// Save / Flash Configurations
// ============================================================================
async function handleSaveAllConfigs() {
  let savedLocal = false;
  let savedHardware = false;

  if (daemonAvailable) {
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appConfig)
      });
      if (res.ok) savedLocal = true;
    } catch (e) {}
  }

  if (isConnected) {
    await flashConfigToDevice();
    savedHardware = true;
  }

  if (savedLocal && savedHardware) {
    showToast("Konfigurasi tersimpan ke sistem Ubuntu & memori MacroPad!", "success");
  } else if (savedLocal) {
    showToast("Konfigurasi tersimpan permanen di Ubuntu (~/.config).", "success");
  } else if (savedHardware) {
    showToast("Konfigurasi terkirim ke memori ESP32!", "success");
  } else {
    exportProfileJson();
    showToast("Profil diekspor ke file JSON.", "info");
  }
}

// ============================================================================
// Web Serial Communication Engine
// ============================================================================
function setupWebSerialSupport() {
  if (!("serial" in navigator)) return;

  navigator.serial.addEventListener("disconnect", () => {
    logSerial("[HARDWARE] Port Serial terputus (kabel dicabut).", "system");
    disconnectDevice();
  });
}

async function handleToggleConnection() {
  if (isConnected) {
    await disconnectDevice();
  } else {
    await connectDevice();
  }
}

async function connectDevice() {
  if (!("serial" in navigator)) {
    showToast("Web Serial API membutuhkan Chrome / Chromium.", "error");
    return;
  }

  try {
    serialPort = await navigator.serial.requestPort();
    await serialPort.open({ baudRate: 115200 });

    isConnected = true;
    updateConnectionUI(true);
    showToast("Terhubung ke SamVivan MacroPad!", "success");
    logSerial("[HARDWARE] Terhubung via Serial (115200 Baud).", "system");

    readSerialLoop();

    setTimeout(() => {
      sendSerialCommand("CMD:PING");
    }, 400);

  } catch (err) {
    logSerial(`[ERROR] Gagal konek: ${err.message}`, "system");
    updateConnectionUI(false);
  }
}

async function disconnectDevice() {
  isConnected = false;
  if (serialReader) {
    try {
      await serialReader.cancel();
      serialReader.releaseLock();
    } catch (_) {}
    serialReader = null;
  }
  if (serialWriter) {
    try {
      serialWriter.releaseLock();
    } catch (_) {}
    serialWriter = null;
  }
  if (serialPort) {
    try {
      await serialPort.close();
    } catch (_) {}
    serialPort = null;
  }
  updateConnectionUI(false);
  showToast("MacroPad disconnected.", "info");
}

function updateConnectionUI(connected) {
  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");
  const btn = document.getElementById("btnConnect");
  const btnText = document.getElementById("btnConnectText");
  const btnRead = document.getElementById("btnReadConfig");

  if (connected) {
    dot.className = "status-indicator connected";
    text.textContent = "Connected";
    btn.className = "btn btn-outline";
    btnText.textContent = "Disconnect";
    btnRead.disabled = false;
  } else {
    dot.className = "status-indicator";
    text.textContent = "Disconnected";
    btn.className = "btn btn-primary";
    btnText.textContent = "Connect Device";
    btnRead.disabled = true;
  }
}

async function readSerialLoop() {
  const textDecoder = new TextDecoderStream();
  const readableStreamClosed = serialPort.readable.pipeTo(textDecoder.writable);
  serialReader = textDecoder.readable.getReader();

  try {
    while (true) {
      const { value, done } = await serialReader.read();
      if (done) break;
      if (value) {
        serialBuffer += value;
        const lines = serialBuffer.split("\n");
        serialBuffer = lines.pop();
        for (const line of lines) {
          processIncomingSerialLine(line.trim());
        }
      }
    }
  } catch (err) {
  } finally {
    serialReader.releaseLock();
  }
}

function processIncomingSerialLine(line) {
  if (!line) return;
  logSerial(line, "rx");

  const buttonMatch = line.match(/Button\s+(\d+)\s+->\s+(\w+)/i);
  if (buttonMatch) {
    const btnNumber = parseInt(buttonMatch[1], 10);
    const eventType = buttonMatch[2];
    triggerHardwareKeyPressVisual(btnNumber - 1, eventType);
  }

  if (line.includes("MODE: HOME ASSISTANT")) {
    switchMode(1);
    blinkLedVisual();
  } else if (line.includes("MODE: DESKTOP")) {
    switchMode(0);
    blinkLedVisual();
  }
}

function triggerHardwareKeyPressVisual(index, eventType) {
  const keyEl = document.getElementById(`keySwitch_${index}`);
  const hintEl = document.getElementById("liveFeedbackNotice");
  if (keyEl) {
    keyEl.classList.add("hardware-pressed");
    setTimeout(() => keyEl.classList.remove("hardware-pressed"), 180);
  }
  if (hintEl) {
    hintEl.innerHTML = `${icon("zap")} Event Terdeteksi: Button ${index + 1} (${eventType})`;
    hintEl.style.color = "#34d399";
  }
}

function blinkLedVisual() {
  const bulb = document.getElementById("boardLedBulb");
  if (bulb) {
    bulb.classList.add("blink");
    setTimeout(() => bulb.classList.remove("blink"), 300);
  }
}

async function sendSerialCommand(cmd) {
  if (!serialPort || !isConnected) return;
  try {
    const textEncoder = new TextEncoder();
    const writer = serialPort.writable.getWriter();
    await writer.write(textEncoder.encode(cmd + "\n"));
    writer.releaseLock();
    logSerial(cmd, "tx");
  } catch (err) {}
}

function handleSendCustomSerial() {
  const input = document.getElementById("customSerialInput");
  const val = input.value.trim();
  if (val) {
    sendSerialCommand(val);
    input.value = "";
  }
}

async function flashConfigToDevice() {
  if (!isConnected) return;
  const payload = JSON.stringify(appConfig);
  await sendSerialCommand(`CMD:SET_CONFIG ${payload}`);
}

async function readConfigFromDevice() {
  if (!isConnected) return;
  await sendSerialCommand("CMD:GET_CONFIG");
}

function logSerial(msg, type = "rx") {
  const out = document.getElementById("consoleOutput");
  const div = document.createElement("div");
  div.className = `log-line log-${type}`;
  const time = new Date().toLocaleTimeString();
  div.textContent = `[${time}] ${msg}`;
  out.appendChild(div);
  out.scrollTop = out.scrollHeight;
}

// ============================================================================
// Profile Import / Export & Presets
// ============================================================================
function exportProfileJson() {
  const jsonString = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appConfig, null, 2));
  const dlAnchor = document.createElement("a");
  dlAnchor.setAttribute("href", jsonString);
  dlAnchor.setAttribute("download", `samvivan-macropad-profile-${new Date().toISOString().slice(0,10)}.json`);
  document.body.appendChild(dlAnchor);
  dlAnchor.click();
  dlAnchor.remove();
  showToast("Profil berhasil diekspor sebagai file JSON!", "success");
}

function importProfileJson(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      if (!data.modes || !Array.isArray(data.modes)) {
        throw new Error("Format JSON tidak valid untuk SamVivan MacroPad.");
      }
      appConfig = data;
      renderKeysGrid();
      loadButtonIntoInspector(selectedButtonIndex);
      showToast("Profil berhasil dimuat!", "success");
    } catch (err) {
      showToast(`Gagal membaca file: ${err.message}`, "error");
    }
  };
  reader.readAsText(file);
}

function applyPreset(presetKey) {
  if (presetKey === 'default') {
    appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    showToast("Preset Default (Desktop & Native HA) dimuat.", "info");
  } else if (presetKey === 'productivity') {
    appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    const desktopBtns = appConfig.modes[0].buttons;
    desktopBtns[1].label = "Terminal";
    desktopBtns[1].single = { type: "system_action", presetId: "open_terminal" };
    desktopBtns[2].label = "Screenshot";
    desktopBtns[2].single = { type: "system_action", presetId: "screenshot_interactive" };
    desktopBtns[3].label = "Lock Screen";
    desktopBtns[3].single = { type: "system_action", presetId: "lock_screen" };
    desktopBtns[4].label = "VS Code";
    desktopBtns[4].single = { type: "launch_app", desktopId: "code.desktop", appName: "Visual Studio Code" };
    showToast("Preset Ubuntu Productivity dimuat.", "info");
  } else if (presetKey === 'media') {
    appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    const desktopBtns = appConfig.modes[0].buttons;
    desktopBtns[1].label = "Play / Pause";
    desktopBtns[1].single = { type: "media", mediaKey: "PLAY_PAUSE" };
    desktopBtns[2].label = "Vol Down";
    desktopBtns[2].single = { type: "system_action", presetId: "volume_down_5" };
    desktopBtns[3].label = "Vol Up";
    desktopBtns[3].single = { type: "system_action", presetId: "volume_up_5" };
    desktopBtns[4].label = "Mute";
    desktopBtns[4].single = { type: "system_action", presetId: "volume_toggle_mute" };
    showToast("Preset Media & Streaming dimuat.", "info");
  }
  renderKeysGrid();
  loadButtonIntoInspector(selectedButtonIndex);
}

// ============================================================================
// Utilities
// ============================================================================
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
