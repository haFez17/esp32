from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["translations_db"]
collection = db["translations"]

def save_data(original, translated, lang):
    data = {
        "original_text": original,
        "translated_text": translated,
        "language": lang
    }
    collection.insert_one(data)

