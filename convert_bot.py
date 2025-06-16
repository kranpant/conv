from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio
from converter import MangSession

# Bot configuration
API_ID = 27455984
API_HASH = "62d5f68ce2e9189636967120220f5755"
BOT_TOKEN = "6513440724:AAH0EGqjCATl-azX89Y2Uemi3OP-BRjzoZs"

# Initialize bot
app = Client(
    "session_converter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store user states and preferences
user_states = {}
user_lang = {}

# Translations
TRANSLATIONS = {
    "ar": {
        "welcome": """**مرحباً بك في بوت تحويل الجلسات! 👋**

يمكنني تحويل جلسات Pyrogram إلى Telethon والعكس.
استخدم الأمر /convert للبدء.""",
        "help": """**📖 كيفية استخدام البوت:**

1. استخدم الأمر /convert لبدء عملية التحويل

2. اختر نوع التحويل:
   • تحويل من بايروجرام إلى تيليثون
   • تحويل من تيليثون إلى بايروجرام

3. أرسل كود الجلسة (Session String)

4. سيقوم البوت بتحويل الجلسة وإرسال النتيجة

**ℹ️ ملاحظات:**
• يتم حذف الجلسات فور تحويلها
• البوت آمن ولا يحفظ أي بيانات""",
        "start_convert": "🔄 بدء التحويل",
        "help_button": "📖 المساعدة",
        "lang_button": "🌍 تغيير اللغة",
        "current_lang": "🌍 اللغة الحالية: العربية",
        "choose_lang": "**اختر لغة البوت:**",
        "lang_changed": "✅ تم تغيير لغة البوت إلى العربية",
        "convert_title": "**اختر نوع التحويل:**",
        "convert_options": """• تحويل من بايروجرام إلى تيليثون
• تحويل من تيليثون إلى بايروجرام""",
        "pyro_to_tele": "1️⃣ بايروجرام الي تيليثون",
        "tele_to_pyro": "2️⃣ تيليثون الي بايروجرام",
        "cancel": "❌ إلغاء",
        "cancelled": "**تم إلغاء العملية**",
        "send_session": """**أرسل كود الجلسة (Session String):**

ℹ️ سيتم حذف رسالتك فور التحويل للحفاظ على أمان حسابك""",
        "start_over": "الرجاء بدء التحويل من جديد باستخدام /convert",
        "converted_to": "**✅ تم التحويل بنجاح إلى {}**",
        "security_note": "ℹ️ تم حذف رسالة الجلسة الأصلية للحفاظ على أمان حسابك",
        "error": "**❌ حدث خطأ:**\n`{}`",
        "conversion_error": "**❌ حدث خطأ أثناء التحويل:**\n`{}`"
    },
    "en": {
        "welcome": """**Welcome to Session Converter Bot! 👋**

I can convert Pyrogram sessions to Telethon and vice versa.
Use /convert command to start.""",
        "help": """**📖 How to use the bot:**

1. Use /convert command to start conversion

2. Choose conversion type:
   • Convert from Pyrogram to Telethon
   • Convert from Telethon to Pyrogram

3. Send your Session String

4. Bot will convert and send the result

**ℹ️ Notes:**
• Sessions are deleted immediately after conversion
• The bot is secure and doesn't store any data""",
        "start_convert": "🔄 Start Converting",
        "help_button": "📖 Help",
        "lang_button": "🌍 Change Language",
        "current_lang": "🌍 Current Language: English",
        "choose_lang": "**Choose bot language:**",
        "lang_changed": "✅ Bot language changed to English",
        "convert_title": "**Choose conversion type:**",
        "convert_options": """• Convert from Pyrogram to Telethon
• Convert from Telethon to Pyrogram""",
        "pyro_to_tele": "1️⃣ Pyrogram To Telethon",
        "tele_to_pyro": "2️⃣ Telethon To Pyrogram",
        "cancel": "❌ Cancel",
        "cancelled": "**Operation cancelled**",
        "send_session": """**Send your Session String:**

ℹ️ Your message will be deleted after conversion for security""",
        "start_over": "Please start over using /convert",
        "converted_to": "**✅ Successfully converted to {}**",
        "security_note": "ℹ️ Original session message was deleted for security",
        "error": "**❌ Error occurred:**\n`{}`",
        "conversion_error": "**❌ Conversion error:**\n`{}`"
    }
}

def get_text(user_id: int, key: str) -> str:
    lang = user_lang.get(user_id, "ar")
    return TRANSLATIONS[lang][key]

def get_start_keyboard(user_id: int) -> InlineKeyboardMarkup:
    lang = user_lang.get(user_id, "ar")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TRANSLATIONS[lang]["start_convert"], callback_data="start_convert")],
        [
            InlineKeyboardButton(TRANSLATIONS[lang]["help_button"], callback_data="help"),
            InlineKeyboardButton(TRANSLATIONS[lang]["lang_button"], callback_data="change_lang")
        ]
    ])

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(
        get_text(user_id, "welcome"),
        reply_markup=get_start_keyboard(user_id)
    )

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(get_text(user_id, "help"))

