import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
from googletrans import Translator
import database
from starlette.responses import RedirectResponse
from spellchecker import SpellChecker
import nltk

nltk.download('punkt')

app = FastAPI()
translator = Translator()
spell = SpellChecker()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# ✅ Переадресация на регистрацию при входе на сайт
@app.get("/")
async def home():
    return RedirectResponse(url="/register/")


# ✅ Страница регистрации
@app.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})


# ✅ Обработка регистрации
@app.post("/register/")
async def register(request: Request, username: str = Form(...), password: str = Form(...), mac_address: str = Form(...)):
    if database.save_user(username, password, mac_address):
        return RedirectResponse(url="/login/", status_code=303)  # ✅ После регистрации перекидывает на логин
    return templates.TemplateResponse("register.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Логин или MAC-адрес уже используется!"
    })


# ✅ Страница логина
@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход"})


# ✅ Обработка логина
@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if database.authenticate_user(username, password):
        return RedirectResponse(url="/translate/", status_code=303)  # ✅ После логина перекидывает на страницу перевода
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Неверный логин или пароль!"
    })


# ✅ Страница перевода (будет выводить оригинальный и переведённый текст, связанный с ESP-32)
@app.get("/translate/")
async def translate_page(request: Request):
    data = list(database.collection.find({}, {"_id": 0}))  # Получаем последние переводы
    return templates.TemplateResponse("translate.html", {
        "request": request,
        "title": "Перевод",
        "translations": data
    })


# ✅ Обработка загрузки изображения и перевода
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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("server:app", host='0.0.0.0', port=8000, reload=True)

#http://127.0.0.1:8000/
