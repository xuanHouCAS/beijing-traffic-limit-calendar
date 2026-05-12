from datetime import date

CALENDAR_NAME = "北京尾号4/9限行"
TIMEZONE = "Asia/Shanghai"

LIMIT_START_HOUR = 7
LIMIT_START_MINUTE = 0
LIMIT_END_HOUR = 20
LIMIT_END_MINUTE = 0

TARGET_TAIL_NUMBERS = "4/9"

EVENT_SUMMARY = "北京尾号4/9限行"
EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号4和9，"
    "限行时间7:00-20:00，范围为五环路以内道路，不含五环路。"
)

# 提醒配置
# 事件开始时间是当天 07:00
# 前一天 20:00 = 事件开始前 11 小时
REMINDERS = [
    {
        "trigger": "-PT11H",
        "description": "明天北京尾号4/9限行，注意提前安排出行。",
    },
    {
        "trigger": "-PT0M",
        "description": "今天北京尾号4/9限行，当前已进入限行时段。",
    },
]

# weekday: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4
WEEKDAY_NAMES = {
    0: "周一",
    1: "周二",
    2: "周三",
    3: "周四",
    4: "周五",
}

# 每个周期配置完整的官方尾号限行规则
# 后续每年只需要改这里
#
# tail_numbers_by_weekday:
#   key 是 weekday，Monday=0 ... Friday=4
#   value 是当天限行尾号
#
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

# 可选：官方节假日、临时不限行日期
EXCLUDE_DATES = {
    # date(2026, 5, 1),
    # date(2026, 10, 1),
}

OUTPUT_ICS_PATH = "docs/beijing_49_limit.ics"