import logging
import sys
from PyQt5 import QtWidgets, uic
from db import create_schema_and_tables
from insert import open_modal
from show import show_table_window

app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("../ui/main.ui")
window.setWindowTitle("PostgreSQL + Qt5")

logging.info("Started Program. . .")
window.mainButton_createTable.clicked.connect(lambda: create_schema_and_tables(window))
window.mainButton_insertData.clicked.connect(lambda: open_modal(window))
window.mainButton_showData.clicked.connect(lambda: show_table_window(window))

window.show()
sys.exit(app.exec_())
