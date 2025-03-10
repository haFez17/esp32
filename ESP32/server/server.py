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
from langdetect import detect
from fastapi import Request
import nltk

nltk.download('punkt')

app = FastAPI()
translator = Translator()
spell = SpellChecker()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Проверка сессии пользователя
async def get_user_session(request: Request):
    return request.cookies.get("user")


@app.get("/")
async def redirect_to_register(request: Request):
    user = await get_user_session(request)
    if user:
        return RedirectResponse(url="/home/")
    return RedirectResponse(url="/register/")


@app.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})


@app.post("/register/")
async def register(request: Request, username: str = Form(...), password: str = Form(...), mac_address: str = Form(...)):
    if database.save_user(username, password, mac_address):
        response = RedirectResponse(url="/login/", status_code=303)
        return response
    return templates.TemplateResponse("register.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Логин или MAC-адрес уже используется!"
    })


@app.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход"})


@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if database.authenticate_user(username, password):
        response = RedirectResponse(url="/home/", status_code=303)
        response.set_cookie(key="user", value=username)  # Устанавливаем cookie для сессии
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Ошибка",
        "error": "Неверный логин или пароль!"
    })


@app.get("/home/")
async def home_page(request: Request):
    user = await get_user_session(request)
    if not user:
        return RedirectResponse(url="/login/")
    return templates.TemplateResponse("home.html", {"request": request, "title": "Главная"})


@app.get("/camera/")
async def camera_page(request: Request):
    user = await get_user_session(request)
    if not user:
        return RedirectResponse(url="/login/")
    return templates.TemplateResponse("camera.html", {"request": request, "title": "Камера"})


@app.get("/translation/")
async def translation_page(request: Request):
    user = await get_user_session(request)
    if not user:
        return RedirectResponse(url="/login/")
    data = list(database.translations_collection.find({}, {"_id": 0}))
    return templates.TemplateResponse("translation.html", {"request": request, "title": "Перевод", "translations": data})


@app.post("/upload/")
async def upload_images(file: UploadFile = File(...), target_language: str = Form("en")):
    image = Image.open(file.file)
    text = pytesseract.image_to_string(image, lang="eng")
    detected_lang = detect(text)
    corrected_text = correct_text(text)
    translated_text = translator.translate(corrected_text, src=detected_lang, dest=target_language).text
    database.save_data(corrected_text, translated_text, target_language)
    return {"original_text": corrected_text, "translated_text": translated_text, "detected_language": detected_lang}


def correct_text(text):
    words = text.split()
    corrected_words = [spell.correction(word) or word for word in words]
    return " ".join(corrected_words)






# http://127.0.0.1:8080/
# uvicorn server:app --host 0.0.0.0 --port 8080 --reload