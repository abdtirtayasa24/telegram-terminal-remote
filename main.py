import html
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from app.config import TELEGRAM_BOT_TOKEN
from app.security import is_authorized, categorize_command, create_confirmation, get_and_clear_confirmation
from app.command_runner import run_command
from app.audit import log_event, log_security_alert

async def check_auth(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    
    if not is_authorized(user.id, chat.type):
        log_security_alert(user.id if user else 0, "Unauthorized access attempt")
        await update.message.reply_text("Unauthorized.")
        return False
    return True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return
    
    command = update.message.text.strip()
    user_id = update.effective_user.id

    if not command:
        return
    
    category = categorize_command(command)

    if category == "BLOCKED":
        log_security_alert(user_id, "Attempted blocked command")
        await update.message.reply_text("Command blocked by security policy.")
        return
    
    if category == "CONFIRM":
        confirm_id = create_confirmation(user_id, command)
        log_event("Command requires confirmation", user_id, f"Confirm ID: {confirm_id}")
        await update.message.reply_text(
            f"Command requires confirmation.\nReply with: <code>/confirm {confirm_id}</code>",
            parse_mode="HTML"
        )
        return
    
    log_event("Executing command", user_id, "Allowed command executed")
    await execute_and_reply(update, command)

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update):
        return

    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Usage: /confirm <confirmation_id>")
        return

    confirm_id = context.args[0]
    command = get_and_clear_confirmation(confirm_id, user_id)

    if not command:
        log_security_alert(user_id, f"Invalid or expired confirmation ID: {confirm_id}")
        await update.message.reply_text("Invalid or expired confirmation ID.")
        return

    log_event("Executing confirmed command", user_id, f"Confirm ID: {confirm_id}")
    await execute_and_reply(update, command)

async def execute_and_reply(update: Update, command: str):
    status_msg = await update.message.reply_text("Running...")
    
    output = run_command(command)
    escaped_output = html.escape(output)
    
    # Format output in an HTML code block to avoid Markdown parsing errors
    formatted_output = f"<pre><code class='language-text'>{escaped_output}</code></pre>"
    
    try:
        await status_msg.edit_text(formatted_output, parse_mode="HTML")
    except Exception as e:
        log_security_alert(update.effective_user.id, f"Failed to send output: {e}")
        await status_msg.edit_text("Error: Output could not be sent (possibly too long or invalid format).")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # CommandHandler must be added first so it intercepts /confirm
    application.add_handler(CommandHandler("confirm", handle_confirm))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    log_event("Agent started", 0, "Bot is polling for updates")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()