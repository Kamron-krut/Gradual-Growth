import asyncio
import logging
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== ДАННЫЕ ==========
user_lang = {}
user_stats = {}
questions_db = []
DATA_FILE = "users_data.json"
QUESTIONS_FILE = "questions.json"
ADMIN_ID = 7570970979

YOUTUBE_URL = "https://youtube.com/@inclusive_educatio0n?si=d2qGsDkM5BIGkUN6"


def load_data():
    global user_lang, user_stats, questions_db
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_lang = {int(k): v for k, v in data.get("language", {}).items()}
            user_stats = {int(k): v for k, v in data.get("stats", {}).items()}
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            questions_db = json.load(f)


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"language": user_lang, "stats": user_stats}, f, ensure_ascii=False, indent=2)
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions_db, f, ensure_ascii=False, indent=2)


load_data()

# ========== ТЕКСТЫ ==========
WELCOME = {
    "uz": "👋 Salom! Inclusive Education botiga xush kelibsiz.",
    "ru": "👋 Привет! Добро пожаловать в бот Inclusive Education.",
    "en": "👋 Hi! Welcome to Inclusive Education bot."
}

# ГЛАВНОЕ МЕНЮ
MAIN_MENU = {
    "uz": ["📖 Loyiha haqida", "❓ Savol berish", "📊 Mening statistikam", "🛍 Do'kon", "🎥 Videokurs", "👥 Jamiyat"],
    "ru": ["📖 О проекте", "❓ Задать вопрос", "📊 Моя статистика", "🛍 Магазин", "🎥 Видеокурс", "👥 Сообщество"],
    "en": ["📖 About", "❓ Ask question", "📊 My stats", "🛍 Shop", "🎥 Video course", "👥 Community"]
}

# МАГАЗИН
SHOP_MENU = {
    "uz": {
        "items": ["📚 Maxsus kurs - 200 tanga", "🎬 Maxsus video - 100 tanga"],
        "earn": "💰 Tanga ishlash",
        "back": "◀️ Orqaga"
    },
    "ru": {
        "items": ["📚 Спецкурс - 200 монет", "🎬 Спецвидео - 100 монет"],
        "earn": "💰 Заработать монеты",
        "back": "◀️ Назад"
    },
    "en": {
        "items": ["📚 Special course - 200 coins", "🎬 Special video - 100 coins"],
        "earn": "💰 Earn coins",
        "back": "◀️ Back"
    }
}


def get_main_keyboard(lang):
    buttons = MAIN_MENU[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn) for btn in buttons]],
        resize_keyboard=True
    )


def get_shop_keyboard(lang):
    shop = SHOP_MENU[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=shop["items"][0]), KeyboardButton(text=shop["items"][1])],
            [KeyboardButton(text=shop["earn"]), KeyboardButton(text=shop["back"])]
        ],
        resize_keyboard=True
    )


def get_language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]],
        resize_keyboard=True
    )


# ========== КОМАНДЫ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Выберите язык / Tilni tanlang / Choose language:", reply_markup=get_language_keyboard())


@dp.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ только для администратора.")
        return
    total_coins = sum(s.get("coins", 0) for s in user_stats.values())
    await message.answer(
        f"📊 Пользователей: {len(user_lang)}\n📋 Вопросов: {len(questions_db)}\n💰 Всего монет: {total_coins}")


@dp.message(Command("broadcast"))
async def broadcast_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав.")
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("❌ Напишите текст после /broadcast")
        return
    count = 0
    for user_id in user_lang.keys():
        try:
            await bot.send_message(user_id, text)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await message.answer(f"✅ Отправлено {count} пользователям.")


@dp.message(Command("answer"))
async def answer_to_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ только для администратора.")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❌ Формат: /answer USER_ID Текст ответа")
        return
    try:
        user_id = int(parts[1])
        answer_text = parts[2]
        await bot.send_message(user_id, f"📬 **Ответ от команды Inclusive Education:**\n\n{answer_text}")
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]))
async def set_language(message: Message):
    lang_map = {"🇺🇿 O'zbek": "uz", "🇷🇺 Русский": "ru", "🇬🇧 English": "en"}
    lang = lang_map[message.text]
    user_lang[message.from_user.id] = lang
    if message.from_user.id not in user_stats:
        user_stats[message.from_user.id] = {"coins": 0, "questions": 0, "bought": []}
    save_data()
    await message.answer(WELCOME[lang], reply_markup=get_main_keyboard(lang))


