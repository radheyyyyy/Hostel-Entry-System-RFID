# 🏠 Hostel Entry Monitoring System using RFID (ESP32 + Python)

A smart hostel monitoring system that tracks **IN/OUT movement of residents** using **RFID cards**, **ESP32**, and a **Python GUI dashboard** with real-time updates.

---

## 🚀 Features

* 🔐 RFID-based authentication (MFRC522)
* 🔄 Automatic IN/OUT status detection
* 🎯 Movement tracking (CLASS / OUTSIDE)
* 📡 Dual communication:

  * WiFi (ESP32 Access Point)
  * Serial fallback
* 📺 OLED display for instant feedback
* 🖥️ Python GUI dashboard (Tkinter + ttkbootstrap)
* 📊 Real-time table updates
* 💾 JSON-based persistent storage
* 📝 Entry history logging system
* 🛠️ Admin panel (Edit + Reset records)

---

## 🧰 Hardware Required

* ESP32
* MFRC522 RFID Module
* OLED Display (SH1106, I2C)
* Push Buttons (2x: CLASS / OUTSIDE)
* RFID Cards/Tags
* Jumper Wires
* Breadboard
* USB Cable

---

## 🔌 Wiring Connections

### 🔹 ESP32 ↔ MFRC522 (SPI)

| MFRC522 Pin | ESP32 Pin |
| ----------- | --------- |
| SDA (SS)    | GPIO 5    |
| SCK         | GPIO 18   |
| MOSI        | GPIO 23   |
| MISO        | GPIO 19   |
| RST         | GPIO 4    |
| GND         | GND       |
| 3.3V        | 3.3V      |

---

### 🔹 ESP32 ↔ OLED (I2C)

| OLED Pin | ESP32 Pin |
| -------- | --------- |
| VCC      | 3.3V      |
| GND      | GND       |
| SDA      | GPIO 21   |
| SCL      | GPIO 22   |

---

### 🔹 Buttons (Movement Selection)

| Button  | ESP32 Pin |
| ------- | --------- |
| CLASS   | GPIO 13   |
| OUTSIDE | GPIO 12   |

---

⚠️ **Important Notes**

* Always use **3.3V (NOT 5V)**
* Ensure proper grounding
* Use pull-up buttons (INPUT_PULLUP in code)

---

## 💻 ESP32 Code Features

* Reads RFID UID
* Creates WiFi Access Point:

```text
SSID: RFID_SYSTEM
Password: 12345678
IP: 192.168.4.1
```

* API Endpoints:

  * `/uid` → sends UID
  * `/move` → sends movement (CLASS / OUTSIDE)
  * `/display` → receives name + status

* OLED displays:

  * Name
  * Status (IN / OUT)
  * Movement selection screen

---

## 🧠 System Workflow

### 🔹 Step 1: Scan RFID

* UID is read by ESP32
* Sent to Python via WiFi

---

### 🔹 Step 2: Python Processing

| Last Status | Action            |
| ----------- | ----------------- |
| OUT         | Mark as IN        |
| IN          | Wait for movement |

---

### 🔹 Step 3: Movement Selection

* User presses:

  * CLASS button
  * OUTSIDE button
* ESP32 sends movement

---

### 🔹 Step 4: Final Update

* Status set to OUT
* Movement stored
* GUI + OLED updated

---

## 🖥️ Python Application

### 🔹 Features

* Live dashboard
* Table with:

  * UID
  * Name
  * Room
  * Status
  * Movement
  * Timestamp
* Popup notifications (IN / OUT)
* Admin controls:

  * Reset records (password protected)
  * Edit user details

---

## 📦 Required Python Libraries

```bash
pip install pyserial ttkbootstrap requests
```

---

## 📁 Project Structure

```
project-folder/
┣ 📜 main.py
┣ 📜 esp32_code.ino
┣ 📜 uid_details.json
┣ 📜 uid_status.json
┣ 📜 entry_history.txt
┗ 📜 README.md
```

---

## 💾 Data Storage

### uid_details.json

```json
{
  "UID123": {
    "name": "Raj",
    "room": "D-318"
  }
}
```

### uid_status.json

```json
{
  "UID123": {
    "status": "OUT",
    "move": "CLASS"
  }
}
```

---

## ⚙️ Setup Instructions

### 🔹 ESP32

1. Open Arduino IDE
2. Select ESP32 board
3. Upload code
4. Power the device

---

### 🔹 Python App

```bash
python main.py
```

---

## ⚠️ Common Issues & Fixes

### 🔴 WiFi not connecting

* Connect to **RFID_SYSTEM**
* Check IP: `192.168.4.1`

### 🔴 RFID not detecting

* Check SPI wiring
* Ensure correct pins

### 🔴 OLED not working

* Verify SDA/SCL pins
* Check I2C address

### 🔴 Movement not saving

* Ensure JSON save logic correct
* Fix movement restore in Python

---

##  Future Improvements

*  Mobile App Integration
* Cloud Database (Firebase / MongoDB)
*  Analytics Dashboard
*  Notifications System
* Face Recognition Integration

---

##  Author

**Rajyavardhan Radhey**
CSE-AI | CSJMU Kanpur

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!!
