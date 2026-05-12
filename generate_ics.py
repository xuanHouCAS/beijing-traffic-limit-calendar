from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import uuid

from config import (
    CALENDAR_NAME,
    TIMEZONE,
    TARGET_TAIL_NUMBERS,
    ACTUAL_LIMIT_START_HOUR,
    ACTUAL_LIMIT_START_MINUTE,
    ACTUAL_LIMIT_END_HOUR,
    ACTUAL_LIMIT_END_MINUTE,
    SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES,
    PREVIOUS_DAY_REMINDER_TARGET_HOUR,
    PREVIOUS_DAY_REMINDER_TARGET_MINUTE,
    PREVIOUS_DAY_REMINDER_EVENT_HOUR,
    PREVIOUS_DAY_REMINDER_EVENT_MINUTE,
    PREVIOUS_DAY_REMINDER_EVENT_DURATION_MINUTES,
    PREVIOUS_DAY_REMINDER_SUMMARY,
    PREVIOUS_DAY_REMINDER_DESCRIPTION,
    MAIN_EVENT_START_HOUR,
    MAIN_EVENT_START_MINUTE,
    MAIN_EVENT_END_HOUR,
    MAIN_EVENT_END_MINUTE,
    EVENT_SUMMARY,
    EVENT_DESCRIPTION,
    LIMIT_PERIODS,
    EXCLUDE_DATES,
    OUTPUT_ICS_PATH,
    WEEKDAY_NAMES,
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
    生成 ICS 本地时间格式，例如：20260401T090000
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


def build_uid(uid_seed: str) -> str:
    return f"{uuid.uuid5(uuid.NAMESPACE_DNS, uid_seed)}@beijing-traffic-limit-calendar"


def build_event(
    uid_seed: str,
    start_dt: datetime,
    end_dt: datetime,
    summary: str,
    description: str,
    dtstamp: str,
    transparent: bool = False,
) -> str:
    """
    构建标准 VEVENT。

    注意：
    当前方案不写 VALARM。
    提醒完全依赖客户端系统默认提醒，例如 Apple 日历默认“开始前 1 小时提醒”。
    """
    uid = build_uid(uid_seed)
    transparency = "TRANSPARENT" if transparent else "OPAQUE"

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
DESCRIPTION:{escape_ics_text(description)}
END:VEVENT"""


def generate_previous_day_reminder_event(current_date, dtstamp: str) -> str:
    """
    生成前一天提醒事件。

    目标提醒时间：前一天 20:00
    系统默认提醒：开始前 1 小时
    因此事件时间：前一天 21:00 - 21:05
    """
    reminder_date = current_date - timedelta(days=1)

    start_dt = datetime.combine(
        reminder_date,
        time(PREVIOUS_DAY_REMINDER_EVENT_HOUR, PREVIOUS_DAY_REMINDER_EVENT_MINUTE),
        tzinfo=TZ,
    )

    end_dt = start_dt + timedelta(minutes=PREVIOUS_DAY_REMINDER_EVENT_DURATION_MINUTES)

    target_reminder_dt = datetime.combine(
        reminder_date,
        time(PREVIOUS_DAY_REMINDER_TARGET_HOUR, PREVIOUS_DAY_REMINDER_TARGET_MINUTE),
        tzinfo=TZ,
    )

    description = (
        f"{PREVIOUS_DAY_REMINDER_DESCRIPTION}\n"
        f"目标提醒时间：{target_reminder_dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"事件时间设置为：{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}\n"
        f"原因：利用系统默认提前{SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES}分钟提醒。\n"
        f"对应限行日期：{current_date.isoformat()}\n"
        f"尾号：{TARGET_TAIL_NUMBERS}"
    )

    uid_seed = (
        f"previous-day-reminder-default-alert-"
        f"{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"
    )

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=PREVIOUS_DAY_REMINDER_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        transparent=True,
    )


def generate_main_limit_event(
    current_date,
    period_name: str,
    weekday: int,
    dtstamp: str,
) -> str:
    """
    生成当天主限行事件。

    实际限行时间：07:00 - 20:00
    目标提醒时间：08:00
    系统默认提醒：开始前 1 小时
    因此事件时间：09:00 - 20:00

    注意：
    事件标题和描述中明确写出实际限行时间为 07:00 - 20:00。
    """
    start_dt = datetime.combine(
        current_date,
        time(MAIN_EVENT_START_HOUR, MAIN_EVENT_START_MINUTE),
        tzinfo=TZ,
    )

    end_dt = datetime.combine(
        current_date,
        time(MAIN_EVENT_END_HOUR, MAIN_EVENT_END_MINUTE),
        tzinfo=TZ,
    )

    actual_start_dt = datetime.combine(
        current_date,
        time(ACTUAL_LIMIT_START_HOUR, ACTUAL_LIMIT_START_MINUTE),
        tzinfo=TZ,
    )

    actual_end_dt = datetime.combine(
        current_date,
        time(ACTUAL_LIMIT_END_HOUR, ACTUAL_LIMIT_END_MINUTE),
        tzinfo=TZ,
    )

    target_reminder_dt = start_dt - timedelta(
        minutes=SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES
    )

    weekday_name = WEEKDAY_NAMES.get(weekday, "")

    description = (
        f"{EVENT_DESCRIPTION}\n"
        f"实际限行时间：{actual_start_dt.strftime('%H:%M')} - {actual_end_dt.strftime('%H:%M')}\n"
        f"日历事件时间：{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}\n"
        f"目标提醒时间：{target_reminder_dt.strftime('%H:%M')}\n"
        f"原因：利用系统默认提前{SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES}分钟提醒。\n"
        f"限行周期：{period_name}\n"
        f"本周期尾号{TARGET_TAIL_NUMBERS}限行日：{weekday_name}"
    )

    uid_seed = (
        f"main-limit-default-alert-"
        f"{TARGET_TAIL_NUMBERS}-{current_date.isoformat()}"
    )

    return build_event(
        uid_seed=uid_seed,
        start_dt=start_dt,
        end_dt=end_dt,
        summary=EVENT_SUMMARY,
        description=description,
        dtstamp=dtstamp,
        transparent=False,
    )


def generate_events() -> list[str]:
    """
    根据 LIMIT_PERIODS 生成所有事件。

    每个限行日生成：
    1. 前一天 21:00 - 21:05 短提醒事件
       利用系统默认提前 1 小时提醒，实现前一天 20:00 弹提醒。

    2. 当天 09:00 - 20:00 主限行事件
       实际限行时间写在 summary / description 中。
       利用系统默认提前 1 小时提醒，实现当天 08:00 弹提醒。
    """
    validate_periods()

    events = []
    dtstamp = format_utc_datetime(datetime.now(tz=TZ))

    for period in LIMIT_PERIODS:
        target_weekday = get_target_weekday(period)

        current = period["start"]
        while current <= period["end"]:
            if current.weekday() == target_weekday and current not in EXCLUDE_DATES:
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
    print(
        "  不写 VALARM，利用系统默认"
        f"提前 {SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES} 分钟提醒"
    )
    print("  前一天 21:00 - 21:05 事件 → 实际 20:00 提醒")
    print("  当天 09:00 - 20:00 事件 → 实际 08:00 提醒")
    print("  实际限行时间 07:00 - 20:00 写在标题和描述中")


if __name__ == "__main__":
    main()