# Telegram to reMarkable Bot

> Hassle-free article delivery from Telegram to your reMarkable tablet

Send any article URL via Telegram and have it automatically converted to EPUB and delivered to your reMarkable tablet in ~30 seconds. No manual downloads, no cable connections, no hassle.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-☕-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white)](https://buymeacoffee.com/kairon)

## ✨ Features

- 📱 **Mobile-first workflow** - Share articles directly from your phone
- ⚡ **Instant delivery** - Article on your tablet in ~30 seconds
- 📚 **EPUB format** - Optimized for reMarkable reading experience
- 🤖 **Set it and forget it** - Runs 24/7, auto-restarts on failure
- 💰 **Free forever** - Runs on Google Cloud free tier
- 🔒 **Secure** - Your credentials stay private
- 🛠️ **Open source** - Fully customizable

## 🚀 Quick Start

### One-Command Setup

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/telegram-remarkable-bot/main/setup.sh | bash
```

That's it! The script will:
1. ✅ Install all dependencies
2. ✅ Set up rmapi and authenticate
3. ✅ Create your Telegram bot
4. ✅ Configure the service
5. ✅ Start the bot 24/7

**Setup time: ~15 minutes** (mostly waiting for you to get tokens)

---

## 📋 Prerequisites

- **reMarkable tablet** with cloud sync enabled
- **reMarkable Cloud subscription** (free trial or paid)
- **Telegram account**
- **Linux server** (Ubuntu/Debian recommended)
  - Google Cloud e2-micro (free tier) - [Setup guide](#google-cloud-setup)
  - Any VPS with 1 GB RAM
  - Raspberry Pi
  - Your own Linux machine

---

## 📖 Manual Setup

If you prefer to set up manually or want to understand what's happening:

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/telegram-remarkable-bot.git
cd telegram-remarkable-bot
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv git golang-go

# Install rmapi
git clone https://github.com/ddvk/rmapi.git
cd rmapi && go build && sudo mv rmapi /usr/local/bin/
cd ..
```

### Step 3: Authenticate reMarkable

```bash
rmapi
# Follow prompts:
# 1. Visit: https://my.remarkable.com/device/browser/connect
# 2. Get your 8-character code
# 3. Paste it when prompted
```

### Step 4: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Follow prompts to create your bot
4. Copy the bot token (format: `1234567890:ABCdef...`)

### Step 5: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Configure Service

```bash
# Create service file
sudo nano /etc/systemd/system/telegram-remarkable-bot.service
```

Paste this configuration (replace `YOUR_TOKEN` and `YOUR_USERNAME`):

```ini
[Unit]
Description=Telegram to reMarkable Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/telegram-remarkable-bot
Environment="TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE"
Environment="RMAPI_PATH=/usr/local/bin/rmapi"
Environment="REMARKABLE_FOLDER=/Articles"
ExecStart=/home/YOUR_USERNAME/telegram-remarkable-bot/venv/bin/python3 /home/YOUR_USERNAME/telegram-remarkable-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 7: Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable telegram-remarkable-bot

# Start service
sudo systemctl start telegram-remarkable-bot

# Check status
sudo systemctl status telegram-remarkable-bot
```

---

## 🎮 Usage

### Basic Commands

- `/start` - Welcome message and instructions
- `/help` - Show help information
- `/status` - Check bot status

### Sending Articles

Just send any article URL to your bot:

```
https://example.substack.com/p/article-title
```

The bot will:
1. Download the article
2. Extract the content
3. Convert to EPUB
4. Upload to your reMarkable
5. Notify you when complete

### Supported Sites

Works with most websites including:
- Substack newsletters
- Medium articles
- Blog posts
- News articles
- Any standard web page with article content

---

## 🔧 Management

### Check Status

```bash
sudo systemctl status telegram-remarkable-bot
```

### View Logs

```bash
# Live logs
sudo journalctl -u telegram-remarkable-bot -f

# Last 50 lines
sudo journalctl -u telegram-remarkable-bot -n 50
```

### Restart Bot

```bash
sudo systemctl restart telegram-remarkable-bot
```

### Stop Bot

```bash
sudo systemctl stop telegram-remarkable-bot
```

### Update Bot

```bash
cd ~/telegram-remarkable-bot
git pull
sudo systemctl restart telegram-remarkable-bot
```

---

## 🌐 Google Cloud Setup

### Create Free VM

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Compute Engine API
4. Create VM instance:
   - **Name:** telegram-bot
   - **Region:** us-east1, us-central1, or us-west1 (free tier only)
   - **Machine type:** e2-micro (free tier)
   - **Boot disk:** Ubuntu 22.04 LTS, 10 GB
   - **Firewall:** Allow HTTP/HTTPS traffic

5. SSH into your VM (click "SSH" button in console)
6. Run the setup script:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/telegram-remarkable-bot/main/setup.sh | bash
```

### Free Tier Details

**Google Cloud e2-micro includes:**
- 1 GB RAM
- 0.25-2 vCPU (burstable)
- 30 GB storage
- 1 GB network egress per month
- **Free forever** (not a trial)

**Limitations:**
- Only available in US regions (us-east1, us-central1, us-west1)
- Latency from Europe ~100-150ms (negligible for this use case)

---

## 📊 Resource Usage

**Typical usage (50 articles/month):**

| Resource | Usage | Free Tier Limit | Headroom |
|----------|-------|-----------------|----------|
| Memory | ~50 MB | 1024 MB | 95% free |
| Bandwidth | ~100 MB/month | 1024 MB/month | 90% free |
| CPU | <1% | 100% | 99% free |
| Storage | ~3 GB | 30 GB | 90% free |

**You'll use less than 10% of the free tier resources!**

---

## 🔒 Security

### Credentials

- ✅ Bot token stored as environment variable
- ✅ reMarkable token in `~/.rmapi` (not in repo)
- ✅ `.gitignore` prevents accidental commits
- ✅ Service file uses environment variables

### Best Practices

- Never commit tokens to git
- Keep your VM updated: `sudo apt update && sudo apt upgrade`
- Use firewall rules if exposing ports
- Rotate tokens periodically
- Monitor logs for unusual activity

---

## 🐛 Troubleshooting

### Bot won't start

```bash
# Check logs
sudo journalctl -u telegram-remarkable-bot -n 50

# Common issues:
# - Wrong token format
# - rmapi not authenticated
# - Python dependencies missing
```

### Authentication fails

```bash
# Re-authenticate rmapi
rm ~/.rmapi
rmapi

# Get fresh code from:
# https://my.remarkable.com/device/browser/connect
```

### Article extraction fails

- Some sites block automated access
- Try different article URL
- Check if site requires login
- View logs for specific error

### Upload fails

```bash
# Test rmapi connection
rmapi ls

# Re-authenticate if needed
rm ~/.rmapi && rmapi
```

### Service won't start after reboot

```bash
# Check if enabled
sudo systemctl is-enabled telegram-remarkable-bot

# Enable if needed
sudo systemctl enable telegram-remarkable-bot
```

---

## 🛠️ Development

### Project Structure

```
telegram-remarkable-bot/
├── bot.py                    # Main bot code
├── requirements.txt          # Python dependencies
├── setup.sh                  # Automated setup script
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── README.md                # This file
└── CONTRIBUTING.md          # Contribution guidelines
```

### Local Development

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/telegram-remarkable-bot.git
cd telegram-remarkable-bot

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_TOKEN="your-token"
export RMAPI_PATH="/usr/local/bin/rmapi"
export REMARKABLE_FOLDER="/Articles"

# Run bot
python3 bot.py
```

### Testing

```bash
# Send test message to your bot
# Check logs for errors
# Verify file appears on reMarkable
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ideas for contributions:**
- Support for more article sources
- PDF conversion option
- Custom folder organization
- Article metadata extraction
- Reading progress sync
- Batch article processing

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built with:**
- [ddvk/rmapi](https://github.com/ddvk/rmapi) - reMarkable Cloud API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API
- [trafilatura](https://github.com/adbar/trafilatura) - Web content extraction
- [ebooklib](https://github.com/aerkalov/ebooklib) - EPUB creation

**Inspired by:**
- [awesome-reMarkable](https://github.com/reHackable/awesome-reMarkable) - Community resources
- [RemarkablePocket](https://github.com/nov1n/RemarkablePocket) - Similar concept
- r/RemarkableTablet community

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/telegram-remarkable-bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/telegram-remarkable-bot/discussions)
- **Community:** [r/RemarkableTablet](https://www.reddit.com/r/RemarkableTablet/)

---

## 🗺️ Roadmap

**v1.0 (Current)**
- ✅ Basic article extraction
- ✅ EPUB conversion
- ✅ reMarkable upload
- ✅ Telegram bot interface
- ✅ systemd service
- ✅ Automated setup

**v1.1 (Planned)**
- [ ] PDF conversion option
- [ ] Custom folder selection
- [ ] Article metadata (author, date)
- [ ] Batch processing
- [ ] Better error messages

**v2.0 (Future)**
- [ ] Web interface
- [ ] Reading progress tracking
- [ ] Annotation sync
- [ ] Multi-user support
- [ ] Docker deployment

---

**Made with ❤️ for the reMarkable community**

**Star ⭐ this repo if you find it useful!**
