#!/usr/bin/env python3
"""
Telegram to reMarkable Bot
Automatically sends Substack articles to your reMarkable tablet
"""

import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import trafilatura
from ebooklib import epub
import requests

# Configuration from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
RMAPI_PATH = os.getenv('RMAPI_PATH', '/usr/local/bin/rmapi')
REMARKABLE_FOLDER = os.getenv('REMARKABLE_FOLDER', '/Articles')

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def extract_article(url: str) -> dict:
    """
    Extract article content from URL using trafilatura
    
    Args:
        url: Article URL to extract
        
    Returns:
        dict with title, author, content, and url
    """
    try:
        logger.info(f"Extracting article from: {url}")
        
        # Download the webpage
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise Exception("Failed to download webpage")
        
        # Extract article content
        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_images=False,
            output_format='txt'
        )
        
        if not content:
            raise Exception("Failed to extract article content")
        
        # Extract metadata
        metadata = trafilatura.extract_metadata(downloaded)
        
        title = metadata.title if metadata and metadata.title else "Article"
        author = metadata.author if metadata and metadata.author else "Unknown"
        
        logger.info(f"Extracted: {title} by {author}")
        
        return {
            'title': title,
            'author': author,
            'content': content,
            'url': url
        }
        
    except Exception as e:
        logger.error(f"Error extracting article: {e}")
        raise


def create_epub(article: dict, output_path: str):
    """
    Create an EPUB file from article content
    
    Args:
        article: dict with title, author, content, url
        output_path: Path where EPUB file should be saved
    """
    try:
        logger.info(f"Creating EPUB: {article['title']}")
        
        # Create EPUB book
        book = epub.EpubBook()
        
        # Set metadata
        book.set_identifier(article['url'])
        book.set_title(article['title'])
        book.set_language('en')
        book.add_author(article['author'])
        
        # Create chapter
        chapter = epub.EpubHtml(
            title=article['title'],
            file_name='content.xhtml',
            lang='en'
        )
        
        # Format content as HTML
        html_content = f"""
        <h1>{article['title']}</h1>
        <p><em>By {article['author']}</em></p>
        <p><a href="{article['url']}">Original article</a></p>
        <hr/>
        """
        
        # Convert plain text to HTML paragraphs
        paragraphs = article['content'].split('\n\n')
        for para in paragraphs:
            if para.strip():
                html_content += f"<p>{para.strip()}</p>\n"
        
        chapter.set_content(html_content)
        
        # Add chapter to book
        book.add_item(chapter)
        
        # Create table of contents
        book.toc = (chapter,)
        
        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define spine
        book.spine = ['nav', chapter]
        
        # Write EPUB file
        epub.write_epub(output_path, book)
        logger.info(f"EPUB created: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating EPUB: {e}")
        raise


def upload_to_remarkable(epub_path: str) -> bool:
    """
    Upload EPUB file to reMarkable using rmapi
    
    Args:
        epub_path: Path to EPUB file to upload
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Uploading to reMarkable: {epub_path}")
        
        # Check if rmapi exists
        if not os.path.exists(RMAPI_PATH):
            raise Exception(f"rmapi not found at {RMAPI_PATH}")
        
        # Upload using rmapi
        result = subprocess.run(
            [RMAPI_PATH, 'put', epub_path, REMARKABLE_FOLDER],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("Upload successful!")
            return True
        else:
            logger.error(f"Upload failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Upload timed out")
        return False
    except Exception as e:
        logger.error(f"Error uploading to reMarkable: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🎉 Welcome to Telegram → reMarkable Bot!

📚 How to use:
1. Share any Substack article link with me
2. I'll extract the content and convert it to EPUB
3. Upload it to your reMarkable tablet
4. Read it on your tablet!

Just send me a URL to get started.

Commands:
/start - Show this message
/help - Show help
/status - Check bot status
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
📖 Help

Send me any article URL and I'll:
1. Extract the article content
2. Convert it to EPUB format
3. Upload to your reMarkable tablet

The article will appear in the "Articles" folder on your tablet.

Supported sites:
✅ Substack
✅ Medium
✅ Most blogs and news sites

Tips:
• Make sure your reMarkable is connected to WiFi
• Sync your tablet to see new articles
• Articles are uploaded to /Articles folder
"""
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status"""
    try:
        result = subprocess.run(
            [RMAPI_PATH, 'ls'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            status = "✅ Bot is operational!\n✅ reMarkable connection: OK"
        else:
            status = "⚠️ Bot is running but reMarkable connection failed"
            
    except Exception as e:
        status = f"❌ Error checking status: {str(e)}"
    
    await update.message.reply_text(status)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming URLs"""
    url = update.message.text.strip()
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            await update.message.reply_text("❌ Invalid URL. Please send a valid article link.")
            return
    except Exception:
        await update.message.reply_text("❌ Invalid URL. Please send a valid article link.")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("⏳ Processing article...")
    
    try:
        # Extract article
        await processing_msg.edit_text("📥 Downloading article...")
        article = extract_article(url)
        
        # Create EPUB
        await processing_msg.edit_text("📝 Converting to EPUB...")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp_file:
            epub_path = tmp_file.name
        
        create_epub(article, epub_path)
        
        # Upload to reMarkable
        await processing_msg.edit_text("📤 Uploading to reMarkable...")
        success = upload_to_remarkable(epub_path)
        
        # Clean up temporary file
        try:
            os.unlink(epub_path)
        except:
            pass
        
        if success:
            await processing_msg.edit_text(
                f"✅ Success!\n\n"
                f"📖 {article['title']}\n"
                f"✍️ By {article['author']}\n\n"
                f"Your article is now on your reMarkable tablet in the 'Articles' folder!"
            )
        else:
            await processing_msg.edit_text(
                "❌ Failed to upload to reMarkable. Please check the logs."
            )
            
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await processing_msg.edit_text(
            f"❌ Error processing article:\n{str(e)}\n\n"
            f"Please try another article or check if the URL is accessible."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-URL messages"""
    await update.message.reply_text(
        "Please send me an article URL to convert and upload to your reMarkable.\n\n"
        "Use /help for more information."
    )


def main():
    """Start the bot"""
    # Check if token is set
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        logger.error("Please set it with: export TELEGRAM_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Check if rmapi exists
    if not os.path.exists(RMAPI_PATH):
        logger.error(f"rmapi not found at {RMAPI_PATH}")
        logger.error("Please install rmapi: https://github.com/ddvk/rmapi")
        sys.exit(1)
    
    logger.info("Starting Telegram → reMarkable Bot...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # URL handler (matches http:// or https://)
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^https?://'),
        handle_url
    ))
    
    # Other text messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Start the Bot
    logger.info("Bot started! Waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
