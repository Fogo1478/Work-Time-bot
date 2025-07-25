# import logging
# import asyncio
# import csv
# import tempfile
# from aiogram import Bot, Dispatcher, F
# from aiogram.enums import ParseMode
# from aiogram.client.default import DefaultBotProperties
# from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
# from datetime import datetime
# import pytz
#
# # 🔐 TOKEN va ID lar
# TOKEN = "7759525886:AAHKP7U-hU1Q-Qxs2XmZ8_ZQm6D-WqcDwBc"
# admin_id = 7530522892
# # log_chat_id = -1002143893100  # Agar kerak bo‘lsa, aktivlashtiring
#
# # Vaqt zonasi
# tz = pytz.timezone("Asia/Tashkent")
# logging.basicConfig(level=logging.INFO)
#
# bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()
#
# # Hodimlar ro'yxati
# employee_names = {
#     5171756780: "Zokir",
#     5917861933: "Yusuf",
#     5149506457: "Umid",
# }
#
# # Klaviaturalar
# only_start_keyboard = ReplyKeyboardMarkup(
#     keyboard=[[KeyboardButton(text="📥 Ishga keldim")]],
#     resize_keyboard=True
# )
#
# full_keyboard = ReplyKeyboardMarkup(
#     keyboard=[[KeyboardButton(text="📤 Ishdan chiqdim")]],
#     resize_keyboard=True
# )
#
# admin_keyboard = ReplyKeyboardMarkup(
#     keyboard=[[KeyboardButton(text="📊 Hisobot")]],
#     resize_keyboard=True
# )
#
# # Holatlarni saqlash
# user_states = {}
# user_times = {}
# used_video_ids = {}
# logs = []
#
# # /start komandasi
# @dp.message(F.text == "/start")
# async def start_handler(msg: Message):
#     if msg.from_user.id == admin_id:
#         await msg.reply("👋 Assalomu alekum Ibrohim aka:", reply_markup=admin_keyboard)
#     else:
#         await msg.reply(
#             f"👋 Assalomu alaykum, {msg.from_user.full_name}!\n"
#             "Quyidagi tugmalar orqali ish vaqtini belgilashingiz mumkin.",
#             reply_markup=only_start_keyboard
#         )
#
# # 📥 Ishga keldim
# @dp.message(F.text == "📥 Ishga keldim")
# async def start_work(msg: Message):
#     user_id = msg.from_user.id
#     user_states[user_id] = "start"
#     await msg.reply("📹 Dumaloq video yuboring.", reply_markup=only_start_keyboard)
#
# # 📤 Ishdan chiqdim
# @dp.message(F.text == "📤 Ishdan chiqdim")
# async def end_work(msg: Message):
#     user_id = msg.from_user.id
#     now = datetime.now(tz)
#     now_str = now.strftime("%Y-%m-%d %H:%M:%S")
#
#     times = user_times.get(user_id)
#     if not times or not isinstance(times.get("start"), datetime):
#         await msg.reply("⚠️ Iltimos, avval '📥 Ishga keldim' tugmasini bosib dumaloq video yuboring.",
#                         reply_markup=only_start_keyboard)
#         return
#
#     times["end"] = now
#     delta = times["end"] - times["start"]
#     soat = delta.seconds // 3600
#     minut = (delta.seconds % 3600) // 60
#
#     logs.append({
#         "user": msg.from_user.full_name,
#         "user_id": user_id,
#         "start": times["start"].strftime("%Y-%m-%d %H:%M:%S"),
#         "end": now_str,
#         "duration": f"{soat} soat {minut} daqiqa"
#     })
#
#     await msg.reply(f"✅ Bugun ishlagan vaqt: <b>{soat} soat {minut} daqiqa</b>", reply_markup=only_start_keyboard)
#
#     user_states.pop(user_id, None)
#     user_times.pop(user_id, None)
#
# # Dumaloq video (faqat ishga kelganda)
# @dp.message(F.video_note)
# async def handle_video_note(msg: Message):
#     user_id = msg.from_user.id
#     video = msg.video_note
#     unique_id = video.file_unique_id
#
#     if msg.forward_date or msg.forward_from or msg.forward_sender_name:
#         await msg.reply("❌ Forward qilingan video yuborish mumkin emas.")
#         return
#
#     if user_id in used_video_ids and unique_id in used_video_ids[user_id]:
#         await msg.reply("⚠️ Bu video allaqachon qabul qilingan.")
#         return
#
#     state = user_states.get(user_id)
#     if not state:
#         await msg.reply("⛔ Iltimos, tugmalardan foydalaning.", reply_markup=only_start_keyboard)
#         return
#
#     used_video_ids.setdefault(user_id, set()).add(unique_id)
#     now = datetime.now(tz)
#     now_str = now.strftime("%Y-%m-%d %H:%M:%S")
#     user_name = employee_names.get(user_id, msg.from_user.full_name)
#
#     if state == "start":
#         user_times[user_id] = {"start": now}
#         await msg.reply(f"✅ Ishga kelgan vaqt: <b>{now_str}</b>", reply_markup=full_keyboard)
#
#         # Guruhga video va vaqt
#         await bot.send_video_note(chat_id=log_chat_id, video_note=video.file_id)
#         await bot.send_message(chat_id=log_chat_id, text=f"👤 {user_name}\n🕒 {now_str}")
#
#         # Admin uchun to‘liq ma’lumot
#         await bot.send_message(admin_id,
#             f"👤 <b>{user_name}</b>\n"
#             f"🕒 Ishga keldi: <b>{now_str}</b>"
#         )
#
# # 📊 Hisobot
# @dp.message(F.text == "📊 Hisobot")
# async def report_handler(msg: Message):
#     if msg.from_user.id != admin_id:
#         await msg.reply("⛔ Sizda bu amal uchun ruxsat yo‘q.")
#         return
#
#     if not logs:
#         await msg.reply("🗃 Hozircha hech qanday log mavjud emas.")
#         return
#
#     with tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, suffix='.csv') as csvfile:
#         fieldnames = ['Foydalanuvchi', 'Ishga kelgan', 'Ishdan chiqqan', 'Ishlagan vaqt']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for log in logs:
#             writer.writerow({
#                 'Foydalanuvchi': log['user'],
#                 'Ishga kelgan': log['start'],
#                 'Ishdan chiqqan': log['end'],
#                 'Ishlagan vaqt': log['duration']
#             })
#         file_path = csvfile.name
#
#     await bot.send_document(chat_id=admin_id, document=FSInputFile(file_path), caption="📊 Ish vaqti hisobot")
#
# # Botni ishga tushurish
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())


