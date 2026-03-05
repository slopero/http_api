import sqlite3
from config import DB_PATH

# Функция для подключения к базе данных
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)  # timeout для избежания database is locked
    return conn

# Инициализация всех таблиц БД
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица городов и данных о погоде
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,      
            longitude REAL NOT NULL, 
            temperature REAL NOT NULL,
            wind_speed REAL NOT NULL,
            pressure REAL NOT NULL
        )
    """)
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE
        )
    """)
    
    # Таблица связи пользователей и городов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_cities (
            id_user INTEGER,
            id_city INTEGER,
            PRIMARY KEY (id_user, id_city),
            FOREIGN KEY (id_user) REFERENCES users(id_user),
            FOREIGN KEY (id_city) REFERENCES weather_data(id)    
        )
    """)
    
    conn.commit()
    conn.close()

# Функция для добавления данных в базу данных
def add_weather_city(city: str, latitude: float, longitude: float, temperature: float, wind_speed: float, pressure: float):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO weather_data (city, latitude, longitude, temperature, wind_speed, pressure)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (city, latitude, longitude, temperature, wind_speed, pressure))
    
    conn.commit()
    conn.close()

# Функция для получения всех городов из базы данных (для обновления погоды)
def get_all_cities():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT city, latitude, longitude FROM weather_data")
    cities = cursor.fetchall()
    conn.close()
    return cities

# Функция для получения города и координат из базы данных для конкретного пользователя
def get_user_cities(id_user: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select city, latitude, longitude from weather_data where id in (select id_city from user_cities where id_user = ?)", (id_user,))
    cities = cursor.fetchall()
    conn.close()
    return cities

# Функция для обновления данных о погоде города
def update_weather(city: str, temperature: float, wind_speed: float, pressure: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("update weather_data set temperature = ?, wind_speed = ?, pressure = ? where city = ?", (temperature, wind_speed, pressure, city))
    conn.commit()
    conn.close()

# Функция для получения координат города по названию для конкретного пользователя
def get_city_coordinates(city: str, id_user: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wd.latitude, wd.longitude 
        FROM weather_data wd 
        JOIN user_cities uc ON wd.id = uc.id_city 
        WHERE wd.city = ? AND uc.id_user = ?
    """, (city, id_user))
    result = cursor.fetchone()
    conn.close()
    return result

# Функция для добавления пользователя в БД
def add_user(login: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Добавление пользователя в БД
    cursor.execute("""
        insert or ignore into users (login) values (?)
    """, (login,))

    conn.commit()
    conn.close()

# Получение id пользователя по логину
def get_user_id(login: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select id_user from users where login = ?", (login,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Получение id города по названию
def get_city_id(city: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select id from weather_data where city = ?", (city,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Функция для добавления данных о городе в список пользователя
def add_city_user(id_user: int, city: str):
    conn = get_connection()
    cursor = conn.cursor()
    id_city = get_city_id(city)
    try:
        cursor.execute("select id_user from users where id_user = ?", (id_user,))
    except Exception:
        raise Exception(f"Пользователь с id_user = {id_user} не найден в базе данных")
    if id_city is None:
        raise Exception(f"Город '{city}' не найден в базе данных")

    # Добавление города в список пользователя
    cursor.execute("""
    insert or ignore into user_cities (id_user, id_city) values (?, ?)
    """, (id_user, id_city))

    conn.commit()
    conn.close()
    
# Проверка на существование пользователя в БД
def user_exists(id_user: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select id_user from users where id_user = ?", (id_user,))
    result = cursor.fetchone()
    conn.close()
    return result is not None