import sys
from PyQt5 import QtWidgets, uic, QtSql, QtCore, QtGui

import psycopg2
def get_connection():
    return psycopg2.connect(
        dbname="postgres",       # имя базы
        user="postgres",         # ваш пользователь
        password="Tyur1234",         # ваш пароль
        host="localhost",        # или другой хост
        port="5432"              # порт PostgreSQL
    )
def create_schema_and_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TYPE attack_enum AS ENUM (
            'syn_flood',
            'udp_flood',
            'icmp_flood',
            'http_get_flood',
            'http_post_flood',
            'slowloris',
            'dns_amplification',
            'ntp_amplification',
            'smurf',
            'botnet'
            );
            
            CREATE TABLE IF NOT EXISTS attack_name (
                name attack_enum PRIMARY KEY
            );
            
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                attack_type attack_enum NOT NULL REFERENCES attack_name(name)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                target_ip VARCHAR NOT NULL,
                start_time TIMESTAMP NOT NULL,
                duration_sec INT NOT NULL CHECK (duration_sec >= 0),
                peak_dbs BIGINT NOT NULL CHECK (peak_dbs >= 0),
                source_count INT NOT NULL CHECK (source_count >= 0),
                is_detected BOOLEAN NOT NULL DEFAULT TRUE,
                source_countries TEXT[]
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
    dialog.setFixedSize(400, 480)

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

    source_country_edit = QtWidgets.QLineEdit(dialog)
    source_country_edit.setPlaceholderText("Source Country")
    source_country_edit.setGeometry(100, 260, 200, 30)

    is_detected_label = QtWidgets.QLabel(dialog)
    is_detected_label.setText("Is detected?")
    is_detected_label.setGeometry(160, 300, 200, 30)

    true_radio = QtWidgets.QRadioButton("Yes", dialog)
    true_radio.setGeometry(120, 330, 100, 30)

    false_radio = QtWidgets.QRadioButton("No", dialog)
    false_radio.setGeometry(200, 330, 100, 30)

    radio_group = QtWidgets.QButtonGroup(dialog)
    radio_group.addButton(true_radio)
    radio_group.addButton(false_radio)

    true_radio.setChecked(True)

    btn_insert = QtWidgets.QPushButton("Внести", dialog)
    btn_insert.setGeometry(150, 380, 100, 30)

    def insert_record():
        try:
            attack_type = attack_type_edit.text().strip()
            target_ip = target_ip_edit.text().strip()
            start_time = start_time_edit.text().strip()
            duration_sec = int(duration_sec_edit.text().strip())
            peak_dbs = int(peak_dbs_edit.text().strip())
            source_count = int(source_count_edit.text().strip())
            source_country = source_country_edit.text().strip()
            is_detected = True if true_radio.isChecked() else False

            if not (attack_type and target_ip and start_time):
                QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Заполните все поля!")
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO attack_name (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """, (attack_type,))
            cursor.execute("""
            INSERT INTO users (attack_type, target_ip, start_time, duration_sec,
            peak_dbs, source_count, is_detected, source_countries)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (attack_type,target_ip, start_time, duration_sec, peak_dbs,
                  source_count, is_detected, [source_country] if source_country else None))
            conn.commit()
            cursor.close()
            conn.close()
            QtWidgets.QMessageBox.information(dialog, "Успех", "Запись добавлена!")
            dialog.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(dialog, "Ошибка", str(e))

    btn_insert.clicked.connect(insert_record)
    dialog.exec_()

def show_table_window():
    # Создаём немодальное окно прямо в коде
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

    # Функция для загрузки данных из psycopg2
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
        cursor.close()
        conn.close()
    load_data()
    filter_edit.textChanged.connect(lambda text: load_data())
    table_dialog.show()
    window.table_dialog_window = table_dialog


app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("ui/main.ui")  # загружаем UI
window.setWindowTitle("PostgreSQL + Qt5")

# ========================
# Подключаем кнопки только после загрузки UI
# ========================
window.mainButton_createTable.clicked.connect(create_schema_and_tables)
window.mainButton_insertData.clicked.connect(open_modal)
window.mainButton_showData.clicked.connect(show_table_window)


# ========================
# Показываем главное окно
# ========================
window.show()
sys.exit(app.exec_())
