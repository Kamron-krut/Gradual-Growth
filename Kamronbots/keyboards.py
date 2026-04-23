from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_language_keyboard():
    buttons = [
        [KeyboardButton(text="🇺🇿 O‘zbek"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_main_keyboard(lang="ru"):
    if lang == "uz":
        buttons = [
            [KeyboardButton(text="💰 Moliyaviy savodxonlik")],
            [KeyboardButton(text="📈 Tadbirkorlik")],
            [KeyboardButton(text="💻 IT va raqamli ko‘nikmalar")],
            [KeyboardButton(text="🧠 Hayotiy ko‘nikmalar")]
        ]
    elif lang == "en":
        buttons = [
            [KeyboardButton(text="💰 Financial literacy")],
            [KeyboardButton(text="📈 Entrepreneurship")],
            [KeyboardButton(text="💻 IT & digital skills")],
            [KeyboardButton(text="🧠 Life skills")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="💰 Финансовая грамотность")],
            [KeyboardButton(text="📈 Предпринимательство")],
            [KeyboardButton(text="💻 IT и цифровые навыки")],
            [KeyboardButton(text="🧠 Жизненные навыки")]
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)