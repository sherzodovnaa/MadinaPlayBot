import asyncio
import logging
import random
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher(storage=MemoryStorage())
class GameState(StatesGroup):
    gues_number = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}! \n"
                         f"o'ynash uchun  /play  kommandasini bosing.")


def play():
    builder = ReplyKeyboardBuilder()
    kbs = ['Ha', "Yo'q"]
    builder.add(*[KeyboardButton(text=kb) for kb in kbs])
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("play"))
async def command_play_handler(message: Message):
    await message.answer(f"O'ynashni xohlaysizmi?", reply_markup=play())


@dp.message(F.text == "Yo'q")
async def yoq(message: Message):
    await message.answer(f"O'ynash uchun  /play  kommandasini bosing.")


@dp.message(F.text == 'Ha')
async def ha(message: Message, state: FSMContext):
    gues_number = random.randint(1, 100)
    await state.update_data(gues_number=gues_number, attempt=0)
    await message.answer(f"Men 1 dan 100 gacha son o'yladim! \n"
                         f"Uni topishga harakat qiling.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(GameState.gues_number)


@dp.message(GameState.gues_number)
async def gues_num(message: Message, state: FSMContext):
    data = await state.get_data()
    gues_number = data.get("gues_number")
    attempt = data.get("attempt")
    son = message.text

    if not son.isdigit():
        return await message.answer('Faqat son kiriting.')
    son = int(son)
    if gues_number < son:
        attempt += 1
        await message.answer(f"Men o'ylagan son {son} dan kichik.")
    elif gues_number > son:
        attempt +=1 # +1
        await message.answer(f"Men o'ylagan son {son} dan katta.")
    else:
        attempt += 1
        await message.answer(f" Tabriklayman siz {attempt} ta urinishda topdingiz!🎉")
    await state.update_data(attempt=attempt)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
