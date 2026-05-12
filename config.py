from datetime import date

# =========================
# 基础日历配置
# =========================

CALENDAR_NAME = "北京尾号限行"
TIMEZONE = "Asia/Shanghai"

# 目标尾号
TARGET_TAIL_NUMBERS = "4/9"

# 实际限行时间，用于文案说明
ACTUAL_LIMIT_START_HOUR = 7
ACTUAL_LIMIT_START_MINUTE = 0
ACTUAL_LIMIT_END_HOUR = 20
ACTUAL_LIMIT_END_MINUTE = 0

# =========================
# 反向利用系统默认提醒配置
# =========================

# 说明：
# Apple 日历对外部订阅 .ics 的 VALARM 支持不稳定。
# 因此这里不写 VALARM，而是利用系统默认“开始前 1 小时提醒”。
#
# 想 20:00 提醒 → 创建 21:00 事件
# 想 08:00 提醒 → 创建 09:00 事件

# 系统默认提醒提前时间，单位：分钟
# 当前方案假设系统默认提醒为“开始前 1 小时”
SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES = 60

# 前一天提醒：实际希望 20:00 提醒
# 因为系统提前 1 小时提醒，所以事件写成 21:00 - 21:05
PREVIOUS_DAY_REMINDER_TARGET_HOUR = 20
PREVIOUS_DAY_REMINDER_TARGET_MINUTE = 0
PREVIOUS_DAY_REMINDER_EVENT_HOUR = 21
PREVIOUS_DAY_REMINDER_EVENT_MINUTE = 0
PREVIOUS_DAY_REMINDER_EVENT_DURATION_MINUTES = 5

PREVIOUS_DAY_REMINDER_SUMMARY = "明天北京尾号4/9限行"
PREVIOUS_DAY_REMINDER_DESCRIPTION = (
    "明天北京尾号4/9限行，请提前安排出行。"
)

# 当天提醒：实际希望 08:00 提醒
# 因为系统提前 1 小时提醒，所以事件写成 09:00 开始。
# 为了减少日历事件数量，同时表达当天限行范围，主事件设置为 09:00 - 20:00。
MAIN_EVENT_START_HOUR = 9
MAIN_EVENT_START_MINUTE = 0
MAIN_EVENT_END_HOUR = 20
MAIN_EVENT_END_MINUTE = 0

EVENT_SUMMARY = "北京尾号4/9限行（实际07:00-20:00）"
EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号4和9。"
    "实际限行时间为07:00-20:00，范围为五环路以内道路，不含五环路。"
    "本日历事件设置为09:00-20:00，是为了利用系统默认提前1小时提醒，在08:00弹出提醒。"
)

# 输出路径
OUTPUT_ICS_PATH = "docs/beijing_49_limit.ics"


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

# 每个周期配置完整的官方尾号限行规则。
# 程序会自动找到 TARGET_TAIL_NUMBERS = "4/9" 对应的 weekday。
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