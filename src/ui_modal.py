from PyQt5 import QtWidgets, QtCore, QtGui
from db import get_connection
import logging


countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Belarus", "Belgium", "Brazil", "Bulgaria", "Canada",
    "China", "Colombia", "Czechia", "Denmark", "Egypt",
    "France", "Germany", "Greece", "India", "Indonesia",
    "Italy", "Japan", "Kazakhstan", "Mexico", "Netherlands",
    "Norway", "Poland", "Portugal", "Romania", "Russia",
    "Spain", "Sweden", "Switzerland", "Turkey", "United Kingdom",
    "United States"
]

# Модальное окно для ввода данных

def open_modal(window):
    dialog = QtWidgets.QDialog(window)
    dialog.setWindowTitle("Добавить запись")
    dialog.setModal(True)
    dialog.setFixedSize(420, 480)

    # ATTACK_TYPE
    attack_type_label = QtWidgets.QLabel("Attack type:", dialog)
    attack_type_label.setGeometry(15, 20, 100, 30)
    attack_type_combo = QtWidgets.QComboBox(dialog)
    attack_type_combo.setGeometry(120, 20, 200, 30)
    attack_type_combo.setEditable(False)
    attack_type_combo.addItems([
        'syn_flood', 'udp_flood', 'icmp_flood', 'http_get_flood', 'http_post_flood',
        'slowloris', 'dns_amplification', 'ntp_amplification', 'smurf', 'botnet'
    ])

    # IP
    target_ip_label = QtWidgets.QLabel("IP:", dialog)
    target_ip_label.setGeometry(15, 60, 100, 30)
    target_ip_edit = QtWidgets.QLineEdit(dialog)
    target_ip_edit.setGeometry(120, 60, 200, 30)
    ipv4_regex = QtCore.QRegExp(r'^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$')
    target_ip_edit.setValidator(QtGui.QRegExpValidator(ipv4_regex, target_ip_edit))

    # START TIME
    start_time_label = QtWidgets.QLabel("Start time:", dialog)
    start_time_label.setGeometry(15, 100, 100, 30)
    start_time_date = QtWidgets.QDateTimeEdit(dialog)
    start_time_date.setGeometry(120, 100, 200, 30)
    start_time_date.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

    # DURATION
    duration_sec_label = QtWidgets.QLabel("Duration (sec):", dialog)
    duration_sec_label.setGeometry(15, 140, 100, 30)
    duration_sec_edit = QtWidgets.QLineEdit(dialog)
    duration_sec_edit.setGeometry(120, 140, 200, 30)

    # PEAK DBS
    peak_dbs_label = QtWidgets.QLabel("Peak dbs:", dialog)
    peak_dbs_label.setGeometry(15, 180, 100, 30)
    peak_dbs_edit = QtWidgets.QLineEdit(dialog)
    peak_dbs_edit.setGeometry(120, 180, 200, 30)

    # SOURCE COUNT
    source_count_label = QtWidgets.QLabel("Source count:", dialog)
    source_count_label.setGeometry(15, 220, 100, 30)
    source_count_edit = QtWidgets.QLineEdit(dialog)
    source_count_edit.setGeometry(120, 220, 200, 30)

    # SOURCE COUNTRY
    source_country_label = QtWidgets.QLabel("Source Country:", dialog)
    source_country_label.setGeometry(15, 260, 100, 30)
    source_country_edit = QtWidgets.QLineEdit(dialog)
    source_country_edit.setGeometry(120, 260, 200, 30)
    completer = QtWidgets.QCompleter(countries, dialog)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    source_country_edit.setCompleter(completer)

    # IS DETECTED
    is_detected_label = QtWidgets.QLabel("Is detected?", dialog)
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

    # Функция для внесения данных в таблицу
    def insert_record():
        conn, cursor = None, None
        try:
            attack_type = attack_type_combo.currentText().strip()
            target_ip = target_ip_edit.text().strip()
            start_time = start_time_date.text().strip()
            duration_sec_text = duration_sec_edit.text().strip()
            peak_dbs_text = peak_dbs_edit.text().strip()
            source_count_text = source_count_edit.text().strip()
            source_country = source_country_edit.text().strip()
            is_detected = true_radio.isChecked()

            if not all([attack_type, target_ip, start_time, duration_sec_text, peak_dbs_text, source_count_text]):
                QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Заполните все обязательные поля!")
                logging.warning("Insert attempt with empty required fields")
                return

            try:
                duration_sec = int(duration_sec_text)
                peak_dbs = int(peak_dbs_text)
                source_count = int(source_count_text)
            except ValueError as ve:
                QtWidgets.QMessageBox.warning(dialog, "Ошибка",
                                              "Duration, Peak dbs и Source count должны быть числами!")
                logging.warning(f"Insert attempt with invalid numbers: {ve}")
                return

            if source_country:
                for c in source_country.split(","):
                    if c.strip() not in countries:
                        QtWidgets.QMessageBox.warning(dialog, "Ошибка", f"Страна '{c.strip()}' не найдена!")
                        return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO attack_name (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (attack_type,))
            cursor.execute("""
                INSERT INTO users (attack_type, target_ip, start_time, duration_sec,
                                   peak_dbs, source_count, is_detected, source_countries)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (attack_type, target_ip, start_time, duration_sec, peak_dbs,
                  source_count, is_detected,
                  [c.strip() for c in source_country.split(",")] if source_country else None))
            conn.commit()
            cursor.close()
            conn.close()
            QtWidgets.QMessageBox.information(dialog, "Успех", "Запись добавлена!")
            logging.info(f"Record inserted: attack_type={attack_type}, target_ip={target_ip}")
            dialog.accept()
        except Exception as e:
            if conn: conn.rollback()
            QtWidgets.QMessageBox.critical(dialog, "Ошибка", str(e))
            logging.error(f"Insert failed: {e}", exc_info=True)

    btn_insert.clicked.connect(insert_record)
    dialog.exec_()
