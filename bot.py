from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ===== CONFIG =====
TOKEN = "8309027727:AAFFr6236nfqi_j-aS4bT26ieMKu_EOTCwU"
ADMIN_ID = 2135565117
UPI_ID = "sutradharakbishal-1@okaxis"
QR_IMAGE = "QR.jpg"


# ===== PAYMENT INFO =====
async def send_payment_info(message):
    await message.reply_text(
        "👋 *Welcome to YT by Bishal Xtreme*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💳 *How It Works*\n\n"
        "📌 *Step 1:* Copy the UPI ID or scan the QR code to pay\n"
        "📌 *Step 2:* Take a screenshot of the payment\n"
        "📌 *Step 3:* Upload the screenshot here for verification\n\n"
        "⏳ *Your channel will be promoted once payment is confirmed.*",
        parse_mode="Markdown"
    )

    await message.reply_photo(
        photo=open(QR_IMAGE, "rb"),
        caption=(
            "📷 *Scan QR or copy UPI ID*\n\n"
            f"`{UPI_ID}`\n\n"
            "⚠️ Make sure payment is successful before uploading the screenshot."
        ),
        parse_mode="Markdown"
    )


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_payment_info(update.message)


# ===== RECEIVE PAYMENT SCREENSHOT =====
async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id

    user_id = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "No username"
    profile = f"tg://user?id={user_id}"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    ]])

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=(
            "💰 *Payment Screenshot*\n\n"
            f"👤 *Name:* {name}\n"
            f"🔗 *Username:* {username}\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"👉 *Profile:* [Open Chat]({profile})"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await update.message.reply_text("⏳ Please wait for verification.")


# ===== ADMIN APPROVE / REJECT =====
async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    old_caption = query.message.caption or ""

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ *Payment Approved!*\n\n📺 Please send your YouTube channel link.",
            parse_mode="Markdown"
        )

        await query.edit_message_caption(
            old_caption + "\n\n✅ *Payment Approved*",
            parse_mode="Markdown"
        )

    else:
        retry_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Start Again", callback_data="restart")
        ]])

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ *Payment Rejected.*\n\nPlease try again.",
            parse_mode="Markdown",
            reply_markup=retry_btn
        )

        await query.edit_message_caption(
            old_caption + "\n\n❌ *Payment Rejected*",
            parse_mode="Markdown"
        )


# ===== RECEIVE YOUTUBE CHANNEL LINK =====
async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    link = update.message.text

    if "youtube.com" not in link and "youtu.be" not in link:
        return

    user_id = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "No username"
    profile = f"tg://user?id={user_id}"

    await update.message.reply_text(
        f"📺 *Channel received:*\n`{link}`\n\n⏳ Please wait.",
        parse_mode="Markdown"
    )

    notify_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("📢 Notify User (Pinned)", callback_data=f"notify_{user_id}")
    ]])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📌 *YouTube Channel Submission*\n\n"
            f"👤 *Name:* {name}\n"
            f"🔗 *Username:* {username}\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"👉 *Profile:* [Open Chat]({profile})\n\n"
            f"📺 *Channel Link:*\n`{link}`"
        ),
        parse_mode="Markdown",
        reply_markup=notify_btn
    )


# ===== ADMIN NOTIFY USER =====
async def notify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, user_id = query.data.split("_")
    user_id = int(user_id)

    old_text = query.message.text or ""

    restart_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("📌 Pin Again", callback_data="restart")
    ]])

    await context.bot.send_message(
    chat_id=user_id,
    text=(
        "✅ *Your promotion is live!*\n\n"
        "🔎 Please open the video/stream to verify your link.\n\n"
        "⚠️ If you face any issue, contact @playstudiohub\n\n"
        "📢 Want to promote *any social media link* or any kind of promotion on my channel?\n"
        "👉 Please contact @playstudiohub"
    ),
    parse_mode="Markdown",
    reply_markup=restart_btn
)


# ===== RESTART =====
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_payment_info(query.message)


# ===== RUN BOT =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, receive_screenshot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel))
app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
app.add_handler(CallbackQueryHandler(notify_user, pattern="^notify_"))
app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

if __name__ == "__main__":
    app.run_polling()