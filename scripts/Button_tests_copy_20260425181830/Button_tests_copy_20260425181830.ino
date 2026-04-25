#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SCIENTIST_PIN    39
#define ENGINEER_PIN     40
#define ENTREPRENEUR_PIN 41

#define SERVICE_UUID "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "abcd1234-ab12-ab12-ab12-abcdef123456"

const unsigned long debounceDelay = 50;

BLECharacteristic *pCharacteristic;

struct Button {
  int pin;
  bool stableState;
  bool lastReading;
  unsigned long lastChangeTime;
  const char* name;
  const char* category;
};

Button scientist    = {SCIENTIST_PIN, HIGH, HIGH, 0, "SCIENTIST", "scientist"};
Button engineer     = {ENGINEER_PIN, HIGH, HIGH, 0, "ENGINEER", "engineer"};
Button entrepreneur = {ENTREPRENEUR_PIN, HIGH, HIGH, 0, "ENTREPRENEUR", "entrepreneur"};

void setupBLE();
void updateButton(Button &btn);
void sendCategory(const char* category);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=== ESP32 BUTTON BLE READ TEST ===");

  pinMode(SCIENTIST_PIN, INPUT_PULLUP);
  pinMode(ENGINEER_PIN, INPUT_PULLUP);
  pinMode(ENTREPRENEUR_PIN, INPUT_PULLUP);

  delay(100);

  scientist.stableState    = digitalRead(SCIENTIST_PIN);
  engineer.stableState     = digitalRead(ENGINEER_PIN);
  entrepreneur.stableState = digitalRead(ENTREPRENEUR_PIN);

  scientist.lastReading    = scientist.stableState;
  engineer.lastReading     = engineer.stableState;
  entrepreneur.lastReading = entrepreneur.stableState;

  scientist.lastChangeTime    = millis();
  engineer.lastChangeTime     = millis();
  entrepreneur.lastChangeTime = millis();

  setupBLE();

  Serial.println("Ready.");
}

void loop() {
  updateButton(scientist);
  updateButton(engineer);
  updateButton(entrepreneur);
}

void setupBLE() {
  BLEDevice::init("ESP32 Selector");

  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ
  );

  pCharacteristic->setValue("{\"category\":\"none\"}");

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->start();

  Serial.println("BLE advertising...");
}

void sendCategory(const char* category) {
  String payload = "{\"category\":\"";
  payload += category;
  payload += "\"}";

  pCharacteristic->setValue(payload.c_str());

  Serial.print("Updated BLE value: ");
  Serial.println(payload);
}

void updateButton(Button &btn) {
  bool reading = digitalRead(btn.pin);

  if (reading != btn.lastReading) {
    btn.lastChangeTime = millis();
    btn.lastReading = reading;
  }

  if ((millis() - btn.lastChangeTime) > debounceDelay) {
    if (reading != btn.stableState) {
      btn.stableState = reading;

      if (btn.stableState == LOW) {
        Serial.printf(">>> %s pressed\n", btn.name);
        sendCategory(btn.category);
      }
    }
  }
}
