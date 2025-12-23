#-----------------------------NOTE------------------------------------
# Create exe by the below command
# pyinstaller --noconsole --onefile --icon=myicon.ico Relay_Control.py
#---------------------------------------------------------------------

import tkinter as tk
from tkinter import messagebox
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS, serialutil
from serial.tools import list_ports
import os

# Relay command bytes
_RELAY_LOW = [
    b'\x55\xAA\x01\x02\x00\x01\x00\x03',
    b'\x55\xAA\x01\x02\x00\x02\x00\x04',
    b'\x55\xAA\x01\x02\x00\x03\x00\x05',
    b'\x55\xAA\x01\x02\x00\x04\x00\x06',
    b'\x55\xAA\x01\x02\x00\x05\x00\x07',
    b'\x55\xAA\x01\x02\x00\x06\x00\x08',
    b'\x55\xAA\x01\x02\x00\x07\x00\x09',
    b'\x55\xAA\x01\x02\x00\x08\x00\x0A'
]

_RELAY_HIGH = [
    b'\x55\xAA\x01\x02\x00\x01\x01\x04',
    b'\x55\xAA\x01\x02\x00\x02\x01\x05',
    b'\x55\xAA\x01\x02\x00\x03\x01\x06',
    b'\x55\xAA\x01\x02\x00\x04\x01\x07',
    b'\x55\xAA\x01\x02\x00\x05\x01\x08',
    b'\x55\xAA\x01\x02\x00\x06\x01\x09',
    b'\x55\xAA\x01\x02\x00\x07\x01\x0A',
    b'\x55\xAA\x01\x02\x00\x08\x01\x0B'
]

_CMD_SUCCESS = b'U\xaa\x01\x01\xff\x00\x00'

def get_relay_serial_port(vendor="USB Serial Device"):
    ports = list_ports.comports()
    for port in ports:
        if vendor in port.description:
            return port.device
    return None

def push_cmd(cmd):
    relay_serial_port = get_relay_serial_port()
    if relay_serial_port is None:
        messagebox.showerror("Serial ERROR", "Relay USB port not found")
        return False
    try:
        rly_serial = Serial(port=relay_serial_port, baudrate=115200,
                            parity=PARITY_NONE, stopbits=STOPBITS_ONE,
                            bytesize=EIGHTBITS, timeout=0.5)
    except serialutil.SerialException:
        messagebox.showerror("Serial ERROR", "Failed to open serial port")
        return False

    rly_serial.write(cmd)
    rsp = rly_serial.readline()
    rly_serial.close()

    if rsp == _CMD_SUCCESS:
        return True

    messagebox.showerror("Serial ERROR", "Command failed or wrong response")
    return False

def switch_relay(relay_num, state):
    if 1 <= relay_num <= 8:
        cmd = _RELAY_HIGH[relay_num - 1] if state == "HIGH" else _RELAY_LOW[relay_num - 1]
        return push_cmd(cmd)
    else:
        messagebox.showerror("Error", f"Invalid relay number: {relay_num}")
        return False

