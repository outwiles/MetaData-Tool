# Metadata Extractor Bot

<p align="center">
  <img src="assets/metadata.png" alt="Metadata Extractor Bot" width="420">
</p>

<p align="center">
  <b>🔍 Extract hidden metadata and EXIF information from images directly in Telegram.</b>
</p>

ACTIVE BOT LINK: https://t.me/MetadataExtractBot

## ✨ Features

- 📷 Extracts EXIF and image metadata
- 📱 Camera and device information
- 📅 Date and time information
- 📐 Image dimensions and resolution
- 🔭 Lens, ISO, aperture and shutter speed (when present in EXIF)
- 📍 GPS coordinates when available
- 🗺️ Google Maps location links for GPS metadata
- 📄 Supports Telegram photos and image documents
- ⚡ Asynchronous processing for fast responses
- 🔐 Private-message only operation
- 📢 Force-join protection (channel + backup)
- ☁️ Ready for deployment on Render

## 🚀 Deployment

### 1. Clone the repository

```bash
git clone https://github.com/outwiles/MetaData-Tool.git
cd MetaData-Tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set the bot token

Set the `BOT_TOKEN` environment variable with your Telegram bot token.

### 4. Run

```bash
python bot.py
```

## 🤖 Usage

- `/start` — greets the user and checks channel membership
- Send a photo or an image file (document) in a private chat with the bot to receive its extracted metadata

For maximum metadata preservation, send the image as a **document/file** rather than a compressed photo — Telegram strips most EXIF data from regular photo uploads.

## ☁️ Render

This project includes `render.yaml` for Render deployment.

Add the following environment variable:

```text
BOT_TOKEN=your_telegram_bot_token
```

The application also exposes a lightweight Flask health endpoint at `/health` (and `/`) for uptime monitoring.

## 📦 Project Structure

```text
.
├── assets/
│   └── metadata.png
├── bot.py
├── requirements.txt
├── render.yaml
├── .python-version
├── LICENCE
└── README.md
```

## 🛠️ Requirements

- Python 3.11+
- Telegram Bot Token
- Pillow
- python-telegram-bot
- Flask

## 🔒 Privacy

Metadata is processed only to generate the requested result and is not stored — files are deleted immediately after processing. Users should avoid uploading images containing sensitive information they do not want processed.

## 📜 License

This project is released under the MIT License. See [`LICENCE`](LICENCE) for details.

---

Credits

<p align="center">
  <b>Developed by Aashu</b><br/><br/>
  <a href="https://t.me/outwiles">
    <img src="https://img.shields.io/badge/Telegram-@outwiles-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram" />
  </a>
  <a href="https://github.com/outwiles">
    <img src="https://img.shields.io/badge/GitHub-@outwiles-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="mailto:outwiles@proton.me">
    <img src="https://img.shields.io/badge/Mail-outwiles%40proton.me-D14836?style=for-the-badge&logo=protonmail&logoColor=white" alt="Mail" />
  </a>
</p>
