#include <HijelHID_BLEKeyboard.h>
#include <Preferences.h>
#include <ArduinoJson.h>

HijelHID_BLEKeyboard keyboard("SamVivan MacroPad", "SamVivan", 100);

constexpr uint8_t BUTTON_COUNT = 8;
constexpr uint8_t MODE_BUTTON = 0; // B1 = GPIO20
constexpr uint8_t LED_PIN = 4;

// Parameter Waktu Akurat untuk Jari Manusia
constexpr unsigned long DEBOUNCE_MS = 25;     // Filter getaran mekanis saklar
constexpr unsigned long CLICK_TIMEOUT = 250;  // Jeda maksimal ANTAR KETUKAN (setelah dilepas)
constexpr unsigned long HOLD_TIMEOUT = 450;   // Durasi tahan untuk fungsi HOLD (Long Press)

Preferences prefs;

const uint8_t buttonPins[BUTTON_COUNT] = {20, 9, 2, 1, 21, 10, 3, 0};


// --- Configurable mapping (akan diload dari NVS) ---
uint8_t cfg_desktopSingle[7] = {KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8};
uint8_t cfg_desktopDouble[7] = {KEY_Q, KEY_W, KEY_E, KEY_I, KEY_T, KEY_Y, KEY_U};
uint8_t cfg_desktopHold[7]   = {KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J};
uint8_t cfg_haSingle[7]      = {KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8};
uint8_t cfg_haDouble[7]      = {KEY_Z,  KEY_X,  KEY_C,  KEY_V,  KEY_B,  KEY_N,  KEY_P};
uint8_t cfg_haHold[7]        = {KEY_9,  KEY_0,  KEY_I,  KEY_O,  KEY_P,  KEY_K,  KEY_L};

unsigned long cfg_debounce = DEBOUNCE_MS;
unsigned long cfg_click   = CLICK_TIMEOUT;
unsigned long cfg_hold    = HOLD_TIMEOUT;


enum MacroMode { DESKTOP_MODE, HOME_ASSISTANT_MODE };
MacroMode currentMode = DESKTOP_MODE;

enum ButtonEvent { NONE, SINGLE_CLICK, DOUBLE_CLICK, HOLD };

struct Button {
  uint8_t pin;
  bool lastRawState;
  bool stableState;
  unsigned long lastDebounceTime;
  
  uint8_t clickCount;
  unsigned long lastReleaseTime;  // Waktu melepas tombol (Arah deteksi klik ganda)
  unsigned long lastPressTime;    // Waktu menekan tombol (Arah deteksi HOLD)
  bool holdReported;
  bool isPressed;
};

Button buttons[BUTTON_COUNT];

void sendShortcut(uint8_t key) {
  if (!keyboard.isConnected()) return;

  keyboard.press(KEY_LCTRL);
  keyboard.press(KEY_LALT);
  keyboard.press(KEY_LSHIFT);
  delay(5); 

  keyboard.press(key);
  delay(15); 
  keyboard.releaseAll();
}

void toggleMode() {
  if (currentMode == DESKTOP_MODE) {
    currentMode = HOME_ASSISTANT_MODE;
    Serial.println("MODE: HOME ASSISTANT");
    digitalWrite(LED_PIN, LOW);   
  } else {
    currentMode = DESKTOP_MODE;
    Serial.println("MODE: DESKTOP");
    digitalWrite(LED_PIN, HIGH);  
  }
}

bool loadConfigFromNVS() {
  prefs.begin("macropad", false);
  if (!prefs.isKey("ver")) {
    prefs.end();
    return false;
  }
  int ver = prefs.getInt("ver", 1);
  (void)ver;
  cfg_debounce = prefs.getULong("debounceMs", cfg_debounce);
  cfg_click    = prefs.getULong("clickMs", cfg_click);
  cfg_hold     = prefs.getULong("holdMs", cfg_hold);

  prefs.getBytes("d1", cfg_desktopSingle, 7);
  prefs.getBytes("d2", cfg_desktopDouble, 7);
  prefs.getBytes("dh", cfg_desktopHold, 7);
  prefs.getBytes("h1", cfg_haSingle, 7);
  prefs.getBytes("h2", cfg_haDouble, 7);
  prefs.getBytes("hh", cfg_haHold, 7);
  prefs.end();
  return true;
}

void saveConfigToNVS() {
  prefs.begin("macropad", false);
  prefs.putInt("ver", 1);
  prefs.putULong("debounceMs", cfg_debounce);
  prefs.putULong("clickMs", cfg_click);
  prefs.putULong("holdMs", cfg_hold);
  prefs.putBytes("d1", cfg_desktopSingle, 7);
  prefs.putBytes("d2", cfg_desktopDouble, 7);
  prefs.putBytes("dh", cfg_desktopHold, 7);
  prefs.putBytes("h1", cfg_haSingle, 7);
  prefs.putBytes("h2", cfg_haDouble, 7);
  prefs.putBytes("hh", cfg_haHold, 7);
  prefs.end();
}