class RelayControlApp:
    def __init__(self, root):
        self.root = root
        root.title("DFRobot 8-Channel Relay Control")

        # Auto-size window
        root.update_idletasks()
        root.minsize(root.winfo_reqwidth() + 20, root.winfo_reqheight() + 20)

        self.description_entries = []
        self.status_circles = []
        self.toggle_buttons = []

        self.relay_states = self.load_relay_states()
        saved_descriptions = self.load_saved_descriptions()

        for i in range(8):
            frame = tk.Frame(root)
            frame.pack(pady=5, padx=5, fill="x")

            relay_label = tk.Label(frame, text=f"Relay {i+1}", width=10, anchor="w")
            relay_label.pack(side="left", padx=5)

            # Toggle button
            state = self.relay_states[i]
            toggle_text = "Turn OFF" if state else "Turn ON"
            toggle_btn = tk.Button(frame, text=toggle_text, width=8,
                                   bg="gray", fg="white",
                                   command=lambda r=i+1: self.toggle_relay(r))
            toggle_btn.pack(side="left", padx=5)
            self.toggle_buttons.append(toggle_btn)

            # Status circle
            canvas = tk.Canvas(frame, width=25, height=25, highlightthickness=0)
            circle = canvas.create_oval(2, 2, 23, 23, fill="green" if state else "red")
            canvas.pack(side="left", padx=10)
            self.status_circles.append((canvas, circle))

            # Description entry
            desc_entry = tk.Entry(frame)
            desc_entry.insert(0, saved_descriptions.get(i + 1, ""))
            desc_entry.pack(side="left", expand=True, fill="x", padx=5)
            self.description_entries.append(desc_entry)

            # Save & Clear buttons in same row
            save_btn = tk.Button(frame, text="Save", width=6,
                                 command=lambda idx=i: self.save_single_description(idx))
            save_btn.pack(side="left", padx=2)

            clear_btn = tk.Button(frame, text="Clear", width=6,
                                  command=lambda idx=i: self.clear_single_description(idx))
            clear_btn.pack(side="left", padx=2)

        # ALL ON / ALL OFF buttons
        action_frame = tk.Frame(root)
        action_frame.pack(pady=15)
        tk.Button(action_frame, text="ALL ON", bg="green", fg="white", font=("Helvetica", 12),
                  command=self.turn_all_on).pack(side="left", padx=10)
        tk.Button(action_frame, text="ALL OFF", bg="red", fg="white", font=("Helvetica", 12),
                  command=self.turn_all_off).pack(side="left", padx=10)

    def update_status_indicator(self, relay_num, state):
        canvas, circle = self.status_circles[relay_num - 1]
        color = "green" if state == "HIGH" else "red"
        canvas.itemconfig(circle, fill=color)
        self.relay_states[relay_num - 1] = (state == "HIGH")
        self.save_relay_states()
        # Update toggle button text
        new_text = "Turn OFF" if state == "HIGH" else "Turn ON"
        self.toggle_buttons[relay_num - 1].config(text=new_text)

    def toggle_relay(self, relay_num):
        i = relay_num - 1
        new_state = "LOW" if self.relay_states[i] else "HIGH"
        success = switch_relay(relay_num, new_state)
        if success:
            self.update_status_indicator(relay_num, new_state)
        else:
            messagebox.showwarning("Error", f"Failed to toggle Relay {relay_num}")

    def turn_all_on(self):
        for i in range(8):
            if switch_relay(i + 1, "HIGH"):
                self.update_status_indicator(i + 1, "HIGH")
                self.root.update()

    def turn_all_off(self):
        for i in range(8):
            if switch_relay(i + 1, "LOW"):
                self.update_status_indicator(i + 1, "LOW")
                self.root.update()

    def clear_descriptions(self):
        for entry in self.description_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "  ")

    def save_descriptions(self):
        try:
            with open("relay_descriptions.txt", "w", encoding="utf-8") as file:
                for i, entry in enumerate(self.description_entries):
                    desc = entry.get().strip()
                    file.write(f"Relay {i+1}: {desc}\n")
            messagebox.showinfo("Saved", "Descriptions saved to relay_descriptions.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def save_single_description(self, idx):
        try:
            desc = self.description_entries[idx].get().strip()
            descriptions = self.load_saved_descriptions()
            descriptions[idx + 1] = desc
            with open("relay_descriptions.txt", "w", encoding="utf-8") as file:
                for i in range(8):
                    d = descriptions.get(i + 1, "")
                    file.write(f"Relay {i+1}: {d}\n")
            messagebox.showinfo("Saved", f"Description for Relay {idx+1} saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save description: {str(e)}")

    def clear_single_description(self, idx):
        self.description_entries[idx].delete(0, tk.END)
        self.description_entries[idx].insert(0, "")

    def load_saved_descriptions(self):
        descriptions = {}
        try:
            if os.path.exists("relay_descriptions.txt"):
                with open("relay_descriptions.txt", "r", encoding="utf-8") as file:
                    for line in file:
                        if line.strip():
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                relay_num = int(parts[0].strip().replace("Relay", ""))
                                descriptions[relay_num] = parts[1].strip()
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load saved descriptions:\n{e}")
        return descriptions

    def save_relay_states(self):
        try:
            with open("relay_states.txt", "w", encoding="utf-8") as file:
                for state in self.relay_states:
                    file.write(f"{int(state)}\n")
        except Exception as e:
            print(f"Error saving relay states: {e}")

    def load_relay_states(self):
        states = [False] * 8
        try:
            if os.path.exists("relay_states.txt"):
                with open("relay_states.txt", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    for i in range(min(8, len(lines))):
                        states[i] = bool(int(lines[i].strip()))
        except Exception as e:
            print(f"Error loading relay states: {e}")
        return states

def main():
    root = tk.Tk()
    app = RelayControlApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
