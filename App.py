import sys
from PyQt5 import QtWidgets, uic
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="postgres",       # имя базы
        user="postgres",         # ваш пользователь
        password="klim",         # ваш пароль
        host="localhost",        # или другой хост
        port="5432"              # порт PostgreSQL
    )


def create_schema_and_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                attack_type VARCHAR NOT NULL,
                target_ip VARCHAR NOT NULL,
                start_time TIMESTAMP NOT NULL,
                duration_sec INT NOT NULL,
                peak_dbs BIGINT NOT NULL,
                source_count INT NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        QtWidgets.QMessageBox.information(window, "Успех", "Таблица создана!")
    except Exception as e:
        QtWidgets.QMessageBox.critical(window, "Ошибка", str(e))

def open_modal():
    dialog = QtWidgets.QDialog(window)
    dialog.setWindowTitle("Добавить запись")
    dialog.setModal(True)
    dialog.setFixedSize(400, 400)

    # Поля для ввода
    attack_type_edit = QtWidgets.QLineEdit(dialog)
    attack_type_edit.setPlaceholderText("Attack Type")
    attack_type_edit.setGeometry(100, 20, 200, 30)

    target_ip_edit = QtWidgets.QLineEdit(dialog)
    target_ip_edit.setPlaceholderText("Target IP")
    target_ip_edit.setGeometry(100, 60, 200, 30)

    start_time_edit = QtWidgets.QLineEdit(dialog)
    start_time_edit.setPlaceholderText("Start Time (YYYY-MM-DD HH:MM:SS)")
    start_time_edit.setGeometry(100, 100, 200, 30)

    duration_sec_edit = QtWidgets.QLineEdit(dialog)
    duration_sec_edit.setPlaceholderText("Duration (sec)")
    duration_sec_edit.setGeometry(100, 140, 200, 30)

    peak_dbs_edit = QtWidgets.QLineEdit(dialog)
    peak_dbs_edit.setPlaceholderText("Peak DBS")
    peak_dbs_edit.setGeometry(100, 180, 200, 30)

    source_count_edit = QtWidgets.QLineEdit(dialog)
    source_count_edit.setPlaceholderText("Source Count")
    source_count_edit.setGeometry(100, 220, 200, 30)

    # Кнопка вставки
    btn_insert = QtWidgets.QPushButton("Внести", dialog)
    btn_insert.setGeometry(150, 280, 100, 30)

    def insert_record():
        try:
            attack_type = attack_type_edit.text().strip()
            target_ip = target_ip_edit.text().strip()
            start_time = start_time_edit.text().strip()
            duration_sec = int(duration_sec_edit.text().strip())
            peak_dbs = int(peak_dbs_edit.text().strip())
            source_count = int(source_count_edit.text().strip())

            if not (attack_type and target_ip and start_time):
                QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Заполните все поля!")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (attack_type, target_ip, start_time, duration_sec, peak_dbs, source_count)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (attack_type, target_ip, start_time, duration_sec, peak_dbs, source_count))
            conn.commit()
            cursor.close()
            conn.close()
            QtWidgets.QMessageBox.information(dialog, "Успех", "Запись добавлена!")
            dialog.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(dialog, "Ошибка", str(e))

    btn_insert.clicked.connect(insert_record)
    dialog.exec_()

# ========================
# Создаём приложение и главное окно
# ========================
app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("ui/main.ui")  # загружаем UI
window.setWindowTitle("PostgreSQL + Qt5")

# ========================
# Подключаем кнопки только после загрузки UI
# ========================
window.mainButton_createTable.clicked.connect(create_schema_and_tables)
window.mainButton_insertData.clicked.connect(open_modal)

# ========================
# Показываем главное окно
# ========================
window.show()
sys.exit(app.exec_())
