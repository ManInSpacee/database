import sys
from PyQt5 import QtWidgets, uic
from db import create_schema_and_tables
from ui_modal import open_modal
from ui_table import show_table_window

app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("../ui/main.ui")
window.setWindowTitle("PostgreSQL + Qt5")


window.mainButton_createTable.clicked.connect(lambda: create_schema_and_tables(window))
window.mainButton_insertData.clicked.connect(lambda: open_modal(window))
window.mainButton_showData.clicked.connect(lambda: show_table_window(window))

window.show()
sys.exit(app.exec_())
