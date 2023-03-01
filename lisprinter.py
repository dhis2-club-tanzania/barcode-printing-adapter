import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QListWidget,QTableWidget, QTableWidgetItem, QLabel, QMainWindow,QMenu,QToolBar,QAction,QMessageBox
import os
import cups
import sqlite3

printers = []
printers_options = []
printers_keyed_by_names = {}
default_printer = ""
default_printer_name = ""

cups_conn = cups.Connection()
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("LIS Printing Adapter")
        self.resize(700, 500)
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
            print(printer_names[key]["printer-make-and-model"])
            printer_name = key
            printers.append({
                "name": printer_name,
                "makeAndModel":printer_names[key]["printer-make-and-model"]
            })
            printers_options.append(key)
            printers_keyed_by_names[printer_names[key]['printer-uri-supported']] = printer_names[key]
            if 'recommended' in printer_names[key]["printer-make-and-model"]:
                default_printer = printer_names[key]['printer-uri-supported']

        table = QTableWidget(self.centralWidget)
        table.setRowCount(len(printers))
        table.setColumnCount(len(printers[0]))
        table.setHorizontalHeaderLabels(["Name","Make & Model"])
        table.setColumnWidth(0, 250)
        table.setColumnWidth(1, 250)
        table.setColumnWidth(2, 230)
        for i, (item) in enumerate(printers):
            tbdata_name = QTableWidgetItem(item["name"])
            tbdata_model = QTableWidgetItem(item["makeAndModel"])
            table.setItem(i, 0, tbdata_name)
            table.setItem(i, 1, tbdata_model)

        table.show()


    def exit(self):
        self.centralWidget.setText("<b>Printers > Exit...</b> clicked")

    def helpContent(self):
        self.centralWidget.setText("<b>Help > Help Content...</b> clicked")

    def about(self):
        self.centralWidget.setText("<b>Help > About...</b> clicked")

   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())