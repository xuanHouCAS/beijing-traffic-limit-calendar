# 北京尾号限行日历

一个根据北京市机动车工作日尾号限行规则，自动生成 `.ics` 日历订阅文件的小工具。

当前版本默认针对 **车牌尾号 4 / 9** 的车辆。其他尾号可以通过修改 `config.py` 后自行生成。

---

## 在线页面

项目提供一个 GitHub Pages 页面，包含订阅链接、ICS 下载入口和不同设备的使用说明：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/
```

当前生成的日历订阅地址：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

iOS 添加路径：

```text
设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历
```

---

## 重要说明：Apple 日历提醒策略

Apple 日历对外部订阅 `.ics` 文件中的 `VALARM` 支持不稳定：  
有时会忽略 `.ics` 中自定义的提醒，而直接套用系统默认提醒。

因此，本项目当前采用更稳定的方案：

```text
不写 VALARM
反向利用系统默认提醒
```

当前配置假设 Apple 日历默认提醒是：

```text
开始前 1 小时提醒
```

因此：

```text
想前一天 20:00 提醒
→ 创建前一天 21:00 - 21:05 的短事件
→ 系统默认提前 1 小时提醒
→ 实际 20:00 弹提醒

想当天 08:00 提醒
→ 创建当天 09:00 - 20:00 的主事件
→ 系统默认提前 1 小时提醒
→ 实际 08:00 弹提醒
```

也就是说，本项目不再依赖 `.ics` 里的 `VALARM`，而是通过调整事件开始时间来适配 Apple 日历的默认提醒机制。

---

## 当前日历效果

每个限行日会生成 **2 个日程事件**：

| 事件 | 日历显示时间 | 实际提醒时间 | 说明 |
| --- | --- | --- | --- |
| 前一天提醒事件 | 前一天 21:00 - 21:05 | 前一天 20:00 | 利用系统默认提前 1 小时提醒 |
| 主限行事件 | 当天 09:00 - 20:00 | 当天 08:00 | 实际限行时间为 07:00 - 20:00，写在标题和描述里 |

主限行事件标题为：

```text
北京尾号4/9限行（实际07:00-20:00）
```

这样虽然日历事件从 **09:00** 开始显示，但标题和描述会明确说明实际限行时间是：

```text
07:00 - 20:00
```

---

## 当前限行规则

本仓库当前内置 **2026-03-30 ~ 2027-03-28** 这一轮尾号限行周期规则。

尾号 **4 / 9** 对应的限行日如下：

| 时间段 | 尾号 4/9 限行日 |
| --- | --- |
| 2026-03-30 ~ 2026-06-28 | 周三 |
| 2026-06-29 ~ 2026-09-27 | 周四 |
| 2026-09-28 ~ 2026-12-27 | 周五 |
| 2026-12-28 ~ 2027-03-28 | 周一 |

基本规则：

- 实际限行时间：**07:00 - 20:00**
- 限行范围：五环路以内道路，不含五环路
- 法定节假日、临时不限行等特殊日期，可在 `config.py` 的 `EXCLUDE_DATES` 中维护

---

## 核心逻辑

本项目采用 **周期配置 + 自动匹配尾号** 的方式生成日历。

在 `config.py` 中，不直接手动写“4/9 是周几”，而是维护每个限行周期内 **周一到周五分别对应哪些尾号**。

例如：

```python
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
]
```

其中：

```text
0 = 周一
1 = 周二
2 = 周三
3 = 周四
4 = 周五
```

程序会自动查找：

```python
TARGET_TAIL_NUMBERS = "4/9"
```

在每个周期中对应的星期，然后生成该周期内所有对应日期的限行事件。

---

## 项目结构

```text
beijing-traffic-limit-calendar/
├── config.py
├── generate_ics.py
├── generate_index.py
├── docs/
│   ├── index.html
│   └── beijing_49_limit.ics
├── .gitignore
└── README.md
```

| 文件 | 说明 |
| --- | --- |
| `config.py` | 限行周期、目标尾号、提醒偏移策略、事件文案、输出路径等配置 |
| `generate_ics.py` | 根据配置生成 `.ics` 文件 |
| `generate_index.py` | 根据配置生成 GitHub Pages 首页 |
| `docs/index.html` | GitHub Pages 首页 |
| `docs/beijing_49_limit.ics` | 生成后的日历订阅文件 |
| `.gitignore` | 忽略 Python 缓存等无关文件 |
| `README.md` | 项目说明文档 |

---

## 环境要求

- Python 3.9+
- 无第三方依赖
- 使用 Python 标准库中的 `zoneinfo`

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/LXuanHou/beijing-traffic-limit-calendar.git
cd beijing-traffic-limit-calendar
```

### 2. 生成 ICS 文件和首页

