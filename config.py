from datetime import date

# =========================
# 基础日历配置
# =========================

CALENDAR_NAME = "北京尾号4/9限行"
TIMEZONE = "Asia/Shanghai"

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

# 是否在限行事件中写入 VALARM
# 注意：部分 iOS 订阅日历可能不会完全采用 VALARM，而是使用系统默认提醒。
ENABLE_VALARM = True

# 是否额外生成“提醒事件”
# 推荐开启，兼容性比 VALARM 更好。
# 开启后会额外生成：
# 1. 前一天 20:00 - 20:05：明天限行提醒
# 2. 当天 07:00 - 07:05：今天限行提醒
ENABLE_STANDALONE_REMINDER_EVENTS = True

# 提醒事件持续时间，单位：分钟
REMINDER_EVENT_DURATION_MINUTES = 5

# VALARM 提醒
# 主事件开始时间是当天 07:00
# 前一天 20:00 距离当天 07:00 是 11 小时，所以是 -PT11H
# 当天 07:00 用 PT0S，不建议用 -PT0M
REMINDERS = [
    {
        "trigger": "-PT11H",
        "description": "明天北京尾号4/9限行，注意提前安排出行。",
    },
    {
        "trigger": "PT0S",
        "description": "今天北京尾号4/9限行，当前已进入限行时段。",
    },
]

# 独立提醒事件文案
PREVIOUS_DAY_REMINDER_SUMMARY = "明天北京尾号4/9限行"
PREVIOUS_DAY_REMINDER_DESCRIPTION = (
    "明天北京尾号4/9限行，请提前安排出行。"
)

SAME_DAY_REMINDER_SUMMARY = "今天北京尾号4/9限行"
SAME_DAY_REMINDER_DESCRIPTION = (
    "今天北京尾号4/9限行，限行时间为07:00-20:00。"
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
#
# tail_numbers_by_weekday:
#   key 是 weekday，Monday=0 ... Friday=4
#   value 是当天限行尾号
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