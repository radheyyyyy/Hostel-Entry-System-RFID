# 🏠 Hostel Entry Monitoring System using RFID (ESP8266 + Python)

This project is a **Hostel Entry Monitoring System** that uses an **RFID reader (MFRC522)** with **ESP8266 (NodeMCU)** to scan student cards and send UID data to a **Python-based desktop application** for real-time tracking.

---

##  Features

* RFID-based entry/exit tracking
*  Automatic student identification via UID
*  IN/OUT status toggle system
*  Live dashboard (Python GUI)
*  Entry logs stored in file
*  New card registration system

---

##  Hardware Required

* ESP8266 (NodeMCU)
* MFRC522 RFID Module
* RFID Cards/Tags
* Jumper wires
* Breadboard
* USB cable

---

## 🔌 Wiring (ESP8266 ↔ MFRC522)

| MFRC522 Pin | NodeMCU Pin |
| ----------- | ----------- |
| SDA (SS)    | D2          |
| SCK         | D5          |
| MOSI        | D7          |
| MISO        | D6          |
| RST         | D1          |
| GND         | GND         |
| 3.3V        | 3.3V        |

> **Important Note:** Do NOT connect to 5V. Use only **3.3V**.

---

## 💻 ESP8266 Code

This code reads RFID card UID and sends it via Serial.

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <SPI.h>
#include <MFRC522.h>

//  UPDATED PINS (your wiring)
#define SS_PIN D2   // SDA
#define RST_PIN D1  // RST

MFRC522 mfrc522(SS_PIN, RST_PIN);
ESP8266WebServer server(80);

// WiFi AP
const char* ssid = "RFID_SYSTEM";
const char* password = "********";

String lastUID = "";

void handleUID() {
  if (lastUID != "") {
    server.send(200, "text/plain", "UID:" + lastUID);
    lastUID = ""; // send once
  } else {
    server.send(200, "text/plain", "");
  }
}

void setup() {
  Serial.begin(115200);
  SPI.begin();  // uses default pins: D5, D6, D7

  mfrc522.PCD_Init();

  WiFi.softAP(ssid, password);

  Serial.println("WiFi AP Started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());

  server.on("/uid", handleUID);
  server.begin();
}

void loop() {
  server.handleClient();

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

  delay(1000);
}
```

---

## 🖥️ Python Application

The Python app:

* Reads serial data from ESP8266
* Matches UID with database
* Updates entry/exit status
* Displays GUI dashboard

###  Required Libraries

```bash
pip install pyserial ttkbootstrap
```

---

## ⚙️ Setup Instructions

1. Upload the ESP8266 code using Arduino IDE
2. Connect RFID module properly
3. Check COM port in Device Manager
4. Update COM port in Python code:

   ```python
   serial.Serial('COM7', 115200)
   ```
5. Run the Python application

---

##  Common Issues & Fixes

###  "Access is denied (COM port error)"

* Close Arduino Serial Monitor
* Ensure correct COM port
* Run Python as Administrator

### RFID not detecting

* Check wiring carefully
* Ensure SPI pins are correct
* Use 3.3V power only

---

## 📁 Project Structure

```
 project-folder
 ┣ 📜 esp8266_rfid.ino
 ┣ 📜 main_app.py
 ┣ 📜 uid_details.json
 ┣ 📜 uid_status.json
 ┣ 📜 entry_history.txt
 ┗ 📜 README.md
```

---

##  Future Improvements

*  Web-based dashboard
*  Mobile notifications
*  Face recognition integration
*  Cloud database

---

##  Support

If you like this project, give it a ⭐ on GitHub!

---
