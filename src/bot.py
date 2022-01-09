import logging
import os
from config import config

from app.twitter_client import TwitterClient
from app.reddit_client import RedditClient

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

TOKEN = config.TELEGRAM_CONFIG["bot_token"]


import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def send_pictures(update: Update, context: CallbackContext) -> None:

    input_message = update.message.text
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    
    image_folder = config.GLOBAL_CONFIG['image_folder']

    # TODO create only once
    if not os.path.exists(image_folder):
        os.mkdir(image_folder)

    # Download images using clients
    if 'reddit' in input_message:
    
        reddit_client = RedditClient(
            config=config,
            logger=logger,
            url=input_message
        )
        
        reddit_client.download_image('testing')  # TODO: split download and save?

    if 'twitter' in input_message:
        twitter_client = TwitterClient(
            config=config,
            logger=logger,
            url=input_message
        )
        
        twitter_client.download_image()

    # Load and send images
    images = [
        name for name in os.listdir(image_folder) 
                       if name != 'placeholder'
        ]

    # Make sure that there's any file
    if images:
        for image in images:
            
            image_path = os.path.join(image_folder, image)
            photo = open(image_path, 'rb')
            
            update.message.bot.send_photo(
                chat_id=chat_id,
                reply_to_message_id=message_id,
                photo=photo
                )
                
            os.remove(image_path)
            logger.info('Image removed')
    else:
        logger.info('Image not found')
    


def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_pictures))


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()