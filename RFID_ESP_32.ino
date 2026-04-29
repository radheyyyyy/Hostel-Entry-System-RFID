#include <WiFi.h>
#include <WebServer.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <U8g2lib.h>

// 🔥 PINS
#define SS_PIN 5
#define RST_PIN 4
#define BTN_CLASS 13
#define BTN_OUTSIDE 12

MFRC522 mfrc522(SS_PIN, RST_PIN);
WebServer server(80);

// OLED
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// WiFi AP
const char* ssid = "RFID_SYSTEM";
const char* password = "12345678";

// 🔥 DATA
String lastUID = "";
String lastMove = "";
String displayName = "Scan Card";
String displayStatus = "";

bool showChoice = false;   // 🔥 NEW

// 🔹 Send UID
void handleUID() {
  if (lastUID != "") {
    server.send(200, "text/plain", "UID:" + lastUID);
    lastUID = "";
  } else {
    server.send(200, "text/plain", "");
  }
}

// 🔹 Send MOVE
void handleMove() {
  if (lastMove != "") {
    server.send(200, "text/plain", "MOVE:" + lastMove);
    lastMove = "";
  } else {
    server.send(200, "text/plain", "");
  }
}

// 🔹 Receive display data
void handleDisplay() {
  if (server.hasArg("name") && server.hasArg("status")) {
    displayName = server.arg("name");
    displayStatus = server.arg("status");

    Serial.println(displayName + " - " + displayStatus);
    server.send(200, "text/plain", "OK");
  }
}

// 🔹 Normal OLED
void updateOLED() {
  u8g2.clearBuffer();

  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 15, "Hostel System");

  u8g2.setFont(u8g2_font_ncenB10_tr);
  u8g2.drawStr(0, 35, displayName.c_str());

  u8g2.setFont(u8g2_font_ncenB14_tr);
  u8g2.drawStr(0, 60, displayStatus.c_str());

  u8g2.sendBuffer();
}

// 🔥 NEW: Choice screen
void showChoiceScreen() {
  u8g2.clearBuffer();

  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 15, "Select Option");

  u8g2.drawStr(0, 35, "Btn1: CLASS");
  u8g2.drawStr(0, 55, "Btn2: OUTSIDE");

  u8g2.sendBuffer();
}

void setup() {
  Serial.begin(115200);

  SPI.begin(18, 19, 23, 5);
  mfrc522.PCD_Init();

  u8g2.begin();

  pinMode(BTN_CLASS, INPUT_PULLUP);
  pinMode(BTN_OUTSIDE, INPUT_PULLUP);

  WiFi.softAP(ssid, password);

  server.on("/uid", handleUID);
  server.on("/move", handleMove);
  server.on("/display", handleDisplay);

  server.begin();

  displayName = "Ready...";
  displayStatus = "";
  updateOLED();
}

void loop() {
  server.handleClient();

  // 🔥 BUTTON CHECK
  if (digitalRead(BTN_CLASS) == LOW) {
    lastMove = "CLASS";
    Serial.println("MOVE:CLASS");
    showChoice = false;   // 🔥 reset screen
    delay(300);
  }

  if (digitalRead(BTN_OUTSIDE) == LOW) {
    lastMove = "OUTSIDE";
    Serial.println("MOVE:OUTSIDE");
    showChoice = false;   // 🔥 reset screen
    delay(300);
  }

  // 🔥 OLED CONTROL
  if (showChoice) {
    showChoiceScreen();
  } else {
    updateOLED();
  }

  // 🔹 RFID READ
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i], HEX);
    if (i != mfrc522.uid.size - 1) uid += " ";
  }

  uid.toUpperCase();
  lastUID = uid;

  Serial.println("UID: " + uid);

  showChoice = true;   // 🔥 SHOW BUTTON MESSAGE

  delay(500);
}
