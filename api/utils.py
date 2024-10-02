import datetime
import enum

import parsedatetime


class TimePeriod(enum.Enum):
    NONE = 0
    DATE = 1
    TIME = 2
    DATETIME = 3


PARSER = parsedatetime.Calendar(parsedatetime.Constants("en_GB"))


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

    return time
