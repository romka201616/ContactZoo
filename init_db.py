import sqlite3
from werkzeug.security import generate_password_hash

# Название файла базы данных
DB_NAME = "database.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    );
    """)

    # Создание таблицы контактов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        photo TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # Вставка тестовых пользователей (с хешированием паролей)
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, is_admin)
    VALUES
        ('admin', ?, 1),
        ('user', ?, 0);
    """, (generate_password_hash('admin123'), generate_password_hash('user123')))

    # Вставка тестовых контактов (привязываем к пользователям)
    cursor.execute("""
    INSERT OR IGNORE INTO contacts (user_id, name, surname, phone, photo)
    VALUES
        (1, 'Иван', 'Иванов', '1234567890', 'ivan.jpg'),
        (2, 'Анна', 'Смирнова', '0987654321', 'anna.jpg');
    """)

    conn.commit()
    conn.close()
    print(f"База данных '{DB_NAME}' успешно инициализирована!")

if __name__ == "__main__":
    initialize_database()