import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import threading
import json
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from serial.tools import list_ports
import socket
import requests

class HostelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hostel Entry Monitoring System")
        self.root.geometry("1000x700")

        # --- Data Files ---
        self.UID_DB_FILE = 'uid_details.json'
        self.STATUS_FILE = 'uid_status.json'
        self.SCAN_LOG_FILE = 'entry_history.txt'

        # --- App Variables ---
        self.last_uid = None
        self.last_scan_time = 0
        self.SCAN_COOLDOWN = 5  # seconds
        self.uid_to_item_id = {}
        self.ADMIN_PASSWORD = "admin123"

        # --- Load Data ---
        self.uid_info = self._load_json(self.UID_DB_FILE)
        self.uid_last_status = self._load_json(self.STATUS_FILE)

        # --- Create and Style UI ---
        self._create_widgets()
        self._restore_previous_state()
        self._update_dashboard()

        # --- Start Serial Communication ---
        self._start_serial_thread()

    def _load_json(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}

    def _save_json(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def _create_widgets(self):
        # --- Header ---
        header_frame = ttk.Frame(self.root, padding=20)
        header_frame.pack(fill=X)
        header_label = ttk.Label(header_frame, text="Hostel Entry Monitoring System", font=("Segoe UI", 24, "bold"), bootstyle=PRIMARY)
        header_label.pack()

        # --- Dashboard ---
        dash_frame = ttk.Frame(self.root, padding=(20, 10))
        dash_frame.pack(fill=X)

        self.residents_in_label = ttk.Label(dash_frame, text="Residents In: 0", font=("Segoe UI", 14, "bold"), bootstyle=SUCCESS)
        self.residents_in_label.pack(side=LEFT, padx=20)

        self.total_residents_label = ttk.Label(dash_frame, text="Total Registered: 0", font=("Segoe UI", 14), bootstyle=INFO)
        self.total_residents_label.pack(side=LEFT, padx=20)
        
        # --- Main Table Frame ---
        table_frame = ttk.Frame(self.root, padding=20)
        table_frame.pack(expand=True, fill=BOTH)

        columns = ("UID", "Name", "Room", "Status", "Time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", bootstyle=PRIMARY)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=CENTER)

        # Adding striped rows for better readability
        self.tree.tag_configure('oddrow', background='#f0f4f7')
        self.tree.tag_configure('evenrow', background='#ffffff')

        self.tree.pack(side=LEFT, expand=True, fill=BOTH)

        # --- Scrollbar ---
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        # --- Footer/Control Panel ---
        footer_frame = ttk.Frame(self.root, padding=20)
        footer_frame.pack(fill=X)

        reset_button = ttk.Button(footer_frame, text="Reset All Records", command=self.reset_records, bootstyle=(DANGER, OUTLINE), width=20)
        reset_button.pack()
        edit_button = ttk.Button(
            footer_frame,
            text="Edit Records",
            command=self.edit_names,
            bootstyle=(INFO, OUTLINE),
            width=20
        )
        edit_button.pack(pady=5)
        

    def _update_dashboard(self):
        residents_in_count = list(self.uid_last_status.values()).count("IN")
        total_residents_count = len(self.uid_info)
        
        self.residents_in_label.config(text=f"Residents In: {residents_in_count}")
        self.total_residents_label.config(text=f"Total Registered: {total_residents_count}")

    def log_scan(self, uid, name, room, status, timestamp):
        with open(self.SCAN_LOG_FILE, "a") as f:
            f.write(f"{timestamp} | UID: {uid} | Name: {name} | Room: {room} | Status: {status}\n")

    def update_table(self, uid, status, silent=False):
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')
        user = self.uid_info.get(uid, {"name": "Unknown", "room": "N/A"})

        values = (uid, user["name"], user["room"], status, now_str)

        all_iids = self.tree.get_children()
        row_tag = 'evenrow'
        if uid in self.uid_to_item_id:
            item_id = self.uid_to_item_id[uid]
            index = self.tree.index(item_id)
            row_tag = 'oddrow' if index % 2 == 0 else 'evenrow'
            self.tree.item(item_id, values=values, tags=(row_tag,))
        else:
            index = len(all_iids)
            row_tag = 'oddrow' if index % 2 == 0 else 'evenrow'
            item_id = self.tree.insert("", "end", values=values, tags=(row_tag,))
            self.uid_to_item_id[uid] = item_id

        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.see(item_id)
        
        if not silent:
            self.show_popup(user["name"], status)
            self.log_scan(uid, user["name"], user["room"], status, now_str)
            self._save_json(self.STATUS_FILE, self.uid_last_status)
            self._update_dashboard()

    def show_popup(self, name, status):
        if status == "IN":
            title, icon, bootstyle, action_text = "Welcome!", '✔️', SUCCESS, "Checked IN"
        else: # OUT
            title, icon, bootstyle, action_text = "Goodbye!", '✔️', DANGER, "Checked OUT"

        popup = ttk.Toplevel(title=title)
        
        container = ttk.Frame(popup, padding=25)
        container.pack(expand=True, fill=BOTH)

        ttk.Label(container, text=name, font=("Segoe UI", 20, "bold")).pack(pady=(0, 10))
        ttk.Label(container, text=f"{icon} {action_text}", font=("Segoe UI", 16), bootstyle=bootstyle).pack(pady=10)
        ttk.Label(container, text=time.strftime('%Y-%m-%d %H:%M:%S'), font=("Segoe UI", 10), bootstyle=SECONDARY).pack(pady=(10, 0))

        popup.update_idletasks()
        main_x, main_y = self.root.winfo_x(), self.root.winfo_y()
        main_w, main_h = self.root.winfo_width(), self.root.winfo_height()
        popup_w, popup_h = popup.winfo_width(), popup.winfo_height()
        center_x = main_x + (main_w // 2) - (popup_w // 2)
        center_y = main_y + (main_h // 2) - (popup_h // 2)
        popup.geometry(f"+{center_x}+{center_y}")
        
        popup.after(2500, popup.destroy)


    def register_uid(self, uid):
        reg_popup = ttk.Toplevel(title="Register New Card")
        reg_popup.geometry("350x250")

        form_frame = ttk.Frame(reg_popup, padding=20)
        form_frame.pack(expand=True, fill=BOTH)
        
        ttk.Label(form_frame, text=f"New Card UID: {uid}", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        name_entry = ttk.Entry(form_frame, bootstyle=PRIMARY)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        name_entry.focus_set()

        ttk.Label(form_frame, text="Room Number:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        room_entry = ttk.Entry(form_frame, bootstyle=PRIMARY)
        room_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def on_save():
            name, room = name_entry.get().strip(), room_entry.get().strip()
            if name and room:
                self.uid_info[uid] = {"name": name, "room": room}
                self._save_json(self.UID_DB_FILE, self.uid_info)
                self.uid_last_status[uid] = "OUT"
                self._save_json(self.STATUS_FILE, self.uid_last_status)
                Messagebox.show_info(title="Success", message=f"{name} has been successfully registered!")
                self._update_dashboard()
                reg_popup.destroy()
            else:
                Messagebox.show_warning(title="Missing Info", message="Please enter both a name and a room number.")
        
        ttk.Button(form_frame, text="Save", command=on_save, bootstyle=SUCCESS).grid(row=3, column=0, columnspan=2, pady=20)


    # --- THIS IS THE CORRECTED FUNCTION ---
    def reset_records(self):
        popup = ttk.Toplevel(self.root)
        popup.title("Admin Verification")
        popup.geometry("300x150")

        frame = ttk.Frame(popup, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Enter Admin Password:").pack(pady=5)

        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack(pady=5)
        password_entry.focus()

        def verify():
            if password_entry.get() != self.ADMIN_PASSWORD:
                Messagebox.show_error("Access Denied", "Incorrect password!")
                return

            popup.destroy()

            result = Messagebox.yesno(
                title="Confirm Reset",
                message="⚠️ Are you sure you want to clear all records?",
                alert=True
            )

            if result == "Yes":
                self.tree.delete(*self.tree.get_children())
                self.uid_last_status.clear()
                self.uid_to_item_id.clear()
                self._save_json(self.STATUS_FILE, self.uid_last_status)
                self._update_dashboard()
                Messagebox.show_info("Reset Complete", "All records cleared!")

        ttk.Button(frame, text="Verify", command=verify, bootstyle="success").pack(pady=10)
    
    
    def edit_names(self):
        def refresh_listbox():
            listbox.delete(0, tk.END)
            for uid, data in self.uid_info.items():
                listbox.insert(tk.END, f"{uid} : {data['name']} (Room {data['room']})")

        def update_selected():
            selected = listbox.curselection()
            if not selected:
                Messagebox.show_warning("No Selection", "Please select a record first.")
                return

            uid = list(self.uid_info.keys())[selected[0]]
            user = self.uid_info[uid]

            # Popup for editing
            edit_popup = ttk.Toplevel(edit_win)
            edit_popup.title("Edit Details")
            edit_popup.geometry("300x250")

            frame = ttk.Frame(edit_popup, padding=20)
            frame.pack(expand=True, fill="both")

            ttk.Label(frame, text=f"UID: {uid}").pack(pady=5)

            ttk.Label(frame, text="Name:").pack()
            name_entry = ttk.Entry(frame)
            name_entry.insert(0, user["name"])
            name_entry.pack(pady=5)

            ttk.Label(frame, text="Room:").pack()
            room_entry = ttk.Entry(frame)
            room_entry.insert(0, user["room"])
            room_entry.pack(pady=5)

            def save_changes():
                new_name = name_entry.get().strip()
                new_room = room_entry.get().strip()

                if not new_name or not new_room:
                    Messagebox.show_warning("Missing Info", "All fields are required.")
                    return

                # ✅ Update data
                self.uid_info[uid] = {"name": new_name, "room": new_room}
                self._save_json(self.UID_DB_FILE, self.uid_info)

                # ✅ 🔥 THIS LINE FIXES YOUR PROBLEM (instant UI update)
                self.update_table(uid, self.uid_last_status.get(uid, "OUT"), silent=True)

                refresh_listbox()
                self._update_dashboard()

                Messagebox.show_info("Updated", "Details updated successfully!")
                edit_popup.destroy()

            ttk.Button(frame, text="Save", command=save_changes, bootstyle="success").pack(pady=10)

        # Main window
        edit_win = ttk.Toplevel(self.root)
        edit_win.title("Edit UID Records")
        edit_win.geometry("400x300")

        listbox = tk.Listbox(edit_win, width=50)
        listbox.pack(pady=10, fill="both", expand=True)

        refresh_listbox()

        ttk.Button(edit_win, text="Edit Selected", command=update_selected, bootstyle="primary").pack(pady=5)

    def read_serial(self):
        while True:
            try:
                line = self.ser.readline().decode().strip()

                if line.startswith("UID:"):
                    uid = line.replace("UID:", "").strip()

                    current_time = time.time()

                    if (current_time - self.last_scan_time) > self.SCAN_COOLDOWN:
                        self.last_uid = uid
                        self.last_scan_time = current_time

                        if uid not in self.uid_info:
                            self.root.after(0, self.register_uid, uid)
                        else:
                            last_status = self.uid_last_status.get(uid, "OUT")
                            new_status = "IN" if last_status == "OUT" else "OUT"
                            self.uid_last_status[uid] = new_status
                            self.root.after(0, self.update_table, uid, new_status, False)

                    self.ser.reset_input_buffer()

            except Exception as e:
                    print(f"Serial read error: {e}")

            time.sleep(0.05)
               
    def read_wifi(self):
        while True:
            try:
                response = requests.get("http://192.168.4.1/uid", timeout=1)
    
                if response.status_code == 200:
                    line = response.text.strip()
    
                    # ✅ Empty response ignore karo (ESP often blank bhejta hai)
                    if not line:
                        time.sleep(0.2)
                        continue
                    
                    if line.startswith("UID:"):
                        uid = line.replace("UID:", "").strip()
    
                        current_time = time.time()
    
                        # ✅ Cooldown check
                        if (current_time - self.last_scan_time) > self.SCAN_COOLDOWN:
                            self.last_uid = uid
                            self.last_scan_time = current_time
    
                            if uid not in self.uid_info:
                                self.root.after(0, self.register_uid, uid)
                            else:
                                last_status = self.uid_last_status.get(uid, "OUT")
                                new_status = "IN" if last_status == "OUT" else "OUT"
                                self.uid_last_status[uid] = new_status
                                self.root.after(0, self.update_table, uid, new_status, False)
    
            except Exception as e:
                # ❌ spam avoid (optional: comment this line)
                # print(f"WiFi read error: {e}")
                pass
            
            time.sleep(0.3)    

    def find_arduino_port(self):
        ports = list_ports.comports()
        # 🔍 Debug: sab ports print karega
        print("\nAvailable Ports:")
        for port in ports:
            print(f"{port.device} - {port.description} (VID: {port.vid}, PID: {port.pid})")
        # 🔥 STEP 1: Try ESP8266 via WiFi first
        try:
            if self.check_wifi_device():
                print("✅ ESP8266 detected over WiFi")
                self.connection_mode = "wifi"
                return "WIFI"
        except Exception as e:
            print("WiFi check failed:", e)
        # 🔥 STEP 2: Try Serial (USB)
        for port in ports:
            desc = port.description.lower()
            if any(keyword in desc for keyword in [
                "cp210", "ch340", "usb serial", "silicon labs", "uart"
            ]):
                print(f"✅ Serial device detected: {port.device}")
                self.connection_mode = "serial"
                return port.device
        # 🔁 STEP 3: Fallback (first available port)
        if ports:
            print(f"⚠️ Fallback port used: {ports[0].device}")
            self.connection_mode = "serial"
            return ports[0].device
        # ❌ No device found
        print("❌ No device found (WiFi or Serial)")
        self.connection_mode = None
        return None
    def check_wifi_device(self):
        try:
            response = requests.get("http://192.168.4.1/uid", timeout=1)
            return response.status_code == 200
        except:
            return False
    def _start_serial_thread(self):
        try:
            # 🔥 Step 1: Try WiFi
            if self.check_wifi_device():
                print("Connected via WiFi")
    
                # Start WiFi reading thread
                wifi_thread = threading.Thread(target=self.read_wifi, daemon=True)
                wifi_thread.start()
                return
    
            # 🔁 Step 2: fallback to Serial
            print("WiFi not found, switching to Serial...")
    
            port = self.find_arduino_port()
    
            if port is None:
                Messagebox.show_error(
                    title="Connection Error",
                    message="No device found (WiFi or Serial)!"
                )
                return
    
            print(f"Connected via Serial: {port}")
    
            if port == "WIFI":
                print("📡 Using WiFi mode")
                wifi_thread = threading.Thread(target=self.read_wifi, daemon=True)
                wifi_thread.start()
                return
            self.ser = serial.Serial(port, 115200, timeout=1)
    
            serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            serial_thread.start()
    
        except Exception as e:
            Messagebox.show_error(
                title="Connection Error",
                message=f"Connection failed: {e}"
            )
    
    def _restore_previous_state(self):
        for uid, status in self.uid_last_status.items():
            self.update_table(uid, status, silent=True)

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = HostelApp(root)
    root.mainloop()
