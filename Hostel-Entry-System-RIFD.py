import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import serial
import time
import threading
import mysql.connector
import csv

class HostelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hostel Entry Monitoring System")
        self.root.geometry("1000x700")

        self.SCAN_LOG_FILE = 'entry_history.txt'

        self.last_uid = None
        self.last_scan_time = 0
        self.SCAN_COOLDOWN = 5
        self.uid_to_item_id = {}

        #  MYSQL CONNECTION
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="core#85208520", 
            database="hostel_entry"
        )
        self.cursor = self.conn.cursor()

        self._create_tables()
        self._load_data()

        self._create_widgets()
        self._restore_previous_state()
        self._update_dashboard()

        self._start_serial_thread()

    # ================= DATABASE =================

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            uid VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            room VARCHAR(20)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS status (
            uid VARCHAR(50) PRIMARY KEY,
            state VARCHAR(10),
            time DATETIME,
            FOREIGN KEY (uid) REFERENCES residents(uid)
        )
        """)
        self.conn.commit()

    def _load_data(self):
        self.cursor.execute("SELECT uid,name,room FROM residents")
        self.uid_info = {u:{"name":n,"room":r} for u,n,r in self.cursor.fetchall()}

        self.cursor.execute("SELECT uid,state FROM status")
        self.uid_last_status = dict(self.cursor.fetchall())

    # ================= UI =================

    def _create_widgets(self):
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill=X)
        ttk.Label(header,text="Hostel Entry Monitoring System",
                  font=("Segoe UI",24,"bold"),
                  bootstyle=PRIMARY).pack()

        dash = ttk.Frame(self.root,padding=(20,10))
        dash.pack(fill=X)

        self.residents_in_label = ttk.Label(dash,font=("Segoe UI",14,"bold"),bootstyle=SUCCESS)
        self.residents_in_label.pack(side=LEFT,padx=20)

        self.total_residents_label = ttk.Label(dash,font=("Segoe UI",14),bootstyle=INFO)
        self.total_residents_label.pack(side=LEFT,padx=20)

        table_frame = ttk.Frame(self.root,padding=20)
        table_frame.pack(expand=True,fill=BOTH)

        cols=("UID","Name","Room","Status","Time")
        self.tree=ttk.Treeview(table_frame,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c)
            self.tree.column(c,anchor=CENTER,width=150)
        self.tree.pack(side=LEFT,expand=True,fill=BOTH)

        scrollbar=ttk.Scrollbar(table_frame,command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT,fill=Y)

        footer=ttk.Frame(self.root,padding=20)
        footer.pack(fill=X)

        ttk.Button(footer,text="Reset Records",
                   command=self.reset_records,
                   bootstyle=(DANGER,OUTLINE),
                   width=20).pack(pady=5)

        ttk.Button(footer,text="Download Status CSV",
                   command=self.export_csv,
                   bootstyle=(INFO,OUTLINE),
                   width=20).pack(pady=5)
        
        # ttk.Button(footer,text="Refresh Data",
        #         command=self.refresh_data,
        #         bootstyle=(PRIMARY, OUTLINE),
        #         width=20).pack(pady=5)

    # ================= CORE =================

    def _update_dashboard(self):
        inside=list(self.uid_last_status.values()).count("IN")
        total=len(self.uid_info)
        self.residents_in_label.config(text=f"Residents In: {inside}")
        self.total_residents_label.config(text=f"Total Registered: {total}")

    def log_scan(self,uid,name,room,status,ts):
        with open(self.SCAN_LOG_FILE,"a") as f:
            f.write(f"{ts} | {uid} | {name} | {room} | {status}\n")

    def update_table(self,uid,status,silent=False):
        now=time.strftime('%Y-%m-%d %H:%M:%S')
        user=self.uid_info.get(uid,{"name":"Unknown","room":"N/A"})
        values=(uid,user["name"],user["room"],status,now)

        if uid in self.uid_to_item_id:
            iid=self.uid_to_item_id[uid]
            self.tree.item(iid,values=values)
        else:
            iid=self.tree.insert("", "end", values=values)
            self.uid_to_item_id[uid]=iid

        if not silent:
            self.log_scan(uid,user["name"],user["room"],status,now)
            self._update_dashboard()

    def register_uid(self,uid):
        popup=ttk.Toplevel(self.root)
        popup.title("Register Card")

        frame=ttk.Frame(popup,padding=20)
        frame.pack()

        ttk.Label(frame,text=f"UID: {uid}").grid(row=0,columnspan=2,pady=10)

        ttk.Label(frame,text="Name").grid(row=1,column=0)
        name=ttk.Entry(frame)
        name.grid(row=1,column=1)

        ttk.Label(frame,text="Room").grid(row=2,column=0)
        room=ttk.Entry(frame)
        room.grid(row=2,column=1)

        def save():
            n,r=name.get(),room.get()
            if n and r:
                self.cursor.execute(
                    "INSERT INTO residents VALUES (%s,%s,%s)",
                    (uid,n,r)
                )
                self.cursor.execute(
                    "INSERT INTO status VALUES (%s,%s,%s)",
                    (uid,"OUT",None)
                )
                self.conn.commit()

                self.uid_info[uid]={"name":n,"room":r}
                self.uid_last_status[uid]="OUT"
                popup.destroy()
                self._update_dashboard()

        ttk.Button(frame,text="Save",command=save,bootstyle=SUCCESS)\
            .grid(row=3,columnspan=2,pady=10)

    def reset_records(self):
        if messagebox.askyesno("Confirm Reset", "Clear all status records?"):

            self.tree.delete(*self.tree.get_children())
            self.uid_to_item_id.clear()   

            self.cursor.execute("""
            SET SQL_SAFE_UPDATES = 0;
            DELETE FROM status;
            """)

        for uid in self.uid_last_status:
            self.uid_last_status[uid] = "OUT"

            self.conn.commit()
        self._update_dashboard()


    def export_csv(self):
        self.cursor.execute("""
        SELECT r.uid,r.name,r.room,s.state,s.time
        FROM residents r
        JOIN status s ON r.uid=s.uid
        """)
        rows=self.cursor.fetchall()

        with open("status_export.csv","w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["UID","Name","Room","Status","Time"])
            writer.writerows(rows)

        Messagebox.show_info("Done","CSV saved as status_export.csv")
    
    # def refresh_data(self):
    #     # Reload data from database
    #     self._load_data()

    #     # Clear table
    #     self.tree.delete(*self.tree.get_children())
    #     self.uid_to_item_id.clear()

    #     # Reload table from DB
    #     for uid, status in self.uid_last_status.items():
    #         self.update_table(uid, status, silent=True)

    #     # Update dashboard
    #     self._update_dashboard()

    # Messagebox.show_info("Refreshed", "Data updated from database.")    

    # ================= SERIAL =================

    def read_serial(self):
        while True:
            try:
                line=self.ser.readline().decode().strip()
                if line.startswith("UID:"):
                    uid=line.replace("UID:","").strip()
                    now=time.time()

                    if uid!=self.last_uid or now-self.last_scan_time>self.SCAN_COOLDOWN:
                        self.last_uid=uid
                        self.last_scan_time=now

                        if uid not in self.uid_info:
                            self.root.after(0,self.register_uid,uid)
                        else:
                            last=self.uid_last_status.get(uid,"OUT")
                            new="IN" if last=="OUT" else "OUT"
                            self.uid_last_status[uid]=new

                            ts=time.strftime('%Y-%m-%d %H:%M:%S')
                            self.cursor.execute("""
                                INSERT INTO status (uid,state,time)
                                VALUES (%s,%s,%s)
                                ON DUPLICATE KEY UPDATE
                                state=VALUES(state),
                                time=VALUES(time)
                            """,(uid,new,ts))
                            self.conn.commit()

                            self.root.after(0,self.update_table,uid,new)

            except:
                pass
            time.sleep(0.1)

    def _start_serial_thread(self):
        try:
            self.ser=serial.Serial('COM16',115200,timeout=1)
            threading.Thread(target=self.read_serial,daemon=True).start()
        except:
            Messagebox.show_error("Error","RFID reader not connected")

    def _restore_previous_state(self):
        for uid,status in self.uid_last_status.items():
            self.update_table(uid,status,True)

if __name__ == "__main__":
    root=ttk.Window(themename="litera")
    app=HostelApp(root)
    root.mainloop()