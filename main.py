import os
import asyncio
import logging
import json
from PIL import Image
import io
from ultralytics import YOLO
from aiogram import Bot, Dispatcher, types, F, types
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.filters.command import Command
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

token = os.getenv("token")
bot = Bot(token=token)
dp = Dispatcher()

model = YOLO("D:/bots/deepmlbot/model2/weights/best.pt")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Отправь изображения и я обведу на нем все лица!")

@dp.message(F.photo)
async def image_catch(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    downloaded_image = await bot.download_file(file.file_path)
    image = Image.open(downloaded_image)
    res = model(image, conf=0.5)

    if len(res[0].boxes) == 0:
            await message.answer_animation(caption="Лицо не обнаружено", animation="CgACAgQAAxkBAAMhaSLTG_EvpMUvZkHaVTxHELXSgd0AAnUDAAKUDa1SrrpEZ6p4wzo2BA")
            return

    for r in res:
            im_array = r.plot()
            im = Image.fromarray(im_array[..., ::-1])
            bio = io.BytesIO()
            im.save(bio, format='PNG')
            bio.seek(0)
            result_photo = BufferedInputFile(bio.read(), filename="result.png")
            if len(res[0].boxes) > 1:
                await message.answer_photo(caption="ВИЖУ ИХ!", photo=result_photo)
                return
            await message.answer_photo(caption="ВИЖУ ЕГО!", photo=result_photo)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())