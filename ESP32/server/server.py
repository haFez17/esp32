import json
from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
from googletrans import Translator
import database
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from spellchecker import SpellChecker
import nltk
nltk.download('punkt')


app = FastAPI()
translator = Translator()
spell=SpellChecker()


@app.post("/upload/")
async def upload_images(file: UploadFile = File(...), target_language: str = "en"):
    image = Image.open(file.file)
    text = pytesseract.image_to_string(image, lang="eng")

    corrected_text = correct_text(text)
    translated_text = translator.translate(corrected_text, dest=target_language).text

    database.save_data(corrected_text, translated_text, target_language)

    return {"original_text": corrected_text, "translated_text": translated_text}


def correct_text(text):
    words = text.split()
    corrected_words = [spell.correction(word) or word for word in words]
    return " ".join(corrected_words)

def save_to_json(original, translated, language):
    data = {"original_text": original, "translated_text": translated, "language": language}

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        content = []

    #content.append(data)
    #with open("data.json", "w", encoding="utf-8") as f:
    #    json.dump(content, f, ensure_ascii=False, indent=4)

    content.append(data)

    if len(content) > 10:
        content.pop(0)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

app.mount("/static", StaticFiles(directory="static"), name="static")

#Для возможно буферизации и черно-белый режим фотографиии, если какие-то не качественные изображения будут и т.д
#image = image.convert("L")
#image = image.point(lambda x: 0 if x < 0 140 else 255)





@app.get("/")
async def read_index():
    return RedirectResponse(url="/static/index.html")

@app.get("/data/")
async def get_data():
    return list(database.collection.find({}, {"_id": 0}))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("server:app", host='0.0.0.0', port=8000, reload=True)

#http://127.0.0.1:8000/
