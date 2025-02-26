import json
from fastapi import FastAPI, UploadFile, File, Body
import pytesseract
from PIL import Image
from googletrans import Translator
import database
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from spellchecker import SpellChecker
import nltk
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates

nltk.download('punkt', quiet=True)

app = FastAPI()
translator = Translator()
spell = SpellChecker()

templates = Jinja2Templates(directory="templates") #Jinja надо создать папку templates

class TranslationRequest(BaseModel):
    text: str
    target_language: str


class SaveTranslationRequest(BaseModel):
    original_text: str
    translated_text: str
    language: str


@app.post("/process_image/")
async def process_image(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file)

        # Optional image preprocessing for better OCR
        # image = image.convert("L")  # Convert to grayscale
        # image = image.point(lambda x: 0 if x < 140 else 255)  # Binarize the image

        text = pytesseract.image_to_string(image, lang="eng")

        corrected_text = correct_text(text)

        return {"extracted_text": corrected_text}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )


# Translate text endpoint
@app.post("/translate_text/")
async def translate_text(request: TranslationRequest):
    try:
        translated = translator.translate(
            request.text,
            dest=request.target_language
        ).text

        return {"translated_text": translated}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Translation failed: {str(e)}"}
        )


# Save translation to database
@app.post("/save_translation/")
async def save_translation(request: SaveTranslationRequest):
    try:
        database.save_data(
            request.original_text,
            request.translated_text,
            request.language
        )
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to save translation: {str(e)}"}
        )


# Original upload endpoint (kept for compatibility)
@app.post("/upload/")
async def upload_images(file: UploadFile = File(...), target_language: str = "en"):
    image = Image.open(file.file)

    # Optional image preprocessing
    # image = image.convert("L")
    # image = image.point(lambda x: 0 if x < 140 else 255)

    text = pytesseract.image_to_string(image, lang="eng")
    corrected_text = correct_text(text)
    translated_text = translator.translate(corrected_text, dest=target_language).text

    database.save_data(corrected_text, translated_text, target_language)

    return {"original_text": corrected_text, "translated_text": translated_text}


def correct_text(text):
    words = text.split()
    corrected_words = [spell.correction(word) or word for word in words]
    return " ".join(corrected_words)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return RedirectResponse(url="/static/home.html")


@app.get("/camera")
async def camera_page():
    return RedirectResponse(url="/static/camera.html")


@app.get("/translate")
async def translate_page():
    return RedirectResponse(url="/static/translate.html")


@app.get("/data/")
async def get_data():
    return list(database.collection.find({}, {"_id": 0}))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("server:app", host='0.0.0.0', port=5000, reload=True)

    # http://127.0.0.1:5000/