import psycopg2
from psycopg2 import errors
import logging
from PyQt5 import QtWidgets


logging.basicConfig(
    filename='../app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    errors='replace'
)

# Подключение к бд
def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="klim",
        host="localhost",
        port="5432"
    )

# Создание таблицы с основными типами данных
def create_schema_and_tables(window):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TYPE attack_enum AS ENUM (
            'syn_flood', 'udp_flood', 'icmp_flood', 'http_get_flood',
            'http_post_flood', 'slowloris', 'dns_amplification',
            'ntp_amplification', 'smurf', 'botnet'
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
        logging.info("Table initialized!")
    except errors.DuplicateObject:
        QtWidgets.QMessageBox.critical(window, "Ошибка", "База данных уже существует")
        logging.info("The table is already initialized!")
    except Exception as e:
        QtWidgets.QMessageBox.critical(window, "Ошибка", str(e))
        logging.error("Table not initialized! " + str(e), exc_info=True)
