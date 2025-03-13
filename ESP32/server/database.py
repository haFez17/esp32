from passlib.hash import bcrypt
from pymongo import MongoClient
import json

uri = "mongodb+srv://Anastasia_team:omar2003@cluster0.bwyk7.mongodb.net/"
client = MongoClient(uri)
db = client["translation_system"]

translations_collection = db["translations"]
users_collection = db["users"]


def save_user(username, password, mac_address):
    try:
        existing_user = users_collection.find_one({
            "$or": [{"username": username}, {"mac_address": mac_address}]
        })
        if existing_user:
            return False

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
    try:
        user = users_collection.find_one({"username": username})
        if user and bcrypt.verify(password, user["password"]):
            return True
        return False
    except Exception as e:
        print(f"Ошибка при аутентификации: {e}")
        return False


def save_data(original, translated, lang):
    try:
        translations_collection.insert_one({
            "original_text": original,
            "translated_text": translated,
            "language": lang
        })
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")


if __name__ == "__main__":
    print("База данных подключена успешно.")
