from datetime import date

# 日历基础信息
CALENDAR_NAME = "北京尾号4/9限行"
TIMEZONE = "Asia/Shanghai"

# 限行时间：07:00 - 20:00
LIMIT_START_HOUR = 7
LIMIT_START_MINUTE = 0
LIMIT_END_HOUR = 20
LIMIT_END_MINUTE = 0

# 只生成尾号 4/9 的限行事件
TARGET_TAIL_NUMBERS = "4/9"

# 事件描述
EVENT_SUMMARY = "北京尾号4/9限行"
EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号4和9，"
    "限行时间7:00-20:00，范围为五环路以内道路，不含五环路。"
)

# 2026-03-30 至 2027-03-28 当前轮换规则
# weekday: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4
RULES = [
    {
        "start": date(2026, 3, 30),
        "end": date(2026, 6, 28),
        "weekday": 2,  # 周三：4/9
    },
    {
        "start": date(2026, 6, 29),
        "end": date(2026, 9, 27),
        "weekday": 3,  # 周四：4/9
    },
    {
        "start": date(2026, 9, 28),
        "end": date(2026, 12, 27),
        "weekday": 4,  # 周五：4/9
    },
    {
        "start": date(2026, 12, 28),
        "end": date(2027, 3, 28),
        "weekday": 0,  # 周一：4/9
    },
]

# 可选：法定节假日、临时不限行日期
# 后续如果官方发布“某日不限行”，就在这里加。
EXCLUDE_DATES = {
    # date(2026, 5, 1),
    # date(2026, 10, 1),
}

# 输出路径，建议放 docs/ 目录，方便 GitHub Pages 发布
OUTPUT_ICS_PATH = "docs/beijing_49_limit.ics"