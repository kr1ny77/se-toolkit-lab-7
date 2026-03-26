import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from handlers.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
    handle_text,
)


def parse_input(text: str) -> tuple[str, list[str]]:
    parts = text.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def run_test_mode(command_text: str) -> None:
    command, args = parse_input(command_text)

    if command == "/start":
        print(handle_start())
        sys.exit(0)

    if command == "/help":
        print(handle_help())
        sys.exit(0)

    if command == "/health":
        print(handle_health())
        sys.exit(0)

    if command == "/labs":
        print(handle_labs())
        sys.exit(0)

    if command == "/scores":
        if args:
            print(handle_scores(args[0]))
        else:
            print(handle_scores())
        sys.exit(0)

    if command.startswith("/"):
        print(f"Unknown command: {command_text}")
        print("Use /help to see available commands.")
        sys.exit(0)

    print(handle_text(command_text))
    sys.exit(0)


def run_production_mode() -> None:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )

    if not config.bot_token:
        print("BOT_TOKEN is missing in .env.bot.secret")
        sys.exit(1)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("What labs are available?", callback_data="what labs are available?")],
            [InlineKeyboardButton("Show scores for lab 4", callback_data="show me scores for lab 4")],
            [InlineKeyboardButton("Lowest pass rate", callback_data="which lab has the lowest pass rate?")],
        ]
    )

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(handle_start(), reply_markup=keyboard)

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(handle_help())

    async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(handle_health())

    async def labs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(handle_labs())

    async def scores_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        if context.args:
            await update.message.reply_text(handle_scores(context.args[0]))
        else:
            await update.message.reply_text(handle_scores())

    async def text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(handle_text(update.message.text or ""))

    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        await query.message.reply_text(handle_text(query.data or ""))

    app = Application.builder().token(config.bot_token).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(CommandHandler("labs", labs_cmd))
    app.add_handler(CommandHandler("scores", scores_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))

    print("Bot started")
    app.run_polling()


def main() -> None:
    parser = argparse.ArgumentParser(description="SE Toolkit Lab 7 Telegram Bot")
    parser.add_argument("--test", type=str, metavar="COMMAND")
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_production_mode()


if __name__ == "__main__":
    main()
