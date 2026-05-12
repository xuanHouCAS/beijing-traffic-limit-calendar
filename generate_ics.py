from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import uuid

from config import (
    CALENDAR_NAME,
    TIMEZONE,
    EVENT_UID_VERSION,
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
    WEEKDAY_NAMES,
    ENABLE_PREVIOUS_DAY_REMINDER_EVENT,
    REMINDER_EVENT_DURATION_MINUTES,
    PREVIOUS_DAY_REMINDER_HOUR,
    PREVIOUS_DAY_REMINDER_MINUTE,
    PREVIOUS_DAY_REMINDER_SUMMARY,
    PREVIOUS_DAY_REMINDER_DESCRIPTION,
    MAIN_EVENT_REMINDER_HOUR,
    MAIN_EVENT_REMINDER_MINUTE,
    MAIN_EVENT_REMINDER_DESCRIPTION,
)

TZ = ZoneInfo(TIMEZONE)
UTC = ZoneInfo("UTC")


def escape_ics_text(text: str) -> str:
    """
    ICS 文本字段需要转义反斜杠、逗号、分号、换行。
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
    生成 UTC 时间格式，例如：20260512T030000Z
    """
    return dt.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def normalize_tail_numbers(value: str) -> str:
    """
    统一尾号格式，避免 '4/9'、'4 和 9'、'4,9'、'4，9' 等格式差异。
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


def validate_periods() -> None:
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


def generate_absolute_valarm(trigger_dt: datetime, description: str) -> str:
    """
    生成绝对时间提醒。

    使用 TRIGGER;VALUE=DATE-TIME，可以避免 Apple Calendar
    对 PT0S / PT1H 等相对提醒解析不稳定的问题。
    """
    alarm_uid = uuid.uuid5(
        uuid.NAMESPACE_DNS,
        f"alarm-{EVENT_UID_VERSION}-{description}-{format_utc_datetime(trigger_dt)}",
    )

    return f"""BEGIN:VALARM
UID:{alarm_uid}
X-WR-ALARMUID:{alarm_uid}
ACTION:DISPLAY
DESCRIPTION:{escape_ics_text(description)}
TRIGGER;VALUE=DATE-TIME:{format_utc_datetime(trigger_dt)}
END:VALARM"""


def build_event(
    uid_seed: str,
    start_dt: datetime,
    end_dt: datetime,
    summary: str,
    description: str,
    dtstamp: str,
    alarms_text: str = "",
    transparent: bool = False,
) -> str:
    """
    构建标准 VEVENT。
    """
    uid = f"{uuid.uuid5(uuid.NAMESPACE_DNS, uid_seed)}@beijing-traffic-limit-calendar"
    transparency = "TRANSPARENT" if transparent else "OPAQUE"
    alarm_part = f"\n{alarms_text}" if alarms_text else ""

    return f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
LAST-MODIFIED:{dtstamp}
SEQUENCE:3
STATUS:CONFIRMED
TRANSP:{transparency}
DTSTART;TZID={TIMEZONE}:{format_ics_datetime(start_dt)}
DTEND;TZID={TIMEZONE}:{format_ics_datetime(end_dt)}
SUMMARY:{escape_ics_text(summary)}
DESCRIPTION:{escape_ics_text(description)}{alarm_part}
END:VEVENT"""


def generate_main_limit_event(
    current_date,
    period_name: str,
    weekday: int,
    dtstamp: str,
) -> str:
    """
    生成主限行事件：当天 07:00 - 20:00。

    提醒时间：当天 08:00。
    注意：提醒使用绝对时间 TRIGGER;VALUE=DATE-TIME。
    """
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

    reminder_dt = datetime.combine(
        current_date,
        time(MAIN_EVENT_REMINDER_HOUR, MAIN_EVENT_REMINDER_MINUTE),
        tzinfo=TZ,
    )

    weekday_name = WEEKDAY_NAMES.get(weekday, "")

    description = (
        f"{EVENT_DESCRIPTION}"
        f"\n限行周期：{period_name}"
        f"\n本周期尾号{TARGET_TAIL_NUMBERS}限行日：{weekday_name}"
    )

    uid_seed = (
        f"{EVENT_UID_VERSION}-main-limit-"
        f"{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"
    )

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=EVENT_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        alarms_text=generate_absolute_valarm(
            trigger_dt=reminder_dt,
            description=MAIN_EVENT_REMINDER_DESCRIPTION,
        ),
        transparent=False,
    )