import os
from fastapi import FastAPI
import uvicorn

import logging
import asyncio
import csv
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from datetime import datetime
import pytz

# 🔐 TOKEN va ID lar

TOKEN = "7759525886:AAGC1tfv3pFGB_qkPtfJ7UZ2-K38K4mIsGU"

admin_id = 2028247200
log_chat_id = -1002143893100  # Faollashtirildi

# Vaqt zonasi
tz = pytz.timezone("Asia/Tashkent")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

app = FastAPI()

# Hodimlar ro'yxati
employee_names = {
    5171756780: "Zokir",
    5917861933: "Yusuf",
    5149506457: "Umid",
}

# Klaviaturalar
only_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📥 Ishga keldim")]],
    resize_keyboard=True
)

full_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📤 Ishdan chiqdim")]],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📊 Hisobot")]],
    resize_keyboard=True
)

# Holatlarni saqlash
user_states = {}
user_times = {}
used_video_ids = {}
logs = []

# /start komandasi
@dp.message(F.text == "/start")
async def start_handler(msg: Message):
    if msg.from_user.id == admin_id:
        await msg.reply("👋 Assalomu alekum Okala :", reply_markup=admin_keyboard)
    else:
        await msg.reply(
            f"👋 Assalomu alaykum, {msg.from_user.full_name}!\n"
            "Quyidagi tugmalar orqali ish vaqtini belgilashingiz mumkin.",
            reply_markup=only_start_keyboard
        )

# 📥 Ishga keldim
@dp.message(F.text == "📥 Ishga keldim")
async def start_work(msg: Message):
    user_id = msg.from_user.id
    now = datetime.now(tz)
    if now.hour > 9 or (now.hour == 9 and now.minute > 0):
        user_states[user_id] = "awaiting_reason_late"
        await msg.reply("⏰ Atlet nime kech kelding?:")
        return
    user_states[user_id] = "start"
    await msg.reply("📹 Dumaloq video yuboring.", reply_markup=only_start_keyboard)

# 📤 Ishdan chiqdim
@dp.message(F.text == "📤 Ishdan chiqdim")
async def end_work(msg: Message):
    user_id = msg.from_user.id
    now = datetime.now(tz)

    # 18:00 dan oldin chiqayotganlar uchun sabab so‘rash
    if now.hour < 18:
        user_states[user_id] = "awaiting_reason_early"
        await msg.reply("❗ Nimaga 18:00 bomadiku qatga ketvosan?:")
        return

    await finalize_checkout(msg, now)

