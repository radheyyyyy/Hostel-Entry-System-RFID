# 🏨 Hostel Entry Monitoring System

A **Python-based RFID Hostel Entry Monitoring System** built using **Tkinter + ttkbootstrap**, **ESP32**, and **MySQL** to monitor hostel resident entry and exit in real time.

This system scans RFID cards, updates resident status (IN/OUT), logs history, and provides a live dashboard for hostel administrators.

---

## 🚀 Features

✅ RFID card scanning using ESP32 + RC522
✅ Automatic IN/OUT status tracking
✅ New card registration popup
✅ Real-time occupancy dashboard
✅ MySQL database storage
✅ Entry history logging
✅ Export status to CSV
✅ Duplicate scan protection (cooldown system)
✅ Modern UI with ttkbootstrap

---

## ⚙️ How the System Works

1. Resident scans RFID card.
2. ESP32 reads UID and sends it to computer via Serial.
3. Python app receives UID.
4. If UID is new → registration window opens.
5. If UID exists → status toggles:

   * OUT ➜ IN
   * IN ➜ OUT
6. Dashboard updates instantly.
7. Data is saved to MySQL and log file.

---

## 🧰 Technologies Used

* Python
* Tkinter
* ttkbootstrap
* MySQL
* PySerial
* ESP32
* MFRC522 RFID Module

---

## 📂 Project Structure

```
Hostel-Entry-System/
│
├── main.py
├── entry_history.txt
├── status_export.csv
├── README.md
└── esp32_rfid.ino
```

---

## 🛠️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/hostel-entry-system.git
cd hostel-entry-system
```

---

### 2️⃣ Install Python Dependencies

```bash
pip install ttkbootstrap pyserial mysql-connector-python
```

---

### 3️⃣ Setup MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE hostel_entry;
```

Update credentials in the Python file:

```python
self.conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="hostel_entry"
)
```

⚠️ **Never upload real passwords to GitHub.**

---

### 4️⃣ Update Serial Port

Modify COM port inside the code:

```python
self.ser = serial.Serial('COM16', 115200, timeout=1)
```

Examples:

* Windows → COM3, COM16
* Linux → /dev/ttyUSB0
* Mac → /dev/cu.usbserial

---

### 5️⃣ Run the Application

```bash
python main.py
```

---

## 🧑‍💻 Usage Guide

### ➤ Register New RFID Card

1. Scan unknown card
2. Enter resident name & room
3. Click **Save**

### ➤ Track Entry & Exit

* Scan once → IN
* Scan again → OUT

### ➤ Reset Records

Clears status and sets everyone to **OUT**.

### ➤ Export CSV

Creates:

```
status_export.csv
```

---

## 🗃️ Database Schema

### residents

| Field | Type    | Description   |
| ----- | ------- | ------------- |
| uid   | VARCHAR | RFID UID      |
| name  | VARCHAR | Resident name |
| room  | VARCHAR | Room number   |

### status

| Field | Type     | Description    |
| ----- | -------- | -------------- |
| uid   | VARCHAR  | RFID UID       |
| state | VARCHAR  | IN / OUT       |
| time  | DATETIME | Last scan time |

---

## 📜 Scan Log File

All scans are recorded in:

```
entry_history.txt
```

Format:

```
YYYY-MM-DD HH:MM:SS | UID | Name | Room | Status
```

---

# 🔌 ESP32 RFID Integration

This system uses an **ESP32** with an **MFRC522 RFID reader** to scan cards and send UID data to the Python application.

---

## 🧰 Required Hardware

* ESP32 Development Board
* MFRC522 RFID Module
* RFID cards/tags
* Jumper wires

---

## 🔗 Wiring Connections (ESP32 ↔ RC522)

| RC522 Pin | ESP32 Pin |
| --------- | --------- |
| SDA (SS)  | GPIO 5    |
| SCK       | GPIO 18   |
| MOSI      | GPIO 23   |
| MISO      | GPIO 19   |
| RST       | GPIO 22   |
| GND       | GND       |
| 3.3V      | 3.3V      |

⚠️ RC522 works on **3.3V only**.

---

## 📦 Install RFID Library

In Arduino IDE:

**Library Manager → Install**

```
MFRC522 by GithubCommunity
```

---

## 🧾 ESP32 RFID Code

Upload this code to your ESP32:

```cpp
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 22

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  Serial.println("Scan RFID Card");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();

  Serial.print("UID:");
  Serial.println(uid);

  delay(1000); // prevents multiple scans
}
```

---

## 🖥️ Serial Output Example

When a card is scanned:

```
UID:3F5A8B12
```

The Python system reads this UID and updates entry status.

---

## 🔧 Troubleshooting ESP32

✔ Ensure baud rate is **115200**
✔ Check correct COM port
✔ Use high-quality USB cable
✔ Increase delay if duplicate scans occur
✔ Ensure RC522 connected to **3.3V**

---

## 🔒 Security Notes

❗ Do NOT upload:

* Database passwords
* Personal resident data
* Local database dumps

Use environment variables for credentials in production.

---

## 🧪 Future Improvements

* Admin login system
* Mobile app dashboard
* Cloud database integration
* Late entry alerts
* Attendance analytics
* RFID scan sound/LED feedback

---

## 🤝 Contributing

Pull requests are welcome!

1. Fork the repo
2. Create a branch
3. Commit changes
4. Open a Pull Request

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Your Name**
GitHub: https://github.com/yourusername

---