def generate_previous_day_reminder_event(current_date, dtstamp: str) -> str:
    """
    生成前一天 20:00 的独立提醒事件。

    事件时间：前一天 20:00 - 20:05
    提醒时间：前一天 20:00
    """
    reminder_date = current_date - timedelta(days=1)

    start_dt = datetime.combine(
        reminder_date,
        time(PREVIOUS_DAY_REMINDER_HOUR, PREVIOUS_DAY_REMINDER_MINUTE),
        tzinfo=TZ,
    )

    end_dt = start_dt + timedelta(minutes=REMINDER_EVENT_DURATION_MINUTES)

    uid_seed = (
        f"{EVENT_UID_VERSION}-previous-day-reminder-"
        f"{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"
    )

    description = (
        f"{PREVIOUS_DAY_REMINDER_DESCRIPTION}"
        f"\n对应限行日期：{current_date.isoformat()}"
        f"\n尾号：{TARGET_TAIL_NUMBERS}"
    )

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=PREVIOUS_DAY_REMINDER_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        alarms_text=generate_absolute_valarm(
            trigger_dt=start_dt,
            description=PREVIOUS_DAY_REMINDER_SUMMARY,
        ),
        transparent=True,
    )


def generate_events() -> list[str]:
    """
    根据 LIMIT_PERIODS 生成所有事件。

    每个限行日生成：
    1. 前一天 20:00 - 20:05 提醒事件：
       明天北京尾号4/9限行，20:00 准时提醒。
    2. 当天 07:00 - 20:00 主限行事件：
       北京尾号4/9限行，08:00 准时提醒。
    """
    validate_periods()

    events = []
    dtstamp = format_utc_datetime(datetime.now(tz=TZ))

    for period in LIMIT_PERIODS:
        target_weekday = get_target_weekday(period)

        current = period["start"]
        while current <= period["end"]:
            if current.weekday() == target_weekday and current not in EXCLUDE_DATES:
                if ENABLE_PREVIOUS_DAY_REMINDER_EVENT:
                    events.append(
                        generate_previous_day_reminder_event(
                            current_date=current,
                            dtstamp=dtstamp,
                        )
                    )

                events.append(
                    generate_main_limit_event(
                        current_date=current,
                        period_name=period["name"],
                        weekday=target_weekday,
                        dtstamp=dtstamp,
                    )
                )

            current += timedelta(days=1)

    return events


def generate_ics() -> str:
    events = generate_events()
    events_text = "\n".join(events)

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Beijing Traffic Restriction Calendar//Tail {TARGET_TAIL_NUMBERS}//CN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{escape_ics_text(CALENDAR_NAME)}
X-WR-TIMEZONE:{TIMEZONE}
REFRESH-INTERVAL;VALUE=DURATION:P1D
X-PUBLISHED-TTL:P1D
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


def main() -> None:
    output_path = Path(OUTPUT_ICS_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    events = generate_events()
    ics_content = generate_ics()

    # ICS 推荐 CRLF 换行
    ics_content = ics_content.replace("\n", "\r\n")

    output_path.write_text(ics_content, encoding="utf-8")

    main_event_count = 0
    reminder_event_count = 0

    for event in events:
        if f"SUMMARY:{escape_ics_text(EVENT_SUMMARY)}" in event:
            main_event_count += 1
        else:
            reminder_event_count += 1

    print(f"Generated: {output_path}")
    print(f"Total events: {len(events)}")
    print(f"Main limit events: {main_event_count}")
    print(f"Previous-day reminder events: {reminder_event_count}")

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

    print("\nReminder strategy:")
    print("  前一天 20:00 - 20:05：明天北京尾号4/9限行，20:00 准时提醒")
    print("  当天 07:00 - 20:00：北京尾号4/9限行，08:00 准时提醒")
    print("  当天 08:00 - 08:05：不再生成独立提醒事件")

    print("\nUID version:")
    print(f"  {EVENT_UID_VERSION}")


if __name__ == "__main__":
    main()