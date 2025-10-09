import datetime
import enum
import re

import parsedatetime
import pytz


DUBLIN_TZ = pytz.timezone("Europe/Dublin")


class TimePeriod(enum.Enum):
    NONE = 0
    DATE = 1
    TIME = 2
    DATETIME = 3


PARSER = parsedatetime.Calendar(parsedatetime.Constants("en_GB"))
WHITESPACE_REGEX = re.compile(r"^\s+|\s+$|\s+(?=\s)")


def strip_whitespace(text: str) -> str:
    return re.sub(WHITESPACE_REGEX, "", text.replace("\xa0", " "))


def str_to_datetime(
    text: str,
    base_time: datetime.datetime | None = None,
) -> datetime.datetime:
    time, result = PARSER.parseDT(text, base_time)

    if isinstance(result, parsedatetime.pdtContext):
        result = result.dateTimeFlag

    time_period = TimePeriod(result)

    if time_period is TimePeriod.NONE:
        raise ValueError(f"failed to parse datetime '{text}'")
    
    assert isinstance(time, datetime.datetime)
    time = DUBLIN_TZ.localize(time)
    time = time.astimezone(pytz.utc)

    return time
