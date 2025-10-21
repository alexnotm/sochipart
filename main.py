from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Конфигурация ===
BOT_TOKEN = "8365794868:AAFOpP5lWnP0sKu9Mve3Nv12n8J_SKchkCw"
ADMIN_ID = 294491997  # Твой Telegram ID

# Словарь для хранения соответствий (кому админ отвечает)
reply_map = {}


# === Приветственное сообщение ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤝 Добро пожаловать в бот партнёров *Sochi Tech & Web3 Summit 2025*!\n\n"
        "Мы рады вашему интересу к сотрудничеству.\n\n"
        "Пожалуйста, укажите:\n"
        "• Название вашей компании / бренда\n"
        "• Формат партнёрства (спонсорство, стенд, промо, выступление и т.д.)\n"
        "• Контактное лицо и номер телефона / Telegram\n\n"
        "После отправки — менеджер свяжется с вами лично."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# === Основной обработчик сообщений ===
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user = msg.from_user

    # === 1️⃣ Если пишет партнёр ===
    if user.id != ADMIN_ID:
        who = user.username or user.full_name or f"id:{user.id}"
        text = msg.text or "(медиа)"
        print(f"[LOG] Сообщение от @{who}: {text}")

        try:
            # Пересылаем админу оригинальное сообщение
            forwarded = await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )

            # Добавляем подпись и сохраняем ID
            caption = f"🏢 Партнёр @{who} (id: {user.id})"
            note = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=caption,
                reply_to_message_id=forwarded.message_id
            )

            # Запоминаем связь (для обратного ответа)
            reply_map[note.message_id] = user.id
            reply_map[forwarded.message_id] = user.id

            # Отправляем подтверждение партнёру
            await msg.reply_text(
                "✅ Спасибо! Ваша заявка передана менеджеру отдела партнёрств. Мы свяжемся с вами в ближайшее время."
            )

        except Exception as e:
            print(f"⚠️ Ошибка при пересылке сообщения админу: {e}")

    # === 2️⃣ Если пишет админ ===
    elif msg.reply_to_message:
        target_id = None

        # Проверяем карту соответствий
        if msg.reply_to_message.message_id in reply_map:
            target_id = reply_map[msg.reply_to_message.message_id]
        elif (
            msg.reply_to_message.forward_origin
            and msg.reply_to_message.forward_origin.sender_user
        ):
            target_id = msg.reply_to_message.forward_origin.sender_user.id

        if target_id:
            try:
                await context.bot.send_message(chat_id=target_id, text=msg.text)
                print(f"[LOG] Ответ от админа → партнёру {target_id}: {msg.text}")
            except Exception as e:
                print(f"⚠️ Ошибка при отправке партнёру {target_id}: {e}")
        else:
            print("⚠️ Не удалось определить адресата для ответа.")


# === Запуск приложения ===
if __name__ == "__main__":
    print("🚀 SummitPartnerBot запускается...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handler))
    print("🤖 Бот готов и ожидает сообщений.")
    app.run_polling()
