import pytz
from datetime import datetime

from app import database


def is_time_between(start_time_str, end_time_str):
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz).time()
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:
        return start_time <= now or now <= end_time


message_exists = lambda message: database.message_exists(message.lead_id, message.id)
manager_intervented = lambda setting, message: setting.manager_intervented_active and database.manager_intervened(
    message.lead_id,
    message.mesages_history)

voice_and_detection_inactive = lambda setting, message: setting.voice_detection is False and ".m4a" in message.answer
is_in_working_time = lambda setting: (not setting.is_date_work_active) or (
        setting.is_date_work_active and is_time_between(setting.datetimeValueStart, setting.datetimeValueFinish))
