# datetime_utils.py
from datetime import datetime
from zoneinfo import ZoneInfo


def get_utc_now() -> datetime:
    return datetime.now(tz=ZoneInfo("UTC"))


def convert_timezone(dt: datetime, to: str) -> datetime:
    return dt.astimezone(ZoneInfo(to))


def get_brt_time_now() -> datetime:
    return convert_timezone(get_utc_now(), 'America/Sao_Paulo').replace(tzinfo=None)


def ensure_brt_timezone(dt: datetime) -> datetime:
    """
    Se `dt` for naive (sem timezone), assume que está em BRT e define o timezone.
    Se já tiver timezone, converte para BRT.
    """
    brt = ZoneInfo("America/Sao_Paulo")
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(brt).replace(tzinfo=None)


def to_naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)
