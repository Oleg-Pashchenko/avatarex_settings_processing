import datetime
from contextlib import contextmanager

import psycopg2

from app.models import Setting, Message, Session
import dotenv
import os

dotenv.load_dotenv()


@contextmanager
def get_connection(db_name: str, db_user: str, db_password: str, db_host: str):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    try:
        yield conn
    finally:
        conn.close()


def execute_db_query(
        db, query, parameters, fetch_one=False, fetch_all=False):
    with get_connection(db_host=db['host'], db_name=db['name'], db_password=db['password'], db_user=db['user']) as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        conn.commit()


def get_settings_list() -> list[Setting]:
    query = """SELECT 
        amocrm.host,
        amocrm.email,
        amocrm.password,
        settings.is_date_work_active,
        settings."datetimeValueStart",
        settings."datetimeValueFinish",
        settings.is_manager_intervented_active,
        settings.voice_detection,
        avatarex_users.openai_api_key AS api_token,
        pipelines.pipeline_id,
        settings.statuses
        
    FROM 
        settings
    JOIN 
        amocrm ON settings.user_id_id = amocrm.user_id_id
    JOIN 
        avatarex_users ON amocrm.user_id_id = avatarex_users.id
    JOIN 
        pipelines ON settings.pipeline_id_id = pipelines.id  
        """
    rows = execute_db_query({
        'host': os.getenv('DB_HOST'),
        'password': os.getenv('DB_PASSWORD'),
        'name': os.getenv('DB_SITE_NAME'),
        'user': os.getenv('DB_USER')
    },
        query,
        (), False, True)
    return [Setting(*row) for row in rows]


def message_exists(lead_id: int, message_id: int) -> bool:
    query = "SELECT id FROM messages WHERE lead_id=%s AND message_id=%s"
    response = execute_db_query({
        'host': os.getenv('DB_HOST'),
        'password': os.getenv('DB_PASSWORD'),
        'name': os.getenv('DB_API_NAME'),
        'user': os.getenv('DB_USER')
    },
        query,
        (lead_id, message_id,))
    return response is not None


def manager_intervened(lead_id: int, messages_history: list) -> bool:
    try:
        entity = messages_history[0]
        for id, message in enumerate(messages_history):
            if id == 5:
                break

            if not message_exists(lead_id, message['id']) and entity['author']['id'] != message['author']['id']:
                created_at = message['created_at']
                datetime_from_timestamp = datetime.datetime.fromtimestamp(created_at)
                current_datetime = datetime.datetime.now()
                time_difference = current_datetime - datetime_from_timestamp

                if time_difference.total_seconds() < 60 * 60:
                    return True
        return False
    except:
        return False


def add_message(message: Message):
    query = "INSERT INTO messages (message_id, text, lead_id, is_bot, is_q) VALUES (%s, %s, %s, %s, %s)"
    execute_db_query({
        'host': os.getenv('DB_HOST'),
        'password': os.getenv('DB_PASSWORD'),
        'name': os.getenv('DB_API_NAME'),
        'user': os.getenv('DB_USER')
    },
        query,
        (message.id, message.answer, message.lead_id, False, False))


def get_session(host: str) -> Session:
    query = "SELECT amojo_id, chat_token, headers FROM amocrm_sessions WHERE host=%s"
    row = execute_db_query({
        'host': os.getenv('DB_SESSIONS_HOST'),
        'password': os.getenv('DB_SESSIONS_PASSWORD'),
        'name': os.getenv('DB_SESSIONS_NAME'),
        'user': os.getenv('DB_SESSIONS_USER')
    },
        query, (host,), fetch_one=True)
    if not row:
        return None
    return Session(*row)


