# VideoEncoder Bot

A Telegram bot for encoding and compressing videos using FFmpeg.

## About

VideoEncoder Bot is designed to help users compress large video files into smaller, data-efficient formats like H.264 or H.265. This is particularly useful for Telegram users who want to save mobile data or manage cloud storage more effectively. The bot features a robust queue system, customizable settings, and supports various utility functions like audio extraction and watermarking.

## Features

- Multi-user support with queue management.
- Dynamic settings panel for codecs, resolution, and audio.
- Fast multi-threaded downloading.
- Custom text and image watermarking.
- Video tools including audio extraction and screenshots.
- Administrative controls for chats and sudo users.

## Configuration

Set the following variables in a .env file:

- API_ID: Telegram API ID.
- API_HASH: Telegram API Hash.
- BOT_TOKEN: Bot token from BotFather.
- MONGO_URI: MongoDB connection string.
- OWNER_ID: Primary admin user ID.
- LOG_CHANNEL: Channel ID for system logs.
- EVERYONE_CHATS: Authorized group IDs.

## Deployment

1. Clone the repository:
   git clone https://github.com/KunalG932/encode-bot.git
   cd encode-bot

2. Install dependencies:
   pip install -r requirements.txt

3. Install FFmpeg on your system.

4. Run the bot:
   python3 -m VideoEncoder

## Disclaimer

This project is for educational purposes only. The developers are not responsible for any misuse of this tool. Users must comply with their local laws and Telegram's terms of service.

## Credits

Developed and maintained by Awakeners Bots.
Built using Pyrogram and FFmpeg.