// Fungsi Dinamis untuk Kedip LED (Dioptimalkan menjadi 80ms agar lag berkurang)
void blinkLED(uint8_t count) {
  bool baseState = digitalRead(LED_PIN); 
  for (uint8_t i = 0; i < count; i++) {
    digitalWrite(LED_PIN, !baseState); 
    delay(80);
    digitalWrite(LED_PIN, baseState);  
    delay(80);
  }
}

void handleButtonEvent(uint8_t buttonIndex, ButtonEvent event) {
  // 1. Eksekusi Perintah/Shortcut Terlebih Dahulu (Respons Kecepatan Tinggi)
  if (buttonIndex == MODE_BUTTON) {
    if (event == SINGLE_CLICK) {
      toggleMode(); 
    } 
    else if (event == HOLD) {
      Serial.println("[SYSTEM] Button 1 -> LONG PRESS: Sending '031004'");
      if (keyboard.isConnected()) {
        keyboard.print("031004");
      }
    }
  } 
  else {
    // Tombol Makro (Button 2-8)
    const uint8_t actionIndex = buttonIndex - 1; 
    uint8_t targetKey = 0;

    if (currentMode == DESKTOP_MODE) {
      if (event == SINGLE_CLICK)      targetKey = cfg_desktopSingle[actionIndex];
      else if (event == DOUBLE_CLICK) targetKey = cfg_desktopDouble[actionIndex];
      else if (event == HOLD)         targetKey = cfg_desktopHold[actionIndex];
    } else {
      if (event == SINGLE_CLICK)      targetKey = cfg_haSingle[actionIndex];
      else if (event == DOUBLE_CLICK) targetKey = cfg_haDouble[actionIndex];
      else if (event == HOLD)         targetKey = cfg_haHold[actionIndex];
    }

    if (targetKey != 0) {
      sendShortcut(targetKey);
    }
  }

  // 2. Cetak Log Debug ke Serial Monitor
  String modeText = (currentMode == DESKTOP_MODE) ? "DESKTOP" : "HA";
  String eventText = (event == SINGLE_CLICK) ? "SINGLE" : (event == DOUBLE_CLICK) ? "DOUBLE" : "HOLD";
  Serial.printf("[%s] Button %d -> %s (LED Feedback Processed)\n", modeText.c_str(), buttonIndex + 1, eventText.c_str());

  // 3. Aturan Global LED Feedback untuk Tombol MANAPUN (Termasuk Button 1)
  if (event == SINGLE_CLICK) {
    // "Tidak jadi apa-apa" -> LED tidak berkedip, mempertahankan state lampu utama.
  } 
  else if (event == DOUBLE_CLICK) {
    blinkLED(2); // Kedip 2x untuk seluruh Double Click
  } 
  else if (event == HOLD) {
    blinkLED(3); // Kedip 3x untuk seluruh Long Press
  }
}

void setup() {
  Serial.begin(115200);
  delay(400);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); 

  for (uint8_t i = 0; i < BUTTON_COUNT; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
    bool initReading = digitalRead(buttonPins[i]);
    
    buttons[i].pin = buttonPins[i];
    buttons[i].lastRawState = initReading;
    buttons[i].stableState = initReading;
    buttons[i].lastDebounceTime = 0;
    buttons[i].clickCount = 0;
    buttons[i].lastReleaseTime = 0;
    buttons[i].lastPressTime = 0;
    buttons[i].holdReported = false;
    buttons[i].isPressed = false;
  }

  loadConfigFromNVS();
  keyboard.begin();
  Serial.println("BLE MacroPad Ready (config loaded)");
}


