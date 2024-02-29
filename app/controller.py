import asyncio
import time

from app.connectors import amocrm
from app.database import get_settings_list
from app.models import Setting, Message, Session
from app.utils import *


async def message_processing(setting: Setting, message: Message):
    try:
        if message_exists(message) or manager_intervented(setting, message) or \
                voice_and_detection_inactive(setting, message):
            return

        database.add_message(message, setting)

    except Exception as e:
        print('message e', e)


async def setting_processing(setting: Setting):
    if not is_in_working_time(setting):
        return
    session: Session = database.get_session(setting.host)
    if not session:
        return
    messages: list[Message] = await amocrm.read_messages(setting, session)
    [await message_processing(setting, message) for message in messages]


async def run():
    while True:
        start_time = time.time()
        settings: list[Setting] = get_settings_list()
        for setting in settings:
            asyncio.create_task(setting_processing(setting))
        print(round(time.time() - start_time, 2))
        await asyncio.sleep(5)
