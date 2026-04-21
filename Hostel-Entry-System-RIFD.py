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
        # The correct function name is 'askyesno' (all lowercase)
        result = Messagebox.askyesno(
            title="Confirm Reset",
            message="⚠️ Are you sure you want to clear all status records? This action cannot be undone.",
            alert=True
        )
        
        # The function returns the string "Yes" or "No"
        if result == "Yes":
            self.tree.delete(*self.tree.get_children())
            self.uid_last_status.clear()
            self.uid_to_item_id.clear()
            self._save_json(self.STATUS_FILE, self.uid_last_status)
            self._update_dashboard()
            Messagebox.showinfo("Reset Complete", "All status records have been cleared!")

    def read_serial(self):
        while True:
            try:
                line = self.ser.readline().decode().strip()
                if line.startswith("UID:"):
                    uid = line.replace("UID:", "").strip()

                    current_time = time.time()
                    if uid != self.last_uid or (current_time - self.last_scan_time) > self.SCAN_COOLDOWN:
                        self.last_uid, self.last_scan_time = uid, current_time

                        if uid not in self.uid_info:
                            self.root.after(0, self.register_uid, uid)
                        else:
                            last_status = self.uid_last_status.get(uid, "OUT")
                            new_status = "IN" if last_status == "OUT" else "OUT"
                            self.uid_last_status[uid] = new_status
                            self.root.after(0, self.update_table, uid, new_status, False)

            except Exception as e:
                print(f"Serial read error: {e}")
            time.sleep(0.1)

    def _start_serial_thread(self):
        try:
            self.ser = serial.Serial('COM7', 115200, timeout=1)
            serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            serial_thread.start()
        except serial.SerialException as e:
            Messagebox.show_error(title="Connection Error", 
                                  message=f"Could not connect to RFID reader on COM7.\n\nPlease check the connection and restart the application.\nError: {e}")

    def _restore_previous_state(self):
        for uid, status in self.uid_last_status.items():
            self.update_table(uid, status, silent=True)

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = HostelApp(root)
    root.mainloop()
