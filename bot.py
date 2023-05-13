import os
import logging
from io import BytesIO
from PIL import Image
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me an image and choose a compression level (100 KB, 50 KB, or 20 KB).")

def compress_image(image, target_size):
    quality = 90
    while image.tell() > target_size:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        image = Image.open(buffer)
        quality -= 10
    return image

def handle_image(update: Update, context: CallbackContext):
    user = update.message.from_user
    photo = update.message.photo[-1]
    target_sizes = {"100": 100 * 1024, "50": 50 * 1024, "20": 20 * 1024}

    if update.message.caption not in target_sizes:
        update.message.reply_text("Please specify a valid compression level: 100 KB, 50 KB, or 20 KB.")
        return

    target_size = target_sizes[update.message.caption]
    image_data = BytesIO(photo.get_file().download_as_bytearray())
    image = Image.open(image_data)

    compressed_image = compress_image(image, target_size)
    output = BytesIO()
    compressed_image.save(output, format="JPEG")
    output.seek(0)

    update.message.reply_photo(photo=InputFile(output, "compressed_image.jpg"), caption="Compressed image")

def main():
    logging.basicConfig(level=logging.INFO)

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