# Dumaloq video (faqat ishga kelganda)
@dp.message(F.video_note)
async def handle_video_note(msg: Message):
    user_id = msg.from_user.id
    video = msg.video_note
    unique_id = video.file_unique_id

    if msg.forward_date or msg.forward_from or msg.forward_sender_name:
        await msg.reply("❌ Forward qilingan videoligin bilvoldimku davay yengisin yubor.")
        return

    if user_id in used_video_ids and unique_id in used_video_ids[user_id]:
        await msg.reply("⚠️ Mani Lox db oyladinmi man faqat yangi vd qabul qilaman.")
        return

    state = user_states.get(user_id)
    if not state or state != "start":
        await msg.reply("⛔ Iltimos, faqat tugmalardan foydalaning.", reply_markup=only_start_keyboard)
        return

    used_video_ids.setdefault(user_id, set()).add(unique_id)
    now = datetime.now(tz)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    user_name = employee_names.get(user_id, msg.from_user.full_name)

    if state == "start":
        user_times[user_id] = {"start": now}
        await msg.reply(f"✅ Ishga kelgan vaqt: <b>{now_str}</b>", reply_markup=full_keyboard)

        # Guruhga video va vaqt
        await bot.send_video_note(chat_id=log_chat_id, video_note=video.file_id)
        await bot.send_message(chat_id=log_chat_id, text=f"👤 {user_name}\n🕒 {now_str}")

        # Admin uchun to‘liq ma’lumot
        await bot.send_message(admin_id,
            f"👤 <b>{user_name}</b>\n"
            f"🕒 Ishga keldi: <b>{now_str}</b>"
        )

# 📊 Hisobot
@dp.message(F.text == "📊 Hisobot")
async def report_handler(msg: Message):
    if msg.from_user.id != admin_id:
        await msg.reply("San kimsan sanga Hisob berishim kere? ⛔.")
        return

    if not logs:
        await msg.reply("🗃 Hozircha hech qanday log mavjud emas.")
        return

    with tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, suffix='.csv') as csvfile:
        fieldnames = ['Foydalanuvchi', 'Ishga kelgan', 'Ishdan chiqqan', 'Ishlagan vaqt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            writer.writerow({
                'Foydalanuvchi': log['user'],
                'Ishga kelgan': log['start'],
                'Ishdan chiqqan': log['end'],
                'Ishlagan vaqt': log['duration']
            })
        file_path = csvfile.name

    await bot.send_document(chat_id=admin_id, document=FSInputFile(file_path), caption="📊 Ish vaqti hisobot")

# Primecheniye sabablarini qabul qilish
@dp.message()
async def handle_reason(msg: Message):
    user_id = msg.from_user.id
    state = user_states.get(user_id)

    if state == "awaiting_reason_late":
        await msg.reply("✅ Rahmat! Dumolo vd tashachi.", reply_markup=only_start_keyboard)
        user_states[user_id] = "start"
        await bot.send_message(admin_id,
            f"⚠️ <b>{employee_names.get(user_id, msg.from_user.full_name)}</b> kech keldi.\n"
            f"📌 Sabab: <i>{msg.text}</i>"
        )

    elif state == "awaiting_reason_early":
        await bot.send_message(admin_id,
            f"⚠️ <b>{employee_names.get(user_id, msg.from_user.full_name)}</b> 18:00 dan oldin ishdan qochib ketdi.\n"
            f"📌 Sabab: <i>{msg.text}</i>"
        )
        user_states.pop(user_id, None)
        await finalize_checkout(msg, datetime.now(tz))

# Chiqish jarayonini yakunlash
async def finalize_checkout(msg: Message, now: datetime):
    user_id = msg.from_user.id
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    times = user_times.get(user_id)
    # if not times or not isinstance(times.get("start"), datetime):
    #     await msg.reply("⚠️ Iltimos, avval '📥 Ishga keldim' tugmasini bosib dumaloq video yuboring.",
    #                     reply_markup=only_start_keyboard)
    #     return

    times["end"] = now or 0
    delta = times["end"] - times["start"]
    soat = delta.seconds // 3600
    minut = (delta.seconds % 3600) // 60

    logs.append({
        "user": msg.from_user.full_name,
        "user_id": user_id,
        "start": times["start"].strftime("%Y-%m-%d %H:%M:%S"),
        "end": now_str,
        "duration": f"{soat} soat {minut} daqiqa"
    })

    await msg.reply(f"✅ Bugun ishlagan vaqt: <b>{soat} soat {minut} daqiqa</b>", reply_markup=only_start_keyboard)

    user_states.pop(user_id, None)
    user_times.pop(user_id, None)

# Botni ishga tushurish
async def main():
    await dp.start_polling(bot)




# if __name__ == "__main__":
#     asyncio.run(main())

@app.get("/")
def root():
    return {"status": "bot is running"}

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

