from PyQt5 import QtWidgets, QtGui
from db import get_connection
import logging

def show_table_window(window):
    table_dialog = QtWidgets.QWidget()
    table_dialog.setWindowTitle("Таблица пользователей")
    table_dialog.setGeometry(100, 100, 800, 450)

    # Поле фильтра
    filter_edit = QtWidgets.QLineEdit(table_dialog)
    filter_edit.setPlaceholderText("Введите текст для фильтрации...")
    filter_edit.setGeometry(10, 10, 780, 30)

    # Таблица
    table_view = QtWidgets.QTableView(table_dialog)
    table_view.setGeometry(10, 50, 780, 390)

    # Функция загрузки данных
    def load_data():
        filter_text = filter_edit.text().strip()
        conn = get_connection()
        cursor = conn.cursor()
        if filter_text:
            cursor.execute("SELECT * FROM users WHERE attack_type::text ILIKE %s", (f"%{filter_text}%",))
        else:
            cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(columns)
        for row in rows:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        table_view.setModel(model)
        table_view.setSortingEnabled(True)
        table_view.resizeColumnsToContents()
        cursor.close()
        conn.close()
        logging.info(f"Table loaded with filter='{filter_text}'")


    filter_edit.textChanged.connect(lambda text: load_data())

    load_data()
    table_dialog.show()
    window.table_dialog_window = table_dialog
