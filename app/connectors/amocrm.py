from app.connectors import connector
from app.models import Message

host = 'http://amocrm.avatarex.tech'


async def read_messages(setting, session):
    url = f'{host}/get-messages/'
    data = {
        'amo_host': setting.host,
        'amojo_hash': session.amojo_id,
        'chat_token': session.chat_token,
        'pipeline_id': setting.pipeline_id,
        'stage_ids': setting.statuses_ids,
        'headers': session.headers
    }
    answer = await connector.send_request(data, url)
    if answer == '-':
        return []

    resp = [Message(**m) for m in answer]
    return resp



