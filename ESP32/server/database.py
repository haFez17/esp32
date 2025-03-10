from passlib.hash import bcrypt
from pymongo import MongoClient
import json

# Подключение к MongoDB Atlas
#uri = "mongodb://atlas-sql-67c82b607ceec523052aa440-bwyk7.a.query.mongodb.net/translation_system?ssl=true&authSource=admin"
uri = "mongodb+srv://Anastasia_team:omar2003@cluster0.bwyk7.mongodb.net/"
client = MongoClient(uri)

# Выбираем базу данных
db = client["translation_system"]

# Выбираем коллекции
translations_collection = db["translations"]
users_collection = db["users"]



def save_user(username, password, mac_address):
    """Сохранение пользователя в базе данных"""
    try:
        existing_user = users_collection.find_one({
            "$or": [{"username": username}, {"mac_address": mac_address}]
        })
        if existing_user:
            return False  # Логин или MAC-адрес уже зарегистрирован

        hashed_password = bcrypt.hash(password)
        users_collection.insert_one({
            "username": username,
            "password": hashed_password,
            "mac_address": mac_address
        })
        return True
    except Exception as e:
        print(f"Ошибка при сохранении пользователя: {e}")
        return False


def authenticate_user(username, password):
    """Проверка логина и пароля"""
    try:
        user = users_collection.find_one({"username": username})
        if user and bcrypt.verify(password, user["password"]):
            return True
        return False
    except Exception as e:
        print(f"Ошибка при аутентификации: {e}")
        return False


def save_data(original, translated, lang):
    """Сохранение перевода в базе данных"""
    try:
        data = {
            "original_text": original,
            "translated_text": translated,
            "language": lang
        }
        translations_collection.insert_one(data)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")


def export_data_to_json():
    """Экспорт данных в texts.json и translation.json"""
    try:
        # Получаем все переводы из MongoDB
        data = list(translations_collection.find({}, {"_id": 0}))  # Убираем MongoDB `_id`

        if not data:
            print("Нет данных для экспорта!")
            return

        # Разделяем на два файла
        texts = [{"original_text": item["original_text"]} for item in data]
        translations = [{"translated_text": item["translated_text"], "language": item["language"]} for item in data]

        # Сохраняем texts.json
        with open("texts.json", "w", encoding="utf-8") as file:
            json.dump(texts, file, ensure_ascii=False, indent=4)

        # Сохраняем translation.json
        with open("translation.json", "w", encoding="utf-8") as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

        print("Данные успешно экспортированы в texts.json и translation.json")
    except Exception as e:
        print(f"Ошибка при экспорте данных: {e}")


if __name__ == "__main__":
    export_data_to_json()
