from dataclasses import dataclass


@dataclass()
class Setting:
    host: str
    email: str
    password: str

    is_date_work_active: bool
    datetimeValueStart: str
    datetimeValueFinish: str

    manager_intervented_active: bool
    voice_detection: bool

    api_token: str
    pipeline_id: int
    statuses_ids: list


@dataclass()
class Message:
    id: int
    chat_id: int
    answer: str
    pipeline_id: int
    lead_id: int
    status_id: int
    messages_history: list


@dataclass()
class Session:
    amojo_id: str
    chat_token: str
    headers: dict