```bash
python3 generate_ics.py
python3 generate_index.py
```

成功后会生成：

```text
docs/beijing_49_limit.ics
docs/index.html
```

`generate_ics.py` 成功输出示例：

```text
Generated: docs/beijing_49_limit.ics
Total events: 104
Main limit events: 52
Previous-day reminder events: 52

Target tail numbers:
  4/9

Limit periods:
  2026年第1轮限行周期: 2026-03-30 ~ 2026-06-28, 周三 限行
  2026年第2轮限行周期: 2026-06-29 ~ 2026-09-27, 周四 限行
  2026年第3轮限行周期: 2026-09-28 ~ 2026-12-27, 周五 限行
  2026年第4轮限行周期: 2026-12-28 ~ 2027-03-28, 周一 限行

Reminder strategy:
  不写 VALARM，利用系统默认提前 60 分钟提醒
  前一天 21:00 - 21:05 事件 → 实际 20:00 提醒
  当天 09:00 - 20:00 事件 → 实际 08:00 提醒
  实际限行时间 07:00 - 20:00 写在标题和描述中
```

---

## 检查生成结果

检查前一天提醒事件：

```bash
grep -A8 -B3 "SUMMARY:明天北京尾号4/9限行" docs/beijing_49_limit.ics | head -30
```

应该能看到类似：

```ics
DTSTART;TZID=Asia/Shanghai:20260512T210000
DTEND;TZID=Asia/Shanghai:20260512T210500
SUMMARY:明天北京尾号4/9限行
```

检查主限行事件：

```bash
grep -A10 -B3 "SUMMARY:北京尾号4/9限行" docs/beijing_49_limit.ics | head -40
```

应该能看到类似：

```ics
DTSTART;TZID=Asia/Shanghai:20260513T090000
DTEND;TZID=Asia/Shanghai:20260513T200000
SUMMARY:北京尾号4/9限行（实际07:00-20:00）
```

确认不写入 `VALARM`：

```bash
grep -n "VALARM" docs/beijing_49_limit.ics
```

如果没有输出，说明当前方案正确：完全依赖系统默认提醒。

---

## 订阅日历

### 方式一：GitHub Pages 页面

打开：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/
```

页面中提供：

- ICS 下载
- 订阅链接
- iOS 使用说明
- 国产安卓使用说明

### 方式二：直接 URL 订阅

订阅地址：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

常见客户端添加方式：

| 平台 | 添加方式 |
| --- | --- |
| iOS | 设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历 |
| macOS 日历 | 文件 → 新建日历订阅 |
| Google Calendar | 其他日历 → 通过网址添加 |
| Outlook | 添加日历 → 从 Internet 订阅 |

---

## 国产安卓手机使用说明

国产安卓系统日历对 `.ics` 的支持不完全一致。建议按以下顺序尝试：

### 方式一：URL 订阅，推荐

如果系统日历支持“订阅日历 / URL 导入 / 网络日历 / 添加日历”，可以直接添加：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

这种方式会随 GitHub Pages 上的 `.ics` 更新而自动同步。

### 方式二：下载 ICS 文件导入

如果系统日历不支持 URL 订阅，可以打开：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/
```

点击“下载 ICS 文件”，然后用系统日历打开并导入。

注意：导入是一次性的，后续规则更新后需要重新下载导入。

### 方式三：通过 Outlook / Google Calendar 中转

如果系统日历既不支持 URL 订阅，也不支持 ICS 导入，可以使用 Outlook、Google Calendar 或其他支持 ICS 的日历服务中转。

---

## GitHub Pages 部署

本项目默认将生成产物放在 `docs/` 目录，适合直接使用 GitHub Pages 托管。

进入 GitHub 仓库设置：

```text
Settings → Pages
```

设置：

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

保存后，等待 GitHub Pages 构建完成。

最终首页地址：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/
```

最终订阅链接：

```text
https://lxuanhou.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

---

## 自定义配置

所有主要配置都集中在 `config.py` 中。

| 配置项 | 说明 |
| --- | --- |
| `CALENDAR_NAME` | 日历显示名称 |
| `TIMEZONE` | 时区，默认 `Asia/Shanghai` |
| `TARGET_TAIL_NUMBERS` | 目标尾号，默认 `4/9` |
| `ACTUAL_LIMIT_START_HOUR` / `ACTUAL_LIMIT_END_HOUR` | 实际限行起止时间 |
| `SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES` | 系统默认提前提醒时间，当前按 60 分钟设计 |
| `PREVIOUS_DAY_REMINDER_EVENT_HOUR` / `PREVIOUS_DAY_REMINDER_EVENT_MINUTE` | 前一天提醒事件的实际日历时间，默认 21:00 |
| `MAIN_EVENT_START_HOUR` / `MAIN_EVENT_END_HOUR` | 主限行事件的日历显示时间，默认 09:00 - 20:00 |
| `EVENT_SUMMARY` | 主限行事件标题 |
| `EVENT_DESCRIPTION` | 主限行事件描述 |
| `LIMIT_PERIODS` | 官方限行周期和每个工作日对应的尾号 |
| `EXCLUDE_DATES` | 不限行的特殊日期 |
| `OUTPUT_ICS_PATH` | `.ics` 输出路径 |

