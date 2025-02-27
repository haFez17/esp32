from pymongo import MongoClient
from passlib.hash import bcrypt

client = MongoClient("mongodb://localhost:27017/")
db = client["translations_db"]
collection = db["translations"]
users_collection = db["users"]


def save_user(username, password, mac_address):
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
    user = users_collection.find_one({"username": username})
    if user and bcrypt.verify(password, user["password"]):
        return True
    return False


def save_data(original, translated, lang):
    data = {
        "original_text": original,
        "translated_text": translated,
        "language": lang
    }
    collection.insert_one(data)