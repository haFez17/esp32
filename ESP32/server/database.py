import json
from passlib.hash import bcrypt
from pymongo import MongoClient

# Подключение к MongoDB Atlas
uri = "mongodb+srv://Anastasia_team:HLnmCzLQI3ne1wY4@cluster0.bwyk7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

# Проверяем подключение
try:
    client.admin.command("ping")
    print("Успешное подключение к MongoDB Atlas!")
except Exception as e:
    print(f"Ошибка подключения: {e}")

# Используем базу данных
db = client["translations_db"]
collection = db["translations"]
users_collection = db["users"]

with open("texts.json", "r", encoding="utf-8") as file:
    data = json.load(file)  # Загружаем JSON

    if isinstance(data, list):  # Если в файле массив JSON-объектов
        collection.insert_many(data)
    else:  # Если один объект
        collection.insert_one(data)

def save_user(username, password, mac_address):
    """Сохраняет нового пользователя в базе данных"""
    if users_collection.find_one({"$or": [{"username": username}, {"mac_address": mac_address}]}):
        return None  # Логин или MAC-адрес уже зарегистрирован

    hashed_password = bcrypt.hash(password)
    result = users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "mac_address": mac_address
    })
    return str(result.inserted_id)  # Возвращаем ID нового пользователя


def authenticate_user(username, password):
    """Аутентифицирует пользователя"""
    user = users_collection.find_one({"username": username})
    if user and bcrypt.verify(password, user["password"]):
        return user  # Возвращаем объект пользователя
    return None


def save_data(original, translated, lang, mac_address):
    """Сохраняет переведённый текст, привязывая его к устройству"""
    data = {
        "original_text": original,
        "translated_text": translated,
        "language": lang,
        "mac_address": mac_address  # Привязываем перевод к конкретному устройству
    }
    collection.insert_one(data)