---

## 想生成其他尾号的日历？

例如想生成尾号 `1/6` 的日历，只需要修改 `config.py`：

```python
TARGET_TAIL_NUMBERS = "1/6"

CALENDAR_NAME = "北京尾号1/6限行"

PREVIOUS_DAY_REMINDER_SUMMARY = "明天北京尾号1/6限行"
PREVIOUS_DAY_REMINDER_DESCRIPTION = (
    "明天北京尾号1/6限行，请提前安排出行。"
)

EVENT_SUMMARY = "北京尾号1/6限行（实际07:00-20:00）"
EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号1和6。"
    "实际限行时间为07:00-20:00，范围为五环路以内道路，不含五环路。"
    "本日历事件设置为09:00-20:00，是为了利用系统默认提前1小时提醒，在08:00弹出提醒。"
)

OUTPUT_ICS_PATH = "docs/beijing_16_limit.ics"
```

然后重新执行：

```bash
python3 generate_ics.py
python3 generate_index.py
```

---

## 更新下一年度规则

当北京市发布下一年度尾号限行通告后，按官方通告更新 `config.py` 中的 `LIMIT_PERIODS`。

更新后重新生成：

```bash
python3 generate_ics.py
python3 generate_index.py
```

然后提交并推送：

```bash
git add config.py generate_ics.py generate_index.py README.md docs/
git commit -m "update traffic restriction calendar rules"
git push
```

如果订阅链接不变，已经订阅的设备会在日历客户端下次刷新时同步到新规则。

---

## 维护特殊不限行日期

如果某些日期虽然落在限行星期，但因为节假日或官方临时通知不限行，可以加入 `EXCLUDE_DATES`。

示例：

```python
EXCLUDE_DATES = {
    date(2026, 5, 1),
    date(2026, 10, 1),
}
```

加入后重新生成 `.ics`，这些日期就不会出现在订阅日历中。

---

## 常见问题

### 1. 为什么不直接写 `VALARM`？

Apple 日历对外部订阅 `.ics` 的 `VALARM` 支持不稳定。  
可能出现 `.ics` 写了提醒，但 Apple 仍然忽略，或者直接套用系统默认提醒。

所以当前版本不再写 `VALARM`，而是反向利用系统默认提醒。

### 2. 为什么主限行事件是 09:00 - 20:00，而不是 07:00 - 20:00？

实际限行时间仍然是：

```text
07:00 - 20:00
```

但为了让 Apple 默认“开始前 1 小时提醒”在 **08:00** 弹出，主事件必须从 **09:00** 开始。

实际限行时间已经写在事件标题和描述中：

```text
北京尾号4/9限行（实际07:00-20:00）
```

### 3. 如果我的系统默认提醒不是“提前 1 小时”怎么办？

当前方案要求系统默认提醒为：

```text
开始前 1 小时
```

如果你的默认提醒是 10 分钟，需要相应调整：

```text
想 20:00 提醒 → 创建 20:10 事件
想 08:00 提醒 → 创建 08:10 事件
```

也就是修改 `config.py` 中的事件开始时间配置。

### 4. iOS 订阅后没有马上更新怎么办？

iOS 订阅日历刷新不是实时的，可能需要等待一段时间。

如果想立即验证，可以删除订阅后重新添加一次。

### 5. 国产安卓手机可以订阅吗？

部分国产安卓日历 App 支持 URL 订阅，可以直接添加 `.ics` 地址。

如果系统日历不支持 URL 订阅，可以下载 `.ics` 文件后导入，但导入是一次性的，后续不会自动更新。

更通用的方式是使用支持 URL 订阅的日历服务或 App，例如 Outlook、Google Calendar 等。

---

## 注意事项

1. 本项目只是根据公开限行规则生成日历提醒，不保证覆盖所有临时交通管理措施。
2. 法定节假日、临时不限行、重大活动交通管制等特殊情况，需要在 `EXCLUDE_DATES` 中额外维护。
3. 当前版本不写 `VALARM`，提醒依赖客户端系统默认提醒设置。
4. 当前配置假设系统默认提醒为“开始前 1 小时”。
5. 如果只是本地导入 `.ics` 文件，后续规则更新不会自动同步，需要重新导入。
6. 本项目仅作为个人出行提醒工具，实际出行请以北京市交通管理部门发布的最新通知为准。

---

## License

MIT