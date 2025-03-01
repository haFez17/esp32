import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
from googletrans import Translator
import database
from starlette.responses import RedirectResponse
from spellchecker import SpellChecker
import nltk
from fastapi import Request

nltk.download('punkt')

app = FastAPI()
translator = Translator()
spell = SpellChecker()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Переадресация на регистрацию при входе на сайт
@app.get("/")
async def home():
    return RedirectResponse(url="/home/")


# Регистрация
@app.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})

@app.post("/register/")
async def register(request: Request, username: str = Form(...), password: str = Form(...), mac_address: str = Form(...)):
    # Проверка на существующего пользователя
    if database.save_user(username, password, mac_address):
        return RedirectResponse(url="/login/", status_code=303)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Логин или MAC-адрес уже используется!"
    })


# Вход
@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход"})

@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Аутентификация пользователя
    if database.authenticate_user(username, password):
        return RedirectResponse(url="/translation/", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Неверный логин или пароль!"
    })


# Страница перевода
@app.get("/translation/")
async def translate_page(request: Request):
    data = list(database.collection.find({}, {"_id": 0}))
    return templates.TemplateResponse("translation.html", {
        "request": request,
        "title": "Перевод",
        "translations": data
    })


# Загрузка изображений и перевод
@app.post("/upload/")
async def upload_images(file: UploadFile = File(...), target_language: str = Form("en")):
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
    uvicorn.run("server:app", host='0.0.0.0', port=8080, reload=True)

#http://127.0.0.1:8080/