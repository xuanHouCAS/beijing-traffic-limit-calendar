from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import uuid

from config import (
    CALENDAR_NAME,
    TIMEZONE,
    LIMIT_START_HOUR,
    LIMIT_START_MINUTE,
    LIMIT_END_HOUR,
    LIMIT_END_MINUTE,
    EVENT_SUMMARY,
    EVENT_DESCRIPTION,
    RULES,
    EXCLUDE_DATES,
    OUTPUT_ICS_PATH,
)

TZ = ZoneInfo(TIMEZONE)


def escape_ics_text(text: str) -> str:
    """
    ICS 文本字段需要转义逗号、分号、反斜杠和换行。
    """
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def format_ics_datetime(dt: datetime) -> str:
    """
    生成 ICS 本地时间格式，例如：20260401T070000
    """
    return dt.strftime("%Y%m%dT%H%M%S")


def format_utc_datetime(dt: datetime) -> str:
    """
    生成 UTC 时间格式，用于 DTSTAMP。
    """
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")


def generate_event_for_date(current_date):
    start_dt = datetime.combine(
        current_date,
        time(LIMIT_START_HOUR, LIMIT_START_MINUTE),
        tzinfo=TZ,
    )

    end_dt = datetime.combine(
        current_date,
        time(LIMIT_END_HOUR, LIMIT_END_MINUTE),
        tzinfo=TZ,
    )

    uid_seed = f"beijing-traffic-limit-49-{current_date.isoformat()}"
    uid = f"{uuid.uuid5(uuid.NAMESPACE_DNS, uid_seed)}@beijing-traffic-limit-calendar"

    dtstamp = format_utc_datetime(datetime.now(tz=TZ))

    return f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;TZID={TIMEZONE}:{format_ics_datetime(start_dt)}
DTEND;TZID={TIMEZONE}:{format_ics_datetime(end_dt)}
SUMMARY:{escape_ics_text(EVENT_SUMMARY)}
DESCRIPTION:{escape_ics_text(EVENT_DESCRIPTION)}
END:VEVENT"""


def generate_events():
    events = []

    for rule in RULES:
        current = rule["start"]

        while current <= rule["end"]:
            if current.weekday() == rule["weekday"] and current not in EXCLUDE_DATES:
                events.append(generate_event_for_date(current))

            current += timedelta(days=1)

    return events


def generate_ics():
    events_text = "\n".join(generate_events())

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Beijing Traffic Restriction Calendar//Tail 4 and 9//CN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{escape_ics_text(CALENDAR_NAME)}
X-WR-TIMEZONE:{TIMEZONE}
BEGIN:VTIMEZONE
TZID:{TIMEZONE}
X-LIC-LOCATION:{TIMEZONE}
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
{events_text}
END:VCALENDAR
"""


def main():
    output_path = Path(OUTPUT_ICS_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ics_content = generate_ics()

    # ICS 推荐 CRLF 换行
    ics_content = ics_content.replace("\n", "\r\n")

    output_path.write_text(ics_content, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Events: {len(generate_events())}")


if __name__ == "__main__":
    main()