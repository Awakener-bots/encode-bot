<p align="center">
  <img src="https://i.ibb.co/xqYbMC4r/photo-2026-01-21-17-17-28-7605970855935344672.jpg" alt="VideoEncoder Bot Banner" width="100%">
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&pause=1000&color=00BFFF&center=true&vCenter=true&width=600&lines=Advanced+Encoder+Bot" alt="Typing SVG" />
</p>

# 🎬 VideoEncoder Bot
# 🎬 VideoEncoder Bot

A powerful and efficient Telegram bot for encoding, compressing, and optimizing videos using **FFmpeg**.

---

## 🚀 About

**VideoEncoder Bot** helps Telegram users compress large video files into smaller, data-efficient formats such as **H.264 (AVC)** and **H.265 (HEVC)**.

It is ideal for:

- Saving mobile data 📉  
- Reducing cloud storage usage ☁️  
- Uploading large files within Telegram limits  
- Managing automated encoding workflows  

The bot includes a smart queue system, customizable encoding settings, and multiple video utility tools — optimized for multi-user environments.

---

## ✨ Features

- 👥 Multi-user support with advanced queue management  
- ⚙️ Dynamic settings panel (Codec, Resolution, Audio bitrate)  
- 🚀 Fast multi-threaded downloading  
- 🖼️ Custom watermarking  
  - Text watermark  
  - Image watermark  
- 🎧 Audio extraction tool  
- 📸 Screenshot generator  
- 🔐 Admin controls  
  - Sudo users  
  - Authorized chats  
  - Log system  
- 🗂️ MongoDB-based persistent settings  

---

## 🛠 Tech Stack

- **Pyrogram** – Telegram MTProto API Framework  
- **FFmpeg** – Video processing engine  
- **MongoDB** – Database storage  

---

## ⚙️ Configuration

Create a `.env` file in the root directory and add:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=your_mongodb_uri
OWNER_ID=your_user_id
LOG_CHANNEL=your_log_channel_id
EVERYONE_CHATS=authorized_group_ids
```

### 🔎 Variable Details

| Variable | Description |
|----------|------------|
| API_ID | Telegram API ID |
| API_HASH | Telegram API Hash |
| BOT_TOKEN | Bot token from BotFather |
| MONGO_URI | MongoDB connection string |
| OWNER_ID | Main admin Telegram ID |
| LOG_CHANNEL | Channel ID for bot logs |
| EVERYONE_CHATS | Group IDs allowed to use the bot |

---

## 📦 Deployment

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/KunalG932/encode-bot.git
cd encode-bot
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Install FFmpeg

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

### 4️⃣ Run the Bot

```bash
python3 -m VideoEncoder
```

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.

The developer and maintainers are not responsible for:

- Copyright violations  
- Misuse of the bot  
- Telegram Terms of Service violations  

Users must comply with their local laws and Telegram policies.

---

## 👨‍💻 Credits

**Developer:**  
Kunal  
🔗 https://github.com/KunalG932  

**Maintained By:**  
Awakeners Bots  
🔗 https://t.me/Awakeners_Bots  

---

## ⭐ Support the Project

If you like this project:

- ⭐ Give the repository a star  
- 🍴 Fork it  
- 🛠 Contribute improvements  
- 📢 Share it with others  

Your support motivates us to build more powerful tools ❤️
