from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import os
import cups
import sqlite3

window = Tk()

#Setting the size of the window
window.geometry('800x700')
window.title("LIS Printing Adapter")

printers = []
printers_options = []
printers_keyed_by_names = {}

# Create a connection to the CUPS server
conn = cups.Connection()

# Get list of printer names
printer_names = conn.getPrinters()
default_printer = ""
default_printer_name = ""
sqlite_conn = sqlite3.connect('lisprinterdb.db')

cursor = sqlite_conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS printer (id INTEGER PRIMARY KEY, name TEXT, code TEXT, description TEXT, type TEXT, uri TEXT, location TEXT,info TEXT,make_and_model TEXT, shared BOOLEAN, current_date TEXT)''')

for key in printer_names.keys():
    default_printer_name = key
    printers.append(printer_names[key])
    printers_options.append(key)
    printers_keyed_by_names[printer_names[key]['printer-uri-supported']] = printer_names[key]
    if 'recommended' in printer_names[key]["printer-make-and-model"]:
        default_printer = printer_names[key]['printer-uri-supported']

# print(printers)
print(default_printer_name)
selected_value = StringVar()
selected_value.set( default_printer )
drop = ttk.OptionMenu(window , selected_value , *printers_options )
default_printer_name = selected_value.get()
# ZTC-GC420t-EPL
# HP-HP-LaserJet-Pro-M428-M429

drop.pack()

# print(printer_names)

def testPort():
    default_printer = selected_value.get()
    print(default_printer)
    if default_printer:
        job_id = conn.printFile(default_printer, "/home/mwakyusa/Desktop/test_printer.txt", "Print Job", {})
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print("DEVICE")
        print(p.device_path)
        print(p.name)
        print(p.device)
        ser = serial.Serial(p.device)  # open serial port
        print(ser)
    print(len(ports), 'ports found')
    os.system(default_printer_name + " /home/mwakyusa/Desktop/test_printer.txt")
    messagebox.showinfo("Message","You are testing printer connection")

btn = ttk.Button(window, text="Print", width=20, command=testPort)
btn.place(x=300,y=300)
btn.pack(pady= 20)

window.mainloop()