void handleSerialCommand() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  if (line.startsWith("CMD:GET_CONFIG")) {
    StaticJsonDocument<1024> doc;
    doc["debounceMs"] = cfg_debounce;
    doc["clickTimeoutMs"] = cfg_click;
    doc["holdTimeoutMs"] = cfg_hold;
    JsonArray d1 = doc.createNestedArray("d1");
    JsonArray d2 = doc.createNestedArray("d2");
    JsonArray dh = doc.createNestedArray("dh");
    JsonArray h1 = doc.createNestedArray("h1");
    JsonArray h2 = doc.createNestedArray("h2");
    JsonArray hh = doc.createNestedArray("hh");
    for (int i = 0; i < 7; i++) { d1.add(cfg_desktopSingle[i]); d2.add(cfg_desktopDouble[i]); dh.add(cfg_desktopHold[i]); h1.add(cfg_haSingle[i]); h2.add(cfg_haDouble[i]); hh.add(cfg_haHold[i]); }
    String out; serializeJson(doc, out);
    Serial.println(out);
    return;
  }

  if (line.startsWith("CMD:SAVE_CONFIG")) {
    saveConfigToNVS();
    Serial.println("{\"ok\":true,\"msg\":\"config saved\"}");
    return;
  }

  if (line.startsWith("CMD:RESET_CONFIG")) {
    cfg_debounce = DEBOUNCE_MS; cfg_click = CLICK_TIMEOUT; cfg_hold = HOLD_TIMEOUT;
    uint8_t def_d1[7]={KEY_2,KEY_3,KEY_4,KEY_5,KEY_6,KEY_7,KEY_8};
    uint8_t def_d2[7]={KEY_Q,KEY_W,KEY_E,KEY_I,KEY_T,KEY_Y,KEY_U};
    uint8_t def_dh[7]={KEY_A,KEY_S,KEY_D,KEY_F,KEY_G,KEY_H,KEY_J};
    uint8_t def_h1[7]={KEY_F2,KEY_F3,KEY_F4,KEY_F5,KEY_F6,KEY_F7,KEY_F8};
    uint8_t def_h2[7]={KEY_Z,KEY_X,KEY_C,KEY_V,KEY_B,KEY_N,KEY_P};
    uint8_t def_hh[7]={KEY_9,KEY_0,KEY_I,KEY_O,KEY_P,KEY_K,KEY_L};
    memcpy(cfg_desktopSingle,def_d1,7); memcpy(cfg_desktopDouble,def_d2,7); memcpy(cfg_desktopHold,def_dh,7);
    memcpy(cfg_haSingle,def_h1,7); memcpy(cfg_haDouble,def_h2,7); memcpy(cfg_haHold,def_hh,7);
    saveConfigToNVS();
    Serial.println("{\"ok\":true,\"msg\":\"reset+saved\"}");
    return;
  }

  if (line.startsWith("CMD:SET_CONFIG:")) {
    String json = line.substring(String("CMD:SET_CONFIG:").length());
    StaticJsonDocument<1024> doc; DeserializationError err = deserializeJson(doc, json);
    if (err) { Serial.println("{\"ok\":false,\"msg\":\"json invalid\"}"); return; }
    if (doc.containsKey("debounceMs")) cfg_debounce = doc["debounceMs"];
    if (doc.containsKey("clickTimeoutMs")) cfg_click = doc["clickTimeoutMs"];
    if (doc.containsKey("holdTimeoutMs")) cfg_hold = doc["holdTimeoutMs"];
    if (doc.containsKey("d1")) for (int i=0;i<7 && i<doc["d1"].size(); i++) cfg_desktopSingle[i]=doc["d1"][i];
    if (doc.containsKey("d2")) for (int i=0;i<7 && i<doc["d2"].size(); i++) cfg_desktopDouble[i]=doc["d2"][i];
    if (doc.containsKey("dh")) for (int i=0;i<7 && i<doc["dh"].size(); i++) cfg_desktopHold[i]=doc["dh"][i];
    if (doc.containsKey("h1")) for (int i=0;i<7 && i<doc["h1"].size(); i++) cfg_haSingle[i]=doc["h1"][i];
    if (doc.containsKey("h2")) for (int i=0;i<7 && i<doc["h2"].size(); i++) cfg_haDouble[i]=doc["h2"][i];
    if (doc.containsKey("hh")) for (int i=0;i<7 && i<doc["hh"].size(); i++) cfg_haHold[i]=doc["hh"][i];
    Serial.println("{\"ok\":true,\"msg\":\"applied\"}");
    return;
  }
}

void loop() {
  handleSerialCommand();
  unsigned long now = millis();

  for (uint8_t i = 0; i < BUTTON_COUNT; i++) {
    bool rawReading = digitalRead(buttons[i].pin);

    // Debounce Filter
    if (rawReading != buttons[i].lastRawState) {
      buttons[i].lastDebounceTime = now;
      buttons[i].lastRawState = rawReading;
    }

    if ((now - buttons[i].lastDebounceTime) >= cfg_debounce) {
      if (rawReading != buttons[i].stableState) {
        buttons[i].stableState = rawReading;
        
        if (buttons[i].stableState == LOW) { 
          buttons[i].isPressed = true;
          buttons[i].lastPressTime = now;   
        } else { 
          buttons[i].isPressed = false;
          if (!buttons[i].holdReported) {
            buttons[i].clickCount++;
            buttons[i].lastReleaseTime = now; 
          } else {
            buttons[i].holdReported = false;  
          }
        }
      }
    }

    // Logika Evaluasi HOLD
    if (buttons[i].isPressed && !buttons[i].holdReported) {
      if (now - buttons[i].lastPressTime >= cfg_hold) {
        buttons[i].holdReported = true;
        buttons[i].clickCount = 0; 
        handleButtonEvent(i, HOLD);
      }
    }

    // Logika Evaluasi Klik (Single / Double)
    if (!buttons[i].isPressed) {
      if (buttons[i].clickCount == 1 && (now - buttons[i].lastReleaseTime >= cfg_click)) {
        handleButtonEvent(i, SINGLE_CLICK);
        buttons[i].clickCount = 0;
      }
      else if (buttons[i].clickCount >= 2) {
        handleButtonEvent(i, DOUBLE_CLICK);
        buttons[i].clickCount = 0;
      }
    }
  }
  delay(1); 
}