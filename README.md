# Telegram Terminal Remote

A secure remote terminal access tool that runs locally on your PC and allows authorized Telegram users to execute terminal commands remotely.

## Security Features
- **No Open Ports**: Uses Telegram Bot API long polling.
- **Strict Authorization**: Only accepts commands from explicitly allowed Telegram User IDs in private chats.
- **Command Categorization**:
  - **Blocked**: Dangerous commands (e.g., `rm -rf /`, `format`) are rejected immediately.
  - **Confirm**: Risky commands (e.g., `rm`, `kill`, `pip install`) require a single-use, time-bound confirmation ID.
  - **Allowed**: Safe commands run immediately.
- **Timeout & Truncation**: Commands timeout after 30 seconds and output is truncated to fit Telegram's message limits.
- **Secure Logging**: Logs security events without leaking secrets or raw dangerous commands.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your `TELEGRAM_BOT_TOKEN` and `ALLOWED_USER_IDS`.

3. Run the app:
```bash
python main.py
```

## Usage
Send a message to your bot with the command you want to run (e.g., `ls -la` or `pwd`).
If a command requires confirmation, the bot will reply with a `/confirm <id>` command for you to tap.

_Note: Interactive commands (like `top`, `nano`, or `python` without arguments) will hang until the 30-second timeout is reached. Use non-interactive commands only._

## Verification
- **Static Inspection**: Passed. The code correctly implements the `python-telegram-bot` v20+ `Application.builder()` pattern.
- **Security Checks**: Passed. Secrets are loaded via `dotenv`, unauthorized users receive a minimal response, and dangerous commands are blocked without echoing the payload.
- **Execution**: To run this locally, you will need to create a Telegram bot via BotFather, get your User ID, populate the `.env` file, and run `python main.py`.


MIT