# ========== ГЛАВНОЕ МЕНЮ ==========
@dp.message(F.text.in_(["📖 О проекте", "📖 Loyiha haqida", "📖 About"]))
async def about_project(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    about_text = {
        "uz": "📖 Loyiha haqida\n\nBiz — UPSHIFT UNICEF loyihasi. Maqsadimiz: kar yoshlarga bepul ta'lim.\n\n👥 Jamoa: 5 nafar ishtirokchi\n📅 2025-yil",
        "ru": "📖 О проекте\n\nМы — проект UPSHIFT UNICEF. Цель: бесплатное образование для глухой молодёжи.\n\n👥 Команда: 5 участников\n📅 2025 год",
        "en": "📖 About the project\n\nWe are UPSHIFT UNICEF project. Goal: free education for deaf youth.\n\n👥 Team: 5 members\n📅 2025"
    }
    await message.answer(about_text[lang])


@dp.message(F.text.in_(["📊 Моя статистика", "📊 Mening statistikam", "📊 My stats"]))
async def my_stats(message: Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "ru")
    if user_id not in user_stats:
        user_stats[user_id] = {"coins": 0, "questions": 0, "bought": []}
        save_data()
    coins = user_stats[user_id].get("coins", 0)
    bought = user_stats[user_id].get("bought", [])
    user_questions = [q for q in questions_db if q.get("userId") == user_id]
    stats_text = {
        "uz": f"📊 Sizning statistikangiz:\n\n💰 Tangalar: {coins}\n❓ Savollar: {len(user_questions)}\n🛍 Sotib olingan: {len(bought)}",
        "ru": f"📊 Ваша статистика:\n\n💰 Монет: {coins}\n❓ Вопросов: {len(user_questions)}\n🛍 Куплено: {len(bought)}",
        "en": f"📊 Your stats:\n\n💰 Coins: {coins}\n❓ Questions: {len(user_questions)}\n🛍 Purchased: {len(bought)}"
    }
    await message.answer(stats_text[lang])


# ========== МАГАЗИН ==========
@dp.message(F.text.in_(["🛍 Магазин", "🛍 Do'kon", "🛍 Shop"]))
async def shop_menu(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    shop_text = {
        "uz": "🛍 Do'kon:\n\n📚 Maxsus kurs - 200 tanga\n🎬 Maxsus video - 100 tanga\n\n💰 Tanga ishlash uchun YouTube video ko'ring!",
        "ru": "🛍 Магазин:\n\n📚 Спецкурс - 200 монет\n🎬 Спецвидео - 100 монет\n\n💰 Чтобы заработать монеты, смотрите видео на YouTube!",
        "en": "🛍 Shop:\n\n📚 Special course - 200 coins\n🎬 Special video - 100 coins\n\n💰 Watch YouTube videos to earn coins!"
    }
    await message.answer(shop_text[lang], reply_markup=get_shop_keyboard(lang))


# КНОПКА НАЗАД ИЗ МАГАЗИНА
@dp.message(F.text.in_(["◀️ Назад", "◀️ Orqaga", "◀️ Back"]))
async def back_to_main(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    await message.answer("Главное меню:", reply_markup=get_main_keyboard(lang))


@dp.message(F.text.in_(["📚 Спецкурс - 200 монет", "📚 Maxsus kurs - 200 tanga", "📚 Special course - 200 coins"]))
async def buy_course(message: Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "ru")
    if user_id not in user_stats:
        user_stats[user_id] = {"coins": 0, "questions": 0, "bought": []}

    coins = user_stats[user_id].get("coins", 0)
    if coins >= 200:
        user_stats[user_id]["coins"] -= 200
        user_stats[user_id]["bought"].append("course")
        save_data()
        await message.answer("✅ Спецкурс куплен! Ссылка появится скоро.", reply_markup=get_shop_keyboard(lang))
    else:
        await message.answer(f"❌ Недостаточно монет. Нужно 200, у вас {coins}", reply_markup=get_shop_keyboard(lang))


@dp.message(F.text.in_(["🎬 Спецвидео - 100 монет", "🎬 Maxsus video - 100 tanga", "🎬 Special video - 100 coins"]))
async def buy_video(message: Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "ru")
    if user_id not in user_stats:
        user_stats[user_id] = {"coins": 0, "questions": 0, "bought": []}

    coins = user_stats[user_id].get("coins", 0)
    if coins >= 100:
        user_stats[user_id]["coins"] -= 100
        user_stats[user_id]["bought"].append("special_video")
        save_data()
        await message.answer("✅ Спецвидео куплено! Ссылка появится скоро.", reply_markup=get_shop_keyboard(lang))
    else:
        await message.answer(f"❌ Недостаточно монет. Нужно 100, у вас {coins}", reply_markup=get_shop_keyboard(lang))


# ========== ЗАРАБОТОК МОНЕТ ==========
@dp.message(F.text.in_(["💰 Заработать монеты", "💰 Tanga ishlash", "💰 Earn coins"]))
async def earn_coins(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    earn_text = {
        "uz": "💰 Tanga ishlash uchun YouTube videolarimizni ko'ring!\n\n🎥 Har bir video uchun +10 tanga!\n\n👇 Quyidagi tugma orqali videoga o'ting:",
        "ru": "💰 Чтобы заработать монеты, смотрите наши видео на YouTube!\n\n🎥 За каждое видео +10 монет!\n\n👇 Перейдите по кнопке ниже:",
        "en": "💰 Watch our YouTube videos to earn coins!\n\n🎥 +10 coins per video!\n\n👇 Click the button below:"
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Смотреть видео и заработать", url=YOUTUBE_URL)]
    ])
    await message.answer(earn_text[lang], reply_markup=keyboard)


# ========== ВИДЕОКУРС ==========
@dp.message(F.text.in_(["🎥 Видеокурс", "🎥 Videokurs", "🎥 Video course"]))
async def video_course(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    video_text = {
        "uz": "🎥 Videokurslarimiz:\n\nEng so'nggi darslarimizni YouTube kanalimizda ko'ring!",
        "ru": "🎥 Наши видеокурсы:\n\nСмотрите последние уроки на нашем YouTube канале!",
        "en": "🎥 Our video courses:\n\nWatch the latest lessons on our YouTube channel!"
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Перейти к видео", url=YOUTUBE_URL)]
    ])
    await message.answer(video_text[lang], reply_markup=keyboard)


# ========== СООБЩЕСТВО ==========
@dp.message(F.text.in_(["👥 Сообщество", "👥 Jamiyat", "👥 Community"]))
async def community(message: Message):
    lang = user_lang.get(message.from_user.id, "ru")
    community_text = {
        "uz": "👥 Jamiyatimiz hozir tayyorlanmoqda!\n\nTez orada qo'shilishingiz mumkin bo'ladi.",
        "ru": "👥 Наше сообщество скоро появится!\n\nСкоро вы сможете присоединиться.",
        "en": "👥 Our community is coming soon!\n\nYou will be able to join soon."
    }
    await message.answer(community_text[lang])


# ========== ОБРАБОТКА ВОПРОСОВ ==========
class QuestionState:
    waiting_for_question = {}


@dp.message(F.text.in_(["❓ Задать вопрос", "❓ Savol berish", "❓ Ask question"]))
async def ask_question_start(message: Message):
    user_id = message.from_user.id
    QuestionState.waiting_for_question[user_id] = True
    lang = user_lang.get(user_id, "ru")
    question_text = {
        "uz": "❓ Savolingizni yozing. Javob tez orada keladi.",
        "ru": "❓ Напишите ваш вопрос. Ответ придёт скоро.",
        "en": "❓ Write your question. You will get an answer soon."
    }
    await message.answer(question_text[lang])


@dp.message()
async def handle_questions(message: Message):
    user_id = message.from_user.id
    if user_id not in QuestionState.waiting_for_question:
        return
    lang = user_lang.get(user_id, "ru")
    question_text = message.text

    questions_db.append({
        "userId": user_id,
        "text": question_text,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "answered": False
    })
    save_data()

    if user_id not in user_stats:
        user_stats[user_id] = {"coins": 0, "questions": 0, "bought": []}
    user_stats[user_id]["questions"] = user_stats[user_id].get("questions", 0) + 1
    save_data()

    await bot.send_message(ADMIN_ID, f"📬 **Новый вопрос!**\n\n👤 ID: {user_id}\n❓ {question_text}")

    answers = {
        "uz": "✅ Savolingiz qabul qilindi. Javob tez orada keladi.",
        "ru": "✅ Ваш вопрос принят. Ответ придёт скоро.",
        "en": "✅ Your question has been received. Answer will come soon."
    }
    await message.answer(answers[lang])
    del QuestionState.waiting_for_question[user_id]


async def main():
    print("✅ Бот запущен")
    print(f"👑 Админ ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())