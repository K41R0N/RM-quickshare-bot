# Quick Start Guide

Get your Telegram to reMarkable bot running in 15 minutes!

## 🎯 What You Need

- [ ] reMarkable tablet with cloud sync
- [ ] Telegram account
- [ ] Linux server (Google Cloud free tier works great)

---

## ⚡ One-Command Setup

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/telegram-remarkable-bot/main/setup.sh | bash
```

The script will guide you through:

1. **System setup** (~2 min)
   - Updates packages
   - Installs dependencies
   - Builds rmapi

2. **reMarkable authentication** (~2 min)
   - Opens browser to get code
   - Authenticates with cloud
   - Tests connection

3. **Telegram bot creation** (~5 min)
   - You create bot with @BotFather
   - Copy token
   - Script configures everything

4. **Service setup** (~1 min)
   - Creates systemd service
   - Enables auto-start
   - Starts bot

5. **Done!** ✅
   - Bot running 24/7
   - Ready to receive articles
   - Auto-restarts on failure

---

## 📱 Using Your Bot

### First Time

1. Open Telegram
2. Search for your bot (the username you chose)
3. Send: `/start`
4. You'll see a welcome message!

### Sending Articles

Just paste any article URL:

```
https://k41r0n.substack.com/p/why-im-building-things-that-dont
```

**What happens:**
1. Bot replies: "⏳ Processing..."
2. Downloads and converts article
3. Uploads to your reMarkable
4. Sends: "✅ Success!"
5. Article appears in `/Articles` folder on your tablet

**Time:** ~30 seconds from send to tablet

---

## 🔧 Common Commands

### Check if bot is running

```bash
sudo systemctl status telegram-remarkable-bot
```

**Look for:** `Active: active (running)`

### View live logs

```bash
sudo journalctl -u telegram-remarkable-bot -f
```

**Press Ctrl+C to exit**

### Restart bot

```bash
sudo systemctl restart telegram-remarkable-bot
```

---

## ❓ Troubleshooting

### Bot not responding

```bash
# Check status
sudo systemctl status telegram-remarkable-bot

# View logs
sudo journalctl -u telegram-remarkable-bot -n 50
```

### Need to re-authenticate reMarkable

```bash
# Remove old token
rm ~/.rmapi

# Re-authenticate
rmapi
# Get fresh code from: https://my.remarkable.com/device/browser/connect
```

### After VM reboot

**Nothing!** The bot auto-starts. Just verify:

```bash
sudo systemctl status telegram-remarkable-bot
```

---

## 🎉 That's It!

Your bot is now:
- ✅ Running 24/7
- ✅ Auto-starting on reboot
- ✅ Auto-restarting on failure
- ✅ Ready to deliver articles

**Send it an article URL and enjoy reading on your reMarkable!**

---

## 📚 More Information

- **Full documentation:** [README.md](README.md)
- **Manual setup:** [README.md#manual-setup](README.md#manual-setup)
- **Google Cloud setup:** [README.md#google-cloud-setup](README.md#google-cloud-setup)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Questions?** [Open an issue](https://github.com/YOUR_USERNAME/telegram-remarkable-bot/issues)
