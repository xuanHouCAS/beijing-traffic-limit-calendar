from datetime import date

# =========================
# 基础日历配置
# =========================

CALENDAR_NAME = "北京尾号限行"
TIMEZONE = "Asia/Shanghai"

# 用于强制 Apple Calendar 识别事件更新。
# 如果修改提醒策略后 Apple 仍显示旧提醒，可以把这里从 v1 改成 v2 / v3。
EVENT_UID_VERSION = "v3"

# 限行时间：07:00 - 20:00
LIMIT_START_HOUR = 7
LIMIT_START_MINUTE = 0
LIMIT_END_HOUR = 20
LIMIT_END_MINUTE = 0

# 目标尾号
TARGET_TAIL_NUMBERS = "4/9"

# 主限行事件文案
EVENT_SUMMARY = "北京尾号4/9限行"
EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号4和9，"
    "限行时间7:00-20:00，范围为五环路以内道路，不含五环路。"
)

# 输出路径
OUTPUT_ICS_PATH = "docs/beijing_49_limit.ics"


# =========================
# 提醒配置
# =========================

# 是否生成前一天提醒事件
ENABLE_PREVIOUS_DAY_REMINDER_EVENT = True

# 前一天提醒事件持续时间，单位：分钟
REMINDER_EVENT_DURATION_MINUTES = 5

# 前一天 20:00 提醒事件
PREVIOUS_DAY_REMINDER_HOUR = 20
PREVIOUS_DAY_REMINDER_MINUTE = 0
PREVIOUS_DAY_REMINDER_SUMMARY = "明天北京尾号4/9限行"
PREVIOUS_DAY_REMINDER_DESCRIPTION = (
    "明天北京尾号4/9限行，请提前安排出行。"
)

# 主限行事件提醒时间：当天 08:00
# 主事件本身是 07:00 - 20:00，但提醒时间单独配置为 08:00。
MAIN_EVENT_REMINDER_HOUR = 8
MAIN_EVENT_REMINDER_MINUTE = 0
MAIN_EVENT_REMINDER_DESCRIPTION = (
    "今天北京尾号4/9限行，当前已进入限行时段。"
)


# =========================
# 星期说明
# =========================

# weekday: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4
WEEKDAY_NAMES = {
    0: "周一",
    1: "周二",
    2: "周三",
    3: "周四",
    4: "周五",
}


# =========================
# 限行周期配置
# =========================

# 每个周期配置完整的官方尾号限行规则
# 程序会自动找到 TARGET_TAIL_NUMBERS = "4/9" 对应的 weekday
LIMIT_PERIODS = [
    {
        "name": "2026年第1轮限行周期",
        "start": date(2026, 3, 30),
        "end": date(2026, 6, 28),
        "tail_numbers_by_weekday": {
            0: "3/8",
            1: "2/7",
            2: "4/9",
            3: "5/0",
            4: "1/6",
        },
    },
    {
        "name": "2026年第2轮限行周期",
        "start": date(2026, 6, 29),
        "end": date(2026, 9, 27),
        "tail_numbers_by_weekday": {
            0: "1/6",
            1: "3/8",
            2: "2/7",
            3: "4/9",
            4: "5/0",
        },
    },
    {
        "name": "2026年第3轮限行周期",
        "start": date(2026, 9, 28),
        "end": date(2026, 12, 27),
        "tail_numbers_by_weekday": {
            0: "5/0",
            1: "1/6",
            2: "3/8",
            3: "2/7",
            4: "4/9",
        },
    },
    {
        "name": "2026年第4轮限行周期",
        "start": date(2026, 12, 28),
        "end": date(2027, 3, 28),
        "tail_numbers_by_weekday": {
            0: "4/9",
            1: "5/0",
            2: "1/6",
            3: "3/8",
            4: "2/7",
        },
    },
]


# =========================
# 特殊不限行日期
# =========================

# 如果某些日期虽然落在限行星期，但因为节假日或官方临时通知不限行，
# 可以加入这里。
EXCLUDE_DATES = {
    # date(2026, 5, 1),
    # date(2026, 10, 1),
}