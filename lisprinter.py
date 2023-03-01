import sys
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import QApplication,QHeaderView,QPushButton,QTableWidget, QTableWidgetItem, QLabel, QMainWindow,QMenu,QToolBar,QAction,QMessageBox,QDialog,QVBoxLayout,QLineEdit,QFormLayout,QGroupBox,QPlainTextEdit
import os
import cups
import sqlite3
import socket

stored_printers =[]
stored_printers_names ={}
printers = []
printers_options = []
printers_keyed_by_names = {}
default_printer = ""
default_printer_name = ""

conn = cups.Connection()

cups_conn = cups.Connection()

sqlite_conn = sqlite3.connect('lisprinterdb.db')

cursor = sqlite_conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS printer (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, description TEXT, type TEXT, uri TEXT, location TEXT,info TEXT,make_and_model TEXT, shared BOOLEAN, current_date TEXT)''')
cursor.execute("SELECT * FROM printer")

printers_list =  cursor.fetchall()

for printer in printers_list:
    stored_printers.append(printer)
    stored_printers_names[printer[1]] = printer

print(stored_printers)
sqlite_conn.commit()
cursor.close()
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("LIS Printing Adapter")
        self.resize(800, 500)
        self.centralWidget = QLabel("Welcome")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        self.setCentralWidget(self.centralWidget)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        printersMenu = QMenu("&Printers", self)
        menuBar.addMenu(printersMenu)
        printersMenu.addAction(self.newAction)
        printersMenu.addAction(self.exitAction)
        # Creating menus using a title
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)
    
    def _createToolBars(self):
        # Using a title
        fileToolBar = self.addToolBar("Printers")
        # Using a QToolBar object and a toolbar area
        helpToolBar = QToolBar("Help", self)
        self.addToolBar(Qt.LeftToolBarArea, helpToolBar)

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.exitAction = QAction("&Exit", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _connectActions(self):
        # Connect File actions
        self.newAction.triggered.connect(self.newPrinter)
        self.exitAction.triggered.connect(self.close)
        # Connect Help actions
        self.helpContentAction.triggered.connect(self.helpContent)
        self.aboutAction.triggered.connect(self.about)

    def newPrinter(self):
        # self.centralWidget.setText("<b>Printers > New</b> clicked")
        printer_names = cups_conn.getPrinters()
        printers= []
        for key in printer_names.keys():
            printer_name = key
            printers.append({
                "name": printer_name,
                "makeAndModel":printer_names[key]["printer-make-and-model"],
                "shared": printer_names[key]["printer-is-shared"],
                "state": printer_names[key]["printer-state"],
                "stateMessage": printer_names[key]["printer-state-message"],
                "stateReasons": printer_names[key]["printer-state-reasons"],
                "printerType": printer_names[key]["printer-type"],
                "uriSupported": printer_names[key]["printer-uri-supported"],
                "location": printer_names[key]["printer-location"],
                "printerInfo": printer_names[key]["printer-info"],
                "deviceUri": printer_names[key]["device-uri"]
            })
            printers_options.append(key)
            printers_keyed_by_names[printer_names[key]['printer-uri-supported']] = printer_names[key]
            if 'recommended' in printer_names[key]["printer-make-and-model"]:
                default_printer = printer_names[key]['printer-uri-supported']

        table = QTableWidget(self.centralWidget)
        table.resize(780,400)
        table.setRowCount(len(printers))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name","Make & Model", "Action"])
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 150)
        table.setColumnWidth(2, 150)
        for i, (item) in enumerate(printers):
            tbdata_name = QTableWidgetItem(item["name"])
            tbdata_model = QTableWidgetItem(item["makeAndModel"])
            table.setCornerButtonEnabled(True)
            btn = QPushButton("+")
            btn.move(30,30)
            if item["name"] in stored_printers_names:
                btn.setEnabled(False)
            btn.clicked.connect(lambda checked, row=item: self.buttonClicked(row))
            btn_settings = QPushButton("Set")
            if item["name"] not in stored_printers_names:
                btn_settings.setEnabled(False)
            btn_settings.move(30,30)

            dialog = QDialog()
            dialog.setWindowTitle(item["name"] + " settings")
            dialog.resize(400,200)
            dialog_layout = QVBoxLayout()
            p_width = QLineEdit()
            p_height = QLineEdit()
            p_size = QLineEdit()
            dialog_layout.addWidget(p_width)
            dialog_layout.addWidget(p_height)
            dialog_layout.addWidget(p_size)
            dialog_layout.addWidget(QPushButton('Close', clicked=dialog.accept))
            dialog.setLayout(dialog_layout)

            btn_settings.clicked.connect(lambda checked, row=item,dialog=dialog: self.setButtonClicked(row,dialog))
            btn_test = QPushButton("Test")
            btn_test.move(30,30)

            dialog_test = QDialog()
            dialog_test.setWindowTitle(item["name"] + " Testing")
            dialog_test.resize(400,200)
            dialog_test_layout = QVBoxLayout()
            sample_data = QPlainTextEdit()
            sample_data.height = '50'
            dialog_test_layout.addWidget(sample_data)
            print_button = QPushButton('Print')
            print_button.clicked.connect(lambda checked, row=item,textInput=sample_data: self.on_button_clicked(row,textInput))
            dialog_test_layout.addWidget(print_button)
            dialog_test_layout.addWidget(QPushButton('Close', clicked=dialog_test.accept))
            dialog_test.setLayout(dialog_test_layout)
            btn_test.clicked.connect(lambda checked, row=item,dialog=dialog_test: self.testButtonClicked(row,dialog_test))
            
            table.setItem(i, 0, tbdata_name)
            table.setItem(i, 1, tbdata_model)
            table.setCellWidget(i,2, btn)
            table.setCellWidget(i,3, btn_settings)
            table.setCellWidget(i,4, btn_test)
            if item["name"] in stored_printers_names:
                for col in range(2):
                    table.item(i,col).setBackground(QColor(48,164,213))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.show()

    def on_button_clicked(self, item, textInput): 
        text = textInput.toPlainText()
        printer = item["name"]
        print(printer)
        zpl_data = """
        ^XA
        ^FO50,50
        ^A0N,50,50
        ^FDHello, AM testing!^FS
        ^XZ
        """
        zpl_bytes_data = zpl_data.encode('utf-8')
        print(zpl_bytes_data)
        zpl_job_id = conn.createJob(printer, "ZPL print job", {"document-format": "application/zpl"})
        conn.printFile(printer, zpl_job_id, "", zpl_bytes_data)
        # job_id = conn.printFile(item["name"], "/home/mwakyusa/Desktop/test_printer.txt", "Print Job", {})
        
    def exit(self):
        self.centralWidget.setText("<b>Printers > Exit...</b> clicked")

    def helpContent(self):
        self.centralWidget.setText("<b>Help > Help Content...</b> clicked")

    def about(self):
        self.centralWidget.setText("<b>Help > About...</b> clicked")

    def sleep5sec(self):
        self.targetBtn.setEnabled(False)
        QTimer.singleShot(5000, lambda: self.targetBtn.setDisabled(False))

    def setButtonClicked(self, item, dialog):
        dialog.show()
    
    def testButtonClicked(self, item, dialog):        
        dialog.show()

    def buttonClicked(self, item):
        name =""
        code = ""
        description = ""
        type = ""
        uri = ""
        location =""
        info =""
        make_and_model =""
        shared =""
        current_date =""
        if "name" in item:
            name = item["name"]
        if "code" in item:
            code = item["code"]
        if "description" in item:
            description = item["description"]
        if "type" in item:
            type = item["type"]
        if "uri" in item:
            uri = item["uri"]
        if "location" in item:
            location = item["location"]
        if "info" in item:
            info = item["info"]
        if "make_and_model" in item:
            make_and_model = item["make_and_model"]
        if "shared" in item:
            shared = item["shared"]
        if "current_date" in item:
            current_date = item["current_date"]

        cursor = sqlite_conn.cursor()
        cursor.execute("INSERT INTO printer (name, code, description, type, uri, location,info,make_and_model,shared,current_date) VALUES (?, ?,?,?,?,?,?,?,?,?)", (name, code, description,type,uri,location,info, make_and_model, shared, current_date))
   
        cursor.execute("SELECT * FROM printer")

        printers_list =  cursor.fetchall()

        for printer in printers_list:
            stored_printers.append(printer)

        print(stored_printers)
        sqlite_conn.commit()
        cursor.close()

# TODO: Consider putting other classes on separate file
class PrinterSettingsDialog(QDialog):
    
    def test():
        print("TESTING")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

# name TEXT, code TEXT, description TEXT, type TEXT, uri TEXT, location TEXT,info TEXT,make_and_model TEXT, shared BOOLEAN, current_date TEXT