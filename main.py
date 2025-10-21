import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "8365794868:AAFOpP5lWnP0sKu9Mve3Nv12n8J_SKchkCw").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

if not ADMIN_ID.isdigit():
    ADMIN_ID = "294491997"  # твой Telegram ID (на случай, если не задано через Railway)
ADMIN_ID = int(ADMIN_ID)

# Память соответствий: { message_id_админа: user_id_партнёра }
reply_map = {}

# === Приветствие ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤝 Добро пожаловать в бот партнёров *Sochi Tech & Web3 Summit 2025*!\n\n"
        "Мы рады вашему интересу к сотрудничеству.\n\n"
        "Пожалуйста, укажите название вашего бренда, компанию и кратко опишите формат "
        "партнёрства, который вам интересен (спонсорство, стенд, выступление, промо и т.д.)."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# === Основной обработчик ===
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user = msg.from_user

    # --- 1️⃣ Сообщение от партнёра
    if user.id != ADMIN_ID:
        who = user.username or user.full_name or f"id:{user.id}"
        text = msg.text or "(медиа)"
        print(f"[LOG] Сообщение от @{who}: {text}")

        try:
            # Пересылаем админу оригинал
            forwarded = await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )

            # Подпись
            caption = f"🏢 Партнёр @{who} (id: {user.id})"
            note = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=caption,
                reply_to_message_id=forwarded.message_id
            )

            # сохраняем связь (ответ админу -> исходный партнёр)
            reply_map[note.message_id] = user.id
            reply_map[forwarded.message_id] = user.id

        except Exception as e:
            print(f"⚠️ Ошибка при пересылке: {e}")

    # --- 2️⃣ Ответ администратора партнёру
    elif msg.reply_to_message:
        target_id = None

        # ищем ID по карте
        if msg.reply_to_message.message_id in reply_map:
            target_id = reply_map[msg.reply_to_message.message_id]

        # если Telegram передал forward_origin
        elif msg.reply_to_message.forward_origin and msg.reply_to_message.forward_origin.sender_user:
            target_id = msg.reply_to_message.forward_origin.sender_user.id

        if target_id:
            try:
                await context.bot.send_message(chat_id=target_id, text=msg.text)
                print(f"[LOG] Ответ админу → партнёру {target_id}: {msg.text}")
            except Exception as e:
                print(f"⚠️ Ошибка при ответе партнёру {target_id}: {e}")
        else:
            print("⚠️ Не удалось определить, кому отправить ответ.")


# === Запуск ===
if __name__ == "__main__":
    print("🚀 SummitPartnerBot запускается...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handler))
    print("🤖 Бот готов и ожидает сообщения.")
    app.run_polling()
