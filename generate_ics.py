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
    WEEKDAY_NAMES,
    ENABLE_VALARM,
    ENABLE_STANDALONE_REMINDER_EVENTS,
    REMINDER_EVENT_DURATION_MINUTES,
    REMINDERS,
    PREVIOUS_DAY_REMINDER_SUMMARY,
    PREVIOUS_DAY_REMINDER_DESCRIPTION,
    SAME_DAY_REMINDER_SUMMARY,
    SAME_DAY_REMINDER_DESCRIPTION,
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


def generate_valarms() -> str:
    """
    为主限行事件生成 VALARM。

    注意：
    - 前一天 20:00：TRIGGER:-PT11H
    - 当天 07:00：TRIGGER:PT0S
    """
    if not ENABLE_VALARM:
        return ""

    alarms = []

    for reminder in REMINDERS:
        alarms.append(
            f"""BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:{escape_ics_text(reminder["description"])}
TRIGGER:{reminder["trigger"]}
END:VALARM"""
        )

    return "\n".join(alarms)


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
SEQUENCE:1
STATUS:CONFIRMED
TRANSP:{transparency}
DTSTART;TZID={TIMEZONE}:{format_ics_datetime(start_dt)}
DTEND;TZID={TIMEZONE}:{format_ics_datetime(end_dt)}
SUMMARY:{escape_ics_text(summary)}
DESCRIPTION:{escape_ics_text(description)}{alarm_part}
END:VEVENT"""


def generate_main_limit_event(current_date, period_name: str, weekday: int, dtstamp: str) -> str:
    """
    生成主限行事件：当天 07:00 - 20:00。
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

    weekday_name = WEEKDAY_NAMES.get(weekday, "")

    description = (
        f"{EVENT_DESCRIPTION}"
        f"\n限行周期：{period_name}"
        f"\n本周期尾号{TARGET_TAIL_NUMBERS}限行日：{weekday_name}"
    )

    uid_seed = f"main-limit-{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=EVENT_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        alarms_text=generate_valarms(),
        transparent=False,
    )


def generate_previous_day_reminder_event(current_date, dtstamp: str) -> str:
    """
    生成前一天 20:00 的独立提醒事件。

    例如 current_date 是 2026-04-01 限行日，
    则提醒事件是 2026-03-31 20:00 - 20:05。
    """
    reminder_date = current_date - timedelta(days=1)

    start_dt = datetime.combine(
        reminder_date,
        time(20, 0),
        tzinfo=TZ,
    )

    end_dt = start_dt + timedelta(minutes=REMINDER_EVENT_DURATION_MINUTES)

    uid_seed = f"previous-day-reminder-{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"

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
        alarms_text="",
        transparent=True,
    )


def generate_same_day_reminder_event(current_date, dtstamp: str) -> str:
    """
    生成当天 07:00 的独立提醒事件。

    时间为 07:00 - 07:05。
    """
    start_dt = datetime.combine(
        current_date,
        time(LIMIT_START_HOUR, LIMIT_START_MINUTE),
        tzinfo=TZ,
    )

    end_dt = start_dt + timedelta(minutes=REMINDER_EVENT_DURATION_MINUTES)

    uid_seed = f"same-day-reminder-{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"

    description = (
        f"{SAME_DAY_REMINDER_DESCRIPTION}"
        f"\n对应限行日期：{current_date.isoformat()}"
        f"\n尾号：{TARGET_TAIL_NUMBERS}"
    )

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=SAME_DAY_REMINDER_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        alarms_text="",
        transparent=True,
    )


def generate_events() -> list[str]:
    """
    根据 LIMIT_PERIODS 生成所有事件。

    每个限行日生成：
    1. 主限行事件：07:00 - 20:00
    2. 可选：前一天 20:00 独立提醒事件
    3. 可选：当天 07:00 独立提醒事件
    """
    validate_periods()

    events = []
    dtstamp = format_utc_datetime(datetime.now(tz=TZ))

    for period in LIMIT_PERIODS:
        target_weekday = get_target_weekday(period)

        current = period["start"]
        while current <= period["end"]:
            if current.weekday() == target_weekday and current not in EXCLUDE_DATES:
                # 主限行事件
                events.append(
                    generate_main_limit_event(
                        current_date=current,
                        period_name=period["name"],
                        weekday=target_weekday,
                        dtstamp=dtstamp,
                    )
                )

                # 独立提醒事件，兼容 iOS 不读取 VALARM 的情况
                if ENABLE_STANDALONE_REMINDER_EVENTS:
                    events.append(
                        generate_previous_day_reminder_event(
                            current_date=current,
                            dtstamp=dtstamp,
                        )
                    )
                    events.append(
                        generate_same_day_reminder_event(
                            current_date=current,
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
    print(f"Standalone reminder events: {reminder_event_count}")

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

    print("\nVALARM:")
    print(f"  {'enabled' if ENABLE_VALARM else 'disabled'}")

    print("\nStandalone reminder events:")
    print(f"  {'enabled' if ENABLE_STANDALONE_REMINDER_EVENTS else 'disabled'}")

    if ENABLE_STANDALONE_REMINDER_EVENTS:
        print("  前一天 20:00 - 20:05")
        print("  当天 07:00 - 07:05")


if __name__ == "__main__":
    main()