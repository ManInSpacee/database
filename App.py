import sys
from PyQt5 import QtWidgets, uic, QtSql, QtCore, QtGui
import psycopg2
from psycopg2 import errors
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Tyur1234",
        host="localhost",
        port="5432"
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
        logging.info("Table initialized!")  # LOG: успешное создание таблиц
    except errors.DuplicateObject:
        QtWidgets.QMessageBox.critical(window, "Ошибка", "База данных уже существует")
    except Exception as e:
        QtWidgets.QMessageBox.critical(window, "Ошибка", str(e))
        logging.error("Table not initialized! " + str(e), exc_info=True)  # LOG: ошибка с traceback


def open_modal():
    dialog = QtWidgets.QDialog(window)
    dialog.setWindowTitle("Добавить запись")
    dialog.setModal(True)
    dialog.setFixedSize(420, 480)

    # ======== Поля для ввода ========
    attack_type_label = QtWidgets.QLabel(dialog)
    attack_type_label.setText("Attack type:")
    attack_type_label.setGeometry(15, 20, 200, 30)
    attack_type_edit = QtWidgets.QLineEdit(dialog)
    attack_type_edit.setPlaceholderText("exp: syn_flood, udp_flood..")
    attack_type_edit.setGeometry(120, 20, 200, 30)

    target_ip_label = QtWidgets.QLabel(dialog)
    target_ip_label.setText("IP:")
    target_ip_label.setGeometry(15, 60, 200, 30)
    target_ip_edit = QtWidgets.QLineEdit(dialog)
    target_ip_edit.setPlaceholderText("x.x.x.x")
    target_ip_edit.setGeometry(120, 60, 200, 30)

    start_time_label = QtWidgets.QLabel(dialog)
    start_time_label.setText("Start time:")
    start_time_label.setGeometry(15, 100, 200, 30)
    start_time_date = QtWidgets.QDateTimeEdit(dialog)
    start_time_date.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
    start_time_date.setGeometry(120, 100, 200, 30)

    duration_sec_label = QtWidgets.QLabel(dialog)
    duration_sec_label.setText("Duration (sec):")
    duration_sec_label.setGeometry(15, 140, 200, 30)
    duration_sec_edit = QtWidgets.QLineEdit(dialog)
    duration_sec_edit.setGeometry(120, 140, 200, 30)

    peak_dbs_label = QtWidgets.QLabel(dialog)
    peak_dbs_label.setText("Peak dbs:")
    peak_dbs_label.setGeometry(15, 180, 200, 30)
    peak_dbs_edit = QtWidgets.QLineEdit(dialog)
    peak_dbs_edit.setGeometry(120, 180, 200, 30)

    source_count_label = QtWidgets.QLabel(dialog)
    source_count_label.setText("Source count:")
    source_count_label.setGeometry(15, 220, 200, 30)
    source_count_edit = QtWidgets.QLineEdit(dialog)
    source_count_edit.setGeometry(120, 220, 200, 30)

    source_country_label = QtWidgets.QLabel(dialog)
    source_country_label.setText("Source Counter:")
    source_country_label.setGeometry(10, 260, 200, 30)
    source_country_edit = QtWidgets.QLineEdit(dialog)
    source_country_edit.setGeometry(120, 260, 200, 30)

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
        conn = None
        cursor = None
        try:
            attack_type = attack_type_edit.text().strip()
            target_ip = target_ip_edit.text().strip()
            start_time = start_time_date.text().strip()
            duration_sec_text = duration_sec_edit.text().strip()
            peak_dbs_text = peak_dbs_edit.text().strip()
            source_count_text = source_count_edit.text().strip()
            source_country = source_country_edit.text().strip()
            is_detected = True if true_radio.isChecked() else False

            # Проверка обязательных полей
            if not all([attack_type, target_ip, start_time, duration_sec_text, peak_dbs_text, source_count_text]):
                QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Заполните все обязательные поля!")
                logging.warning("Insert attempt with empty required fields")  # LOG: предупреждение
                return

            try:
                duration_sec = int(duration_sec_text)
                peak_dbs = int(peak_dbs_text)
                source_count = int(source_count_text)
            except ValueError as ve:
                QtWidgets.QMessageBox.warning(dialog, "Ошибка",
                                              "Поля Duration, Peak dbs и Source count должны быть числами!")
                logging.warning(f"Insert attempt with invalid numbers: {ve}")  # LOG: предупреждение
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO attack_name (name)
                           VALUES (%s) ON CONFLICT (name) DO NOTHING
                           """, (attack_type,))
            cursor.execute("""
                           INSERT INTO users (attack_type, target_ip, start_time, duration_sec,
                                              peak_dbs, source_count, is_detected, source_countries)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                           """, (attack_type, target_ip, start_time, duration_sec, peak_dbs,
                                 source_count, is_detected, [source_country] if source_country else None))
            conn.commit()
            cursor.close()
            conn.close()

            QtWidgets.QMessageBox.information(dialog, "Успех", "Запись добавлена!")
            logging.info(f"Record inserted: attack_type={attack_type}, target_ip={target_ip}")  # LOG: успешная вставка
            dialog.accept()
        except errors.CheckViolation:
            QtWidgets.QMessageBox.warning(dialog, "Ошибка", "В одном из полей введено отрицательное значение!")
            logging.warning("Check constraint violation during insert")  # LOG/DB ERROR
        except errors.InvalidTextRepresentation:
            QtWidgets.QMessageBox.warning(
                dialog,
                "Ой, сладенький 💖",
                "Такого значения в ENUM нет... ну ты хоть иногда читай, что вводишь 😘")
            logging.error(f"Invalid ENUM value entered: attack_type='{attack_type}'")
        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    QtWidgets.QMessageBox.critical(dialog, "Ошибка отката", str(rollback_error))
                    logging.error(f"Rollback failed: {rollback_error}", exc_info=True)  # LOG: ошибка отката
            QtWidgets.QMessageBox.critical(dialog, "Ошибка", str(e))
            logging.error(f"Insert failed: {e}", exc_info=True)  # LOG: ошибка вставки

    btn_insert.clicked.connect(insert_record)
    dialog.exec_()

def show_table_window():
    table_dialog = QtWidgets.QWidget()
    table_dialog.setWindowTitle("Таблица пользователей")
    table_dialog.setGeometry(100, 100, 800, 450)

    filter_edit = QtWidgets.QLineEdit(table_dialog)
    filter_edit.setPlaceholderText("Введите текст для фильтрации...")
    filter_edit.setGeometry(10, 10, 780, 30)

    table_view = QtWidgets.QTableView(table_dialog)
    table_view.setGeometry(10, 50, 780, 390)

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
        table_view.setSortingEnabled(True)
        table_view.resizeColumnsToContents()
        model.setHorizontalHeaderLabels(columns)
        for row in rows:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        table_view.setModel(model)
        cursor.close()
        conn.close()
        logging.info(f"Table loaded with filter='{filter_text}'")  # LOG: инфо о загрузке таблицы

    load_data()
    filter_edit.textChanged.connect(lambda text: load_data())
    table_dialog.show()
    window.table_dialog_window = table_dialog

app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("ui/main.ui")
window.setWindowTitle("PostgreSQL + Qt5")

window.mainButton_createTable.clicked.connect(create_schema_and_tables)
window.mainButton_insertData.clicked.connect(open_modal)
window.mainButton_showData.clicked.connect(show_table_window)

window.show()
sys.exit(app.exec_())
