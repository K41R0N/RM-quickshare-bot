#!/bin/bash
set -e

echo "================================================"
echo "Telegram to reMarkable Bot - Setup Script"
echo "================================================"
echo ""

# Check if running on supported OS
if [[ ! -f /etc/os-release ]]; then
    echo "❌ Error: Cannot detect OS. This script requires Ubuntu/Debian."
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
    echo "⚠️  Warning: This script is designed for Ubuntu/Debian."
    echo "   It may work on other distributions but is not tested."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ OS Check: $PRETTY_NAME"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv git golang-go curl

# Verify installations
echo "✅ Verifying installations..."
python3 --version
go version
git --version

# Install rmapi
echo ""
echo "📥 Installing rmapi..."
if [[ -f /usr/local/bin/rmapi ]]; then
    echo "✅ rmapi already installed"
else
    cd ~
    if [[ -d rmapi ]]; then
        echo "📁 rmapi directory exists, updating..."
        cd rmapi
        git pull
    else
        echo "📥 Cloning rmapi..."
        git clone https://github.com/ddvk/rmapi.git
        cd rmapi
    fi
    
    echo "🔨 Building rmapi..."
    go build
    
    echo "📦 Installing rmapi..."
    sudo mv rmapi /usr/local/bin/
    
    echo "✅ rmapi installed successfully"
fi

# Verify rmapi
which rmapi
rmapi version

# Authenticate rmapi
echo ""
echo "================================================"
echo "🔐 reMarkable Authentication"
echo "================================================"
echo ""
echo "You need to authenticate with your reMarkable Cloud account."
echo ""
echo "Steps:"
echo "1. Open this URL in your browser:"
echo "   https://my.remarkable.com/device/browser/connect"
echo ""
echo "2. Log in to your reMarkable account"
echo "3. Click 'Connect'"
echo "4. Copy the 8-character code"
echo "5. Come back here and paste it"
echo ""

# Check if already authenticated
if [[ -f ~/.rmapi ]]; then
    echo "✅ Found existing rmapi authentication"
    read -p "Test existing authentication? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        if rmapi ls > /dev/null 2>&1; then
            echo "✅ Authentication works!"
        else
            echo "❌ Authentication failed. Re-authenticating..."
            rm ~/.rmapi
            rmapi
        fi
    fi
else
    echo "🔑 Starting authentication..."
    rmapi
fi

# Verify authentication
echo ""
echo "✅ Testing rmapi connection..."
if rmapi ls > /dev/null 2>&1; then
    echo "✅ Successfully connected to reMarkable Cloud!"
else
    echo "❌ Failed to connect. Please run 'rmapi' manually to authenticate."
    exit 1
fi

# Set up project directory
echo ""
echo "================================================"
echo "📁 Setting up project directory"
echo "================================================"
echo ""

PROJECT_DIR="$HOME/telegram-remarkable-bot"

if [[ -d "$PROJECT_DIR" ]]; then
    echo "📁 Project directory already exists: $PROJECT_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        echo "❌ Aborted. Please remove or rename the existing directory."
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "✅ Created project directory: $PROJECT_DIR"

# Copy files (assumes script is run from repo directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📋 Copying files from: $SCRIPT_DIR"

cp "$SCRIPT_DIR/bot.py" "$PROJECT_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$PROJECT_DIR/"
cp "$SCRIPT_DIR/.gitignore" "$PROJECT_DIR/" 2>/dev/null || true

echo "✅ Files copied"

# Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

echo "✅ Virtual environment created"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Get Telegram bot token
echo ""
echo "================================================"
echo "🤖 Telegram Bot Setup"
echo "================================================"
echo ""
echo "You need to create a Telegram bot and get its token."
echo ""
echo "Steps:"
echo "1. Open Telegram and search for @BotFather"
echo "2. Send: /start"
echo "3. Send: /newbot"
echo "4. Follow the prompts to create your bot"
echo "5. Copy the bot token (format: 1234567890:ABCdef...)"
echo ""
read -p "Press Enter when you have your bot token..."
echo ""
read -p "Enter your Telegram bot token: " TELEGRAM_TOKEN

if [[ -z "$TELEGRAM_TOKEN" ]]; then
    echo "❌ Error: Token cannot be empty"
    exit 1
fi

# Validate token format (basic check)
if [[ ! "$TELEGRAM_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
    echo "⚠️  Warning: Token format looks incorrect"
    echo "   Expected format: 1234567890:ABCdef..."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Token received"

# Test bot
echo ""
echo "🧪 Testing bot..."
export TELEGRAM_TOKEN="$TELEGRAM_TOKEN"
timeout 10s python3 bot.py &
BOT_PID=$!
sleep 5

if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot started successfully!"
    kill $BOT_PID 2>/dev/null || true
else
    echo "❌ Bot failed to start. Check the error messages above."
    exit 1
fi

# Create systemd service
echo ""
echo "================================================"
echo "⚙️  Setting up systemd service"
echo "================================================"
echo ""

SERVICE_FILE="/etc/systemd/system/telegram-remarkable-bot.service"
USERNAME=$(whoami)

echo "Creating service file: $SERVICE_FILE"

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Telegram to reMarkable Bot
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$PROJECT_DIR
Environment="TELEGRAM_TOKEN=$TELEGRAM_TOKEN"
Environment="RMAPI_PATH=/usr/local/bin/rmapi"
Environment="REMARKABLE_FOLDER=/Articles"
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"

# Enable and start service
echo ""
echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-remarkable-bot
sudo systemctl start telegram-remarkable-bot

# Wait a moment for service to start
sleep 3

# Check service status
echo ""
echo "📊 Checking service status..."
if sudo systemctl is-active --quiet telegram-remarkable-bot; then
    echo "✅ Service is running!"
else
    echo "❌ Service failed to start. Checking logs..."
    sudo journalctl -u telegram-remarkable-bot -n 20
    exit 1
fi

# Final instructions
echo ""
echo "================================================"
echo "🎉 Setup Complete!"
echo "================================================"
echo ""
echo "Your Telegram to reMarkable bot is now running!"
echo ""
echo "✅ Bot is running 24/7"
echo "✅ Auto-starts on system reboot"
echo "✅ Auto-restarts on failure"
echo ""
echo "📱 Next Steps:"
echo ""
echo "1. Open Telegram and find your bot"
echo "2. Send: /start"
echo "3. Share any article URL"
echo "4. Check your reMarkable tablet!"
echo ""
echo "🔧 Useful Commands:"
echo ""
echo "  Check status:   sudo systemctl status telegram-remarkable-bot"
echo "  View logs:      sudo journalctl -u telegram-remarkable-bot -f"
echo "  Restart bot:    sudo systemctl restart telegram-remarkable-bot"
echo "  Stop bot:       sudo systemctl stop telegram-remarkable-bot"
echo ""
echo "📚 Documentation: See README.md for more information"
echo ""
echo "================================================"
echo ""
