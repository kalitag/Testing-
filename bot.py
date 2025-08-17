#!/usr/bin/env python3
"""
Telegram Product Scraper Bot - Simplified & Verified Implementation
"""

import os
import re
import time
import logging
from datetime import datetime

# Telegram bot framework
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)
from telegram import (
    InputMediaPhoto,
    Update
)

# Local modules
from config import BOT_TOKEN, MODE_ADVANCED, SCREENSHOT_DIR
from utils import setup_directories, format_output
from scraper import process_link

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global state
LAST_PROCESSED = {}

def setup_environment():
    """Setup the bot environment"""
    setup_directories()
    logger.info("Environment setup completed")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "🛒 Product Scraper Bot\n\n"
        "I automatically process product links from:\n"
        "• Amazon • Flipkart • Meesho • Myntra • Ajio • Snapdeal\n\n"
        "Commands:\n"
        "/advancing - Switch to High-Advanced Mode\n"
        "/off_advancing - Switch to Medium Mode\n"
        "/img - Regenerate last message with new screenshots"
    )

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode switching commands"""
    global MODE_ADVANCED
    command = update.effective_message.text
    
    if command == '/advancing':
        MODE_ADVANCED = True
        await update.effective_message.reply_text("✅ Switched to High-Advanced Mode\n\n"
                                                "• Full smart features enabled\n"
                                                "• Stock verification\n"
                                                "• Price optimization\n"
                                                "• Screenshot replacement\n"
                                                "• Advanced formatting")
    elif command == '/off_advancing':
        MODE_ADVANCED = False
        await update.effective_message.reply_text("✅ Switched to Medium Mode\n\n"
                                                "• Fast processing\n"
                                                "• Basic scraping\n"
                                                "• Minimal checks\n"
                                                "• Optimized for speed")
    else:
        await update.effective_message.reply_text("❌ Unknown command")

async def img_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Regenerate last message with new screenshots"""
    chat_id = update.effective_chat.id
    
    if chat_id not in LAST_PROCESSED:
        await update.effective_message.reply_text("❌ No previous link to process")
        return
    
    try:
        link_data = LAST_PROCESSED[chat_id]
        pin_code = "110001"  # In a real implementation, extract from message
        
        # Re-process the link to get new screenshots
        processed = process_link(link_data['link'], pin_code)
        if processed:
            # Format the output
            formatted_text = format_output(processed)
            
            # Send message with appropriate media
            if processed['images']:
                await update.effective_message.reply_photo(
                    photo=open(processed['images'][0], 'rb'),
                    caption=formatted_text
                )
                await update.effective_message.reply_text("✅ Screenshots updated")
            else:
                await update.effective_message.reply_text("❌ Could not generate screenshot")
        else:
            await update.effective_message.reply_text("❌ Could not regenerate message")
    except Exception as e:
        logger.error(f"Error regenerating screenshots: {str(e)}")
        await update.effective_message.reply_text(f"❌ Error updating screenshots: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages for product links"""
    message = update.effective_message
    chat_id = update.effective_chat.id
    
    # Skip if message doesn't contain links
    if not message.text and not message.caption:
        return
    
    # Extract text from message (caption for media messages)
    text = message.text or message.caption or ""
    
    # Find all links in the message
    links = re.findall(r'https?://[^\s]+', text)
    
    # Process each detected link
    for link in links:
        try:
            # Store the last processed link for /img command
            LAST_PROCESSED[chat_id] = {
                'link': link,
                'timestamp': time.time()
            }
            
            # Extract pin code if available
            pin_code = "110001"
            pin_match = re.search(r'pin\s*[:\-]?\s*(\d{6})', text, re.IGNORECASE)
            if pin_match:
                pin_code = pin_match.group(1)
            
            # Process the link
            processed = process_link(link, pin_code)
            if processed:
                # Format the output
                formatted_text = format_output(processed)
                
                # Send message with appropriate media
                if processed['images']:
                    await message.reply_photo(
                        photo=open(processed['images'][0], 'rb'),
                        caption=formatted_text
                    )
                else:
                    await message.reply_text(formatted_text)
            else:
                await message.reply_text(f"❌ Could not process link: {link}")
                
        except Exception as e:
            logger.error(f"Error processing link {link}: {str(e)}")
            await message.reply_text(f"❌ Error processing link: {str(e)}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Setup environment
    setup_environment()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("advancing", mode_command))
    application.add_handler(CommandHandler("off_advancing", mode_command))
    application.add_handler(CommandHandler("img", img_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.CAPTION, 
        handle_message
    ))
    
    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
