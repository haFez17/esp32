from passlib.hash import bcrypt
from pymongo import MongoClient
import json

# Подключение к MongoDB Atlas
uri = "mongodb+srv://Anastasia_team:HLnmCzLQI3ne1wY4@cluster0.bwyk7.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# Выбор базы данных
db = client["translation_system"]

# Выбор коллекций
translations_collection = db["translations"]
users_collection = db["users"]


def save_user(username, password, mac_address):
    """Сохранение пользователя в базе данных"""
    if users_collection.find_one({"username": username}) or users_collection.find_one({"mac_address": mac_address}):
        return False  # Логин или MAC-адрес уже зарегистрирован

    hashed_password = bcrypt.hash(password)
    users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "mac_address": mac_address
    })
    return True


def authenticate_user(username, password):
    """Проверка логина и пароля"""
    user = users_collection.find_one({"username": username})
    if user and bcrypt.verify(password, user["password"]):
        return True
    return False


def save_data(original, translated, lang):
    """Сохранение перевода в базе данных"""
    data = {
        "original_text": original,
        "translated_text": translated,
        "language": lang
    }
    translations_collection.insert_one(data)


def export_data_to_json():
    """Экспорт переводов в JSON-файл"""
    import json
    data = list(translations_collection.find({}, {"_id": 0}))  # Убираем MongoDB `_id`

    with open("translations.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Данные успешно экспортированы в translations.json")