@app.on_message(filters.command("convert"))
async def convert_command(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        user_states[user_id] = {"step": "awaiting_type"}
        
        buttons = [
            [
                InlineKeyboardButton(get_text(user_id, "pyro_to_tele"), callback_data="type_1"),
                InlineKeyboardButton(get_text(user_id, "tele_to_pyro"), callback_data="type_2")
            ],
            [InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="cancel")]
        ]
        
        await message.reply_text(
            f"{get_text(user_id, 'convert_title')}\n\n{get_text(user_id, 'convert_options')}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await message.reply_text(get_text(message.from_user.id, "error").format(str(e)))

@app.on_callback_query()
async def handle_callbacks(client: Client, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        
        if callback_query.data == "change_lang":
            buttons = [
                [
                    InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                    InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
                ]
            ]
            await callback_query.message.edit_text(
                get_text(user_id, "choose_lang"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
        elif callback_query.data.startswith("lang_"):
            lang = callback_query.data.split("_")[1]
            user_lang[user_id] = lang
            await callback_query.message.edit_text(
                get_text(user_id, "lang_changed"),
                reply_markup=get_start_keyboard(user_id)
            )
            
        elif callback_query.data == "start_convert":
            user_states[user_id] = {"step": "awaiting_type"}
            buttons = [
                [
                    InlineKeyboardButton(get_text(user_id, "pyro_to_tele"), callback_data="type_1"),
                    InlineKeyboardButton(get_text(user_id, "tele_to_pyro"), callback_data="type_2")
                ],
                [InlineKeyboardButton(get_text(user_id, "cancel"), callback_data="cancel")]
            ]
            
            await callback_query.message.edit_text(
                f"{get_text(user_id, 'convert_title')}\n\n{get_text(user_id, 'convert_options')}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
        elif callback_query.data == "help":
            await callback_query.message.edit_text(get_text(user_id, "help"))
            
        elif callback_query.data == "cancel":
            if user_id in user_states:
                del user_states[user_id]
            await callback_query.message.edit_text(get_text(user_id, "cancelled"))
            
        elif callback_query.data.startswith("type_"):
            if user_id not in user_states:
                await callback_query.answer(get_text(user_id, "start_over"), show_alert=True)
                return
                
            conversion_type = callback_query.data.split("_")[1]
            user_states[user_id].update({"type": conversion_type, "step": "awaiting_session"})
            
            await callback_query.message.edit_text(get_text(user_id, "send_session"))
            
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(str(e), show_alert=True)

@app.on_message(filters.text & filters.private)
async def handle_messages(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        if user_id not in user_states:
            return
            
        state = user_states[user_id]
        if state["step"] != "awaiting_session":
            return

        session_string = message.text.strip()
        
        try:
            if state["type"] == "1":  # Pyrogram to Telethon
                result = MangSession.PYROGRAM_TO_TELETHON(session_string)
                conversion_type = "Telethon" if user_lang.get(user_id) == "en" else "تيليثون"
            else:  # Telethon to Pyrogram
                result = MangSession.TELETHON_TO_PYROGRAM(session_string)
                conversion_type = "Pyrogram" if user_lang.get(user_id) == "en" else "بايروجرام"

            await message.delete()

            await message.reply_text(
                f"{get_text(user_id, 'converted_to').format(conversion_type)}\n\n"
                f"`{result}`\n\n"
                f"{get_text(user_id, 'security_note')}"
            )

        except Exception as e:
            await message.reply_text(get_text(user_id, "conversion_error").format(str(e)))
            await message.delete()
        
        finally:
            del user_states[user_id]
            
    except Exception as e:
        await message.reply_text(get_text(message.from_user.id, "error").format(str(e)))

print("Bot Started!")
app.run()