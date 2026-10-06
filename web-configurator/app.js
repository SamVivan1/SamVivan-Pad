/**
 * SamVivan MacroPad Studio - Web Configurator & Hardware Manager
 * Compatible with ESP32-C3 SuperMini running SamVivan MacroPad Firmware
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

// Default configuration matching macropadv2.5.ino
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
          label: "Macro 1",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "2" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "Q" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "A" }
        },
        {
          index: 2,
          pin: 2,
          label: "Macro 2",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "3" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "W" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "S" }
        },
        {
          index: 3,
          pin: 1,
          label: "Macro 3",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "4" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "E" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "D" }
        },
        {
          index: 4,
          pin: 21,
          label: "Macro 4",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "5" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "I" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F" }
        },
        {
          index: 5,
          pin: 10,
          label: "Macro 5",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "6" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "T" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "G" }
        },
        {
          index: 6,
          pin: 3,
          label: "Macro 6",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "7" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "Y" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "H" }
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
        {
          index: 1,
          pin: 9,
          label: "HA Light 1",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F2" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "Z" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "9" }
        },
        {
          index: 2,
          pin: 2,
          label: "HA Light 2",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F3" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "X" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "0" }
        },
        {
          index: 3,
          pin: 1,
          label: "HA Scene",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F4" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "C" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "I" }
        },
        {
          index: 4,
          pin: 21,
          label: "HA Switch 1",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F5" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "V" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "O" }
        },
        {
          index: 5,
          pin: 10,
          label: "HA Switch 2",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F6" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "B" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "P" }
        },
        {
          index: 6,
          pin: 3,
          label: "HA Fan",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F7" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "N" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "K" }
        },
        {
          index: 7,
          pin: 0,
          label: "HA Media",
          single: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "F8" },
          double: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "P" },
          hold: { type: "shortcut", modifiers: ["ctrl", "alt", "shift"], key: "L" }
        }
      ]
    }
  ]
};

// Application State
let appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
let selectedButtonIndex = 0;
let currentModeIndex = 0;

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
  initDOM();
  renderKeysGrid();
  loadButtonIntoInspector(selectedButtonIndex);
  setupWebSerialSupport();
});

function initDOM() {
  // Mode Switcher Tabs
  document.getElementById("tabDesktopMode").addEventListener("click", () => switchMode(0));
  document.getElementById("tabHaMode").addEventListener("click", () => switchMode(1));

  // Connect Button
  document.getElementById("btnConnect").addEventListener("click", handleToggleConnection);

  // Monitor drawer toggles
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

  // Custom Serial Input send
  document.getElementById("btnSendSerial").addEventListener("click", handleSendCustomSerial);
  document.getElementById("customSerialInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSendCustomSerial();
  });

  // Profile Dropdown
  const btnProfileMenu = document.getElementById("btnProfileMenu");
  const profileDropdown = document.getElementById("profileDropdown");
  btnProfileMenu.addEventListener("click", (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle("show");
  });
  window.addEventListener("click", () => profileDropdown.classList.remove("show"));

  // Profile Export / Import
  document.getElementById("btnExportJson").addEventListener("click", exportProfileJson);
  document.getElementById("fileImportJson").addEventListener("change", importProfileJson);

  // Preset Handlers
  document.querySelectorAll(".preset-option").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const presetKey = e.currentTarget.dataset.preset;
      applyPreset(presetKey);
    });
  });

  // Device Flash / Read Buttons
  document.getElementById("btnWriteConfig").addEventListener("click", flashConfigToDevice);
  document.getElementById("btnReadConfig").addEventListener("click", readConfigFromDevice);

  // Inspector form bindings
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

  // Timing inputs
  ['Debounce', 'ClickTimeout', 'HoldTimeout'].forEach(key => {
    const input = document.getElementById(`input${key}`);
    input.addEventListener("change", () => {
      const field = key === 'Debounce' ? 'debounceMs' : (key === 'ClickTimeout' ? 'clickTimeoutMs' : 'holdTimeoutMs');
      appConfig[field] = parseInt(input.value, 10);
      showToast(`Updated ${field} to ${input.value}ms`, 'info');
    });
  });
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
    if (action.type === 'text') return `"${action.text.slice(0, 7)}${action.text.length > 7 ? '..' : ''}"`;
    if (action.type === 'media') return `Media: ${action.mediaKey}`;
    if (action.type === 'shortcut') {
      const mods = (action.modifiers || []).map(m => m[0].toUpperCase()).join('+');
      return mods ? `${mods}+${action.key}` : action.key;
    }
    return action.type;
  };

  return `
    <span class="action-chip chip-single" title="Single Click: ${getLabel(btn.single)}">1x: ${getLabel(btn.single)}</span>
    <span class="action-chip chip-double" title="Double Click: ${getLabel(btn.double)}">2x: ${getLabel(btn.double)}</span>
    <span class="action-chip chip-hold" title="Hold: ${getLabel(btn.hold)}">H: ${getLabel(btn.hold)}</span>
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
// Web Serial Communication Engine
// ============================================================================
function setupWebSerialSupport() {
  if (!("serial" in navigator)) {
    logSerial("[STUDIO] Peringatan: Web Serial API tidak didukung pada browser ini. Gunakan Google Chrome, Chromium, MS Edge, atau Brave.", "system");
    document.getElementById("statusText").textContent = "WebSerial Unavailable";
    return;
  }

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
    showToast("Browser Anda belum mendukung Web Serial API. Gunakan Chrome / Chromium.", "error");
    return;
  }

  try {
    serialPort = await navigator.serial.requestPort();
    await serialPort.open({ baudRate: 115200 });

    isConnected = true;
    updateConnectionUI(true);
    showToast("Terhubung ke SamVivan MacroPad!", "success");
    logSerial("[HARDWARE] Terhubung via Serial (115200 Baud).", "system");

    // Start reading stream
    readSerialLoop();

    // Send PING to verify
    setTimeout(() => {
      sendSerialCommand("CMD:PING");
    }, 400);

  } catch (err) {
    console.error("Serial connection error:", err);
    logSerial(`[ERROR] Gagal konek: ${err.message}`, "system");
    showToast(`Koneksi dibatalkan atau gagal: ${err.message}`, "error");
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
  const btnWrite = document.getElementById("btnWriteConfig");

  if (connected) {
    dot.className = "status-indicator connected";
    text.textContent = "Connected";
    btn.className = "btn btn-outline";
    btnText.textContent = "Disconnect";
    btnRead.disabled = false;
    btnWrite.disabled = false;
  } else {
    dot.className = "status-indicator";
    text.textContent = "Disconnected";
    btn.className = "btn btn-primary";
    btnText.textContent = "Connect Device";
    btnRead.disabled = true;
    btnWrite.disabled = true;
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
        serialBuffer = lines.pop(); // keep last incomplete chunk
        for (const line of lines) {
          processIncomingSerialLine(line.trim());
        }
      }
    }
  } catch (err) {
    console.error("Stream reading error:", err);
  } finally {
    serialReader.releaseLock();
  }
}

function processIncomingSerialLine(line) {
  if (!line) return;
  logSerial(line, "rx");

  // Real-time hardware feedback parsing
  // E.g. [DESKTOP] Button 2 -> SINGLE (LED Feedback Processed)
  // or [HA] Button 1 -> DOUBLE (LED Feedback Processed)
  const buttonMatch = line.match(/Button\s+(\d+)\s+->\s+(\w+)/i);
  if (buttonMatch) {
    const btnNumber = parseInt(buttonMatch[1], 10); // 1-8
    const eventType = buttonMatch[2]; // SINGLE, DOUBLE, HOLD
    triggerHardwareKeyPressVisual(btnNumber - 1, eventType);
  }

  // Mode change parsing
  if (line.includes("MODE: HOME ASSISTANT")) {
    switchMode(1);
    blinkLedVisual();
  } else if (line.includes("MODE: DESKTOP")) {
    switchMode(0);
    blinkLedVisual();
  }

  // Configuration JSON response from ESP32
  if (line.startsWith("CONFIG_DATA:")) {
    try {
      const jsonStr = line.substring("CONFIG_DATA:".length);
      const imported = JSON.parse(jsonStr);
      appConfig = imported;
      renderKeysGrid();
      loadButtonIntoInspector(selectedButtonIndex);
      showToast("Berhasil membaca konfigurasi dari memori ESP32!", "success");
    } catch (e) {
      logSerial(`[ERROR] Gagal parse JSON konfigurasi dari ESP32: ${e.message}`, "system");
    }
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
    hintEl.textContent = `⚡ Event Terdeteksi: Button ${index + 1} (${eventType})`;
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
  if (!serialPort || !isConnected) {
    showToast("Perangkat belum terhubung!", "error");
    return;
  }
  try {
    const textEncoder = new TextEncoder();
    const writer = serialPort.writable.getWriter();
    await writer.write(textEncoder.encode(cmd + "\n"));
    writer.releaseLock();
    logSerial(cmd, "tx");
  } catch (err) {
    logSerial(`[ERROR] Gagal mengirim: ${err.message}`, "system");
    showToast(`Gagal kirim: ${err.message}`, "error");
  }
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
  if (!isConnected) {
    showToast("Silakan hubungkan MacroPad via USB terlebih dahulu.", "error");
    return;
  }

  showToast("Menyiapkan payload konfigurasi...", "info");
  const payload = JSON.stringify(appConfig);
  // Send via chunked / structured command
  await sendSerialCommand(`CMD:SET_CONFIG ${payload}`);
  showToast("Konfigurasi terkirim ke ESP32! Tunggu konfirmasi NVS.", "success");
}

async function readConfigFromDevice() {
  if (!isConnected) {
    showToast("Silakan hubungkan MacroPad via USB terlebih dahulu.", "error");
    return;
  }
  showToast("Mengambil data konfigurasi dari ESP32...", "info");
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
    showToast("Preset Default v2.5 dimuat.", "info");
  } else if (presetKey === 'productivity') {
    appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    // Customize for Ubuntu shortcuts
    const desktopBtns = appConfig.modes[0].buttons;
    desktopBtns[1].label = "Terminal";
    desktopBtns[1].single = { type: "shortcut", modifiers: ["ctrl", "alt"], key: "T" };
    desktopBtns[2].label = "Screenshot";
    desktopBtns[2].single = { type: "shortcut", modifiers: ["shift", "super"], key: "S" };
    desktopBtns[3].label = "Lock Screen";
    desktopBtns[3].single = { type: "shortcut", modifiers: ["super"], key: "L" };
    desktopBtns[4].label = "Files";
    desktopBtns[4].single = { type: "shortcut", modifiers: ["super"], key: "E" };
    showToast("Preset Ubuntu Productivity dimuat.", "info");
  } else if (presetKey === 'media') {
    appConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    const desktopBtns = appConfig.modes[0].buttons;
    desktopBtns[1].label = "Play / Pause";
    desktopBtns[1].single = { type: "media", mediaKey: "PLAY_PAUSE" };
    desktopBtns[2].label = "Vol Down";
    desktopBtns[2].single = { type: "media", mediaKey: "VOL_DOWN" };
    desktopBtns[3].label = "Vol Up";
    desktopBtns[3].single = { type: "media", mediaKey: "VOL_UP" };
    desktopBtns[4].label = "Mute";
    desktopBtns[4].single = { type: "media", mediaKey: "MUTE" };
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
