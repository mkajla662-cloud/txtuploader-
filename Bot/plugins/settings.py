from .. import client
from pyrogram import Client, filters
from pyrogram.types import Message
from ..functions.filters import OWNER_FILTER
from ..functions.helper import URL_REGEX, run_cmd
from ..config import Config


async def reply_to_photo_filter(_, __, m: Message):
    return bool(m.reply_to_message.photo)


async def no_args_filter(_, __, m: Message):
    return True if len(m.command) == 1 else False


@Client.on_message(filters.private & OWNER_FILTER & filters.command('caption'))
async def custom_caption(bot: Client, update: Message):
    try:
        caption = update.text.html.split(' ', 1)[1]
        await update.reply(text='Custom caption updated.')
    except IndexError:
        if not client.custom_caption.get(update.from_user.id):
            return await update.reply(
                text='Ex: `/caption abcdfgh`'
            )
        caption = ""
        await update.reply(text='Custom caption cleared.')
    client.custom_caption[update.from_user.id] = caption


@Client.on_message(filters.private & OWNER_FILTER & filters.command('thumbnail') & ~filters.reply & (filters.regex(pattern=URL_REGEX) | filters.create(no_args_filter)))
async def custom_thumbnail(bot: Client, update: Message):
    try:
        thumbnail = f'{Config.DOWNLOAD_DIR}{update.from_user.id}.jpg'
        command = 'wget -O "{}" "{}"'.format(
            thumbnail, URL_REGEX.findall(update.text)[0])
        await run_cmd(command)
        await update.reply(text='Custom thumbnail updated.')
    except IndexError:
        if not client.custom_thumbnail.get(update.from_user.id):
            return await update.reply(
                text='Reply to a photo or `/thumbnail https.....jpg`'
            )
        thumbnail = None
        await update.reply(text='Custom thumbnail cleared.')
    client.custom_thumbnail[update.from_user.id] = thumbnail


@Client.on_message(filters.private & OWNER_FILTER & filters.command('thumbnail') & filters.reply & filters.create(reply_to_photo_filter))
async def custom_thumbnail_reply(bot: Client, update: Message):
    client.custom_thumbnail[update.from_user.id] = await update.reply_to_message.download(file_name=f'{Config.DOWNLOAD_DIR}{update.from_user.id}.jpg')
    await update.reply(text='Custom thumbnail updated.')