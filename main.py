import asyncio
import os

from aiogram import Bot, Dispatcher  # , Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
import json

from dotenv import load_dotenv

load_dotenv()

bot_token = str(os.getenv('bot_token'))


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message):
    """
    Этот обработчик принимает сообщения с командой `/start`
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message):
    try:
        text = str(json.loads(message.model_dump_json())["chat"]['id'])
        await message.answer(f"Твой id = {text}")
    except TypeError:
        await message.answer("Код упал на обработке сообщения")


async def main():
    bot = Bot(bot_token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
