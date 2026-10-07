#include <HijelHID_BLEKeyboard.h>
#include <Preferences.h>

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

// --- LAYER DESKTOP MODE ---
uint8_t cfg_desktopSingle[BUTTON_COUNT - 1] = {KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8};
uint8_t cfg_desktopDouble[BUTTON_COUNT - 1] = {KEY_Q, KEY_W, KEY_E, KEY_I, KEY_T, KEY_Y, KEY_U};
uint8_t cfg_desktopHold[BUTTON_COUNT - 1]   = {KEY_A, KEY_S, KEY_D, KEY_F, KEY_G, KEY_H, KEY_J};

// --- LAYER HOME ASSISTANT MODE ---
uint8_t cfg_haSingle[BUTTON_COUNT - 1]  = {KEY_F2, KEY_F3, KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8};
uint8_t cfg_haDouble[BUTTON_COUNT - 1]  = {KEY_Z,  KEY_X,  KEY_C,  KEY_V,  KEY_B,  KEY_N,  KEY_P};
uint8_t cfg_haHold[BUTTON_COUNT - 1]    = {KEY_9,  KEY_0,  KEY_I,  KEY_O,  KEY_P,  KEY_K,  KEY_L};

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


bool loadConfig() {
  prefs.begin("mp", false);
  if (!prefs.isKey("v")) {
    prefs.end();
    return false;
  }
  prefs.getBytes("d1", cfg_desktopSingle, 7);
  prefs.getBytes("d2", cfg_desktopDouble, 7);
  prefs.getBytes("dh", cfg_desktopHold, 7);
  prefs.getBytes("h1", cfg_haSingle, 7);
  prefs.getBytes("h2", cfg_haDouble, 7);
  prefs.getBytes("hh", cfg_haHold, 7);
  prefs.end();
  return true;
}

void saveConfig() {
  prefs.begin("mp", false);
  prefs.putUChar("v", 1);
  prefs.putBytes("d1", cfg_desktopSingle, 7);
  prefs.putBytes("d2", cfg_desktopDouble, 7);
  prefs.putBytes("dh", cfg_desktopHold, 7);
  prefs.putBytes("h1", cfg_haSingle, 7);
  prefs.putBytes("h2", cfg_haDouble, 7);
  prefs.putBytes("hh", cfg_haHold, 7);
  prefs.end();
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

  loadConfig();
  keyboard.begin();
  Serial.println("BLE MacroPad Ready");
}


void handleCmd() {
  if (!Serial.available()) return;
  String l = Serial.readStringUntil('\\n');
  l.trim();

  if (l.startsWith("SET ")) {
    // SET <key> <c0,c1,c2,c3,c4,c5,c6>
    String rest = l.substring(4);
    int sp = rest.indexOf(' ');
    if (sp > 0) {
      String key = rest.substring(0, sp);
      String csv = rest.substring(sp + 1);
      uint8_t* arr = nullptr;
      if (key == "d1") arr = cfg_desktopSingle;
      else if (key == "d2") arr = cfg_desktopDouble;
      else if (key == "dh") arr = cfg_desktopHold;
      else if (key == "h1") arr = cfg_haSingle;
      else if (key == "h2") arr = cfg_haDouble;
      else if (key == "hh") arr = cfg_haHold;
      if (arr) {
        int i = 0, s = 0;
        while (i < 7 && s < (int)csv.length()) {
          int e = csv.indexOf(',', s);
          String tok = (e < 0) ? csv.substring(s) : csv.substring(s, e);
          arr[i] = (uint8_t)strtol(tok.c_str(), nullptr, 10);
          i++;
          if (e < 0) break;
          s = e + 1;
        }
        Serial.println(String("SET:") + key + ":OK");
        return;
      }
    }
    Serial.println("SET:ERR");
    return;
  }
  if (l.startsWith("SAVE")) {
    saveConfig();
    Serial.println("SAVED");
    return;
  }
  if (l.startsWith("RESET")) {
    // keep defaults; save
    saveConfig();
    Serial.println("RESET+SAVED");
    return;
  }
}

void loop() {
  handleCmd();
  unsigned long now = millis();

  for (uint8_t i = 0; i < BUTTON_COUNT; i++) {
    bool rawReading = digitalRead(buttons[i].pin);

    // Debounce Filter
    if (rawReading != buttons[i].lastRawState) {
      buttons[i].lastDebounceTime = now;
      buttons[i].lastRawState = rawReading;
    }

    if ((now - buttons[i].lastDebounceTime) >= DEBOUNCE_MS) {
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
      if (now - buttons[i].lastPressTime >= HOLD_TIMEOUT) {
        buttons[i].holdReported = true;
        buttons[i].clickCount = 0; 
        handleButtonEvent(i, HOLD);
      }
    }

    // Logika Evaluasi Klik (Single / Double)
    if (!buttons[i].isPressed) {
      if (buttons[i].clickCount == 1 && (now - buttons[i].lastReleaseTime >= CLICK_TIMEOUT)) {
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