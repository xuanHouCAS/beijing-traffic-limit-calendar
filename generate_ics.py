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
    TARGET_TAIL_NUMBERS,
    EVENT_SUMMARY,
    EVENT_DESCRIPTION,
    LIMIT_PERIODS,
    EXCLUDE_DATES,
    OUTPUT_ICS_PATH,
    REMINDERS,
    WEEKDAY_NAMES,
)

TZ = ZoneInfo(TIMEZONE)


def escape_ics_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def format_ics_datetime(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def format_utc_datetime(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")


def normalize_tail_numbers(value: str) -> str:
    """
    统一尾号格式，避免 '4/9'、'4 和 9'、'4,9' 这种配置差异。
    当前推荐配置仍然用 '4/9'。
    """
    return (
        value.replace("和", "/")
        .replace(",", "/")
        .replace("，", "/")
        .replace("、", "/")
        .replace(" ", "")
    )


def get_target_weekday(period: dict) -> int:
    """
    从一个限行周期中自动找出 TARGET_TAIL_NUMBERS 对应的 weekday。
    """
    target = normalize_tail_numbers(TARGET_TAIL_NUMBERS)

    for weekday, tail_numbers in period["tail_numbers_by_weekday"].items():
        if normalize_tail_numbers(tail_numbers) == target:
            return weekday

    raise ValueError(
        f"在周期 {period['name']} 中没有找到尾号 {TARGET_TAIL_NUMBERS} 对应的限行日"
    )


def validate_periods():
    """
    检查周期配置是否存在明显问题。
    """
    for period in LIMIT_PERIODS:
        start = period["start"]
        end = period["end"]

        if start > end:
            raise ValueError(f"{period['name']} 的 start 晚于 end")

        weekdays = set(period["tail_numbers_by_weekday"].keys())
        expected_weekdays = {0, 1, 2, 3, 4}

        if weekdays != expected_weekdays:
            raise ValueError(
                f"{period['name']} 的 weekday 配置不完整，应包含 0,1,2,3,4"
            )

        get_target_weekday(period)


def generate_alarms() -> str:
    alarms = []

    for reminder in REMINDERS:
        alarms.append(f"""BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{escape_ics_text(reminder["description"])}
TRIGGER:{reminder["trigger"]}
END:VALARM""")

    return "\n".join(alarms)


def generate_event_for_date(current_date, period_name: str, weekday: int):
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

    uid_seed = f"beijing-traffic-limit-{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"
    uid = f"{uuid.uuid5(uuid.NAMESPACE_DNS, uid_seed)}@beijing-traffic-limit-calendar"

    dtstamp = format_utc_datetime(datetime.now(tz=TZ))
    alarms_text = generate_alarms()

    weekday_name = WEEKDAY_NAMES.get(weekday, "")

    description = (
        f"{EVENT_DESCRIPTION}"
        f"\\n限行周期：{period_name}"
        f"\\n本周期尾号{TARGET_TAIL_NUMBERS}限行日：{weekday_name}"
    )

    return f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;TZID={TIMEZONE}:{format_ics_datetime(start_dt)}
DTEND;TZID={TIMEZONE}:{format_ics_datetime(end_dt)}
SUMMARY:{escape_ics_text(EVENT_SUMMARY)}
DESCRIPTION:{escape_ics_text(description)}
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{escape_ics_text("明天北京尾号4/9限行，注意提前安排出行。")}
TRIGGER:-PT11H
END:VALARM
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{escape_ics_text("今天北京尾号4/9限行，当前已进入限行时段。")}
TRIGGER:-PT0M
END:VALARM
END:VEVENT"""


def generate_events():
    events = []

    for period in LIMIT_PERIODS:
        target_weekday = get_target_weekday(period)

        current = period["start"]
        while current <= period["end"]:
            if current.weekday() == target_weekday and current not in EXCLUDE_DATES:
                events.append(
                    generate_event_for_date(
                        current_date=current,
                        period_name=period["name"],
                        weekday=target_weekday,
                    )
                )

            current += timedelta(days=1)

    return events


def generate_ics():
    validate_periods()

    events = generate_events()
    events_text = "\n".join(events)

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
    ics_content = ics_content.replace("\n", "\r\n")

    output_path.write_text(ics_content, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Events: {len(generate_events())}")

    print("\nTarget tail numbers:")
    print(f"  {TARGET_TAIL_NUMBERS}")

    print("\nLimit periods:")
    for period in LIMIT_PERIODS:
        weekday = get_target_weekday(period)
        print(
            f"  {period['name']}: "
            f"{period['start']} ~ {period['end']}, "
            f"{WEEKDAY_NAMES[weekday]} 限行"
        )

    print("\nReminders:")
    print("  前一天 20:00")
    print("  当天 07:00")


if __name__ == "__main__":
    main()