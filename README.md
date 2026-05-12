# 北京尾号限行日历

一个根据北京市机动车工作日尾号限行规则，自动生成 `.ics` 日历订阅文件的小工具。

订阅生成后的日历后，每个限行日会在手机 / 电脑日历中生成限行日程，并支持两次提醒：

- **前一天 20:00**：提醒明天限行
- **当天 08:00**：提醒当前已进入限行时段

当前版本默认针对 **车牌尾号 4 / 9** 的车辆。其他尾号可以通过修改 `config.py` 后自行生成。

---

## 订阅地址

当前生成的日历订阅地址：

```text
https://xuanhoucas.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

iOS 添加路径：

```text
设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历
```

填入上面的 `.ics` 地址即可。

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

- 限行时间：**07:00 - 20:00**
- 限行范围：五环路以内道路，不含五环路
- 法定节假日、临时不限行等特殊日期，可在 `config.py` 的 `EXCLUDE_DATES` 中维护

---

## 日程与提醒设计

每个限行日会生成 **2 个日程事件**：

| 事件 | 时间 | 提醒方式 | 说明 |
| --- | --- | --- | --- |
| 前一天提醒事件 | 前一天 20:00 - 20:05 | 日程开始时提醒，`TRIGGER;RELATED=START:PT0S` | 提醒明天尾号 4/9 限行 |
| 主限行事件 | 当天 07:00 - 20:00 | 日程开始后 1 小时提醒，`TRIGGER;RELATED=START:PT1H` | 也就是当天 08:00 提醒 |

也就是说，日历中会显示：

```text
前一天 20:00 - 20:05：明天北京尾号4/9限行
当天 07:00 - 20:00：北京尾号4/9限行
```

当前版本**不再单独生成**：

```text
当天 08:00 - 08:05：今天北京尾号4/9限行
```

当天 08:00 的提醒写入主限行事件的 `VALARM` 中。

---

## Apple 日历提醒兼容设计

Apple 日历 / iCloud 日历对订阅 `.ics` 中的提醒解析比较敏感。为了尽量避免系统套用默认提醒，本项目的 `VALARM` 采用更接近 Apple Calendar 的写法：

```ics
BEGIN:VALARM
UID:...
X-WR-ALARMUID:...
X-APPLE-DEFAULT-ALARM:TRUE
ACTION:DISPLAY
DESCRIPTION:...
TRIGGER;RELATED=START:PT1H
END:VALARM
```

其中：

- `UID`：提醒自身的唯一 ID
- `X-WR-ALARMUID`：Apple 日历常见的提醒 ID 扩展字段
- `X-APPLE-DEFAULT-ALARM:TRUE`：Apple 日历常见的默认提醒标记
- `TRIGGER;RELATED=START:PT0S`：日程开始时提醒
- `TRIGGER;RELATED=START:PT1H`：日程开始后 1 小时提醒

如果修改提醒逻辑后 Apple 日历仍显示旧提醒，可以修改 `config.py` 中的：

```python
EVENT_UID_VERSION = "v4"
```

例如改成：

```python
EVENT_UID_VERSION = "v5"
```

然后重新生成 `.ics` 并推送。这样会让 Apple 日历把事件识别为新版本，减少旧缓存影响。

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

这样做的好处是：

- 后续更新规则时，只需要按官方通告填写完整周期规则
- 不需要手动计算 4/9 到底轮到周几
- 后续想生成其他尾号日历，只需要改 `TARGET_TAIL_NUMBERS`
- 周期配置更直观，也更不容易出错

---

## 项目结构

```text
beijing-traffic-limit-calendar/
├── config.py
├── generate_ics.py
├── docs/
│   └── beijing_49_limit.ics
├── .gitignore
└── README.md
```

| 文件 | 说明 |
| --- | --- |
| `config.py` | 限行周期、目标尾号、提醒时间、事件文案、输出路径等配置 |
| `generate_ics.py` | 根据配置生成 `.ics` 文件 |
| `docs/beijing_49_limit.ics` | 生成后的日历订阅文件，用于 GitHub Pages 托管 |
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
git clone https://github.com/xuanHouCAS/beijing-traffic-limit-calendar.git
cd beijing-traffic-limit-calendar
```

### 2. 生成 ICS 文件

```bash
python3 generate_ics.py
```

成功后会看到类似输出：

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
  前一天 20:00 - 20:05：明天北京尾号4/9限行，开始时提醒
  当天 07:00 - 20:00：北京尾号4/9限行，开始后 1 小时提醒
  当天 08:00 - 08:05：不再生成独立提醒事件

Apple Calendar alarm style:
  UID
  X-WR-ALARMUID
  X-APPLE-DEFAULT-ALARM:TRUE
  TRIGGER;RELATED=START

UID version:
  v4
```

生成文件默认位于：

```text
docs/beijing_49_limit.ics
```

---

## 检查生成结果

检查前一天提醒事件：

```bash
grep -A14 -B3 "SUMMARY:明天北京尾号4/9限行" docs/beijing_49_limit.ics | head -40
```

应该能看到类似：

```ics
DTSTART;TZID=Asia/Shanghai:20260512T200000
DTEND;TZID=Asia/Shanghai:20260512T200500
SUMMARY:明天北京尾号4/9限行
BEGIN:VALARM
UID:...
X-WR-ALARMUID:...
X-APPLE-DEFAULT-ALARM:TRUE
ACTION:DISPLAY
DESCRIPTION:明天北京尾号4/9限行
TRIGGER;RELATED=START:PT0S
END:VALARM
```

检查主限行事件：

```bash
grep -A18 -B3 "SUMMARY:北京尾号4/9限行" docs/beijing_49_limit.ics | head -50
```

应该能看到类似：

```ics
DTSTART;TZID=Asia/Shanghai:20260513T070000
DTEND;TZID=Asia/Shanghai:20260513T200000
SUMMARY:北京尾号4/9限行
BEGIN:VALARM
UID:...
X-WR-ALARMUID:...
X-APPLE-DEFAULT-ALARM:TRUE
ACTION:DISPLAY
DESCRIPTION:今天北京尾号4/9限行，当前已进入限行时段。
TRIGGER;RELATED=START:PT1H
END:VALARM
```

确认不再生成当天 08:00 短事件：

```bash
grep -n "SUMMARY:今天北京尾号4/9限行" docs/beijing_49_limit.ics
```

如果没有输出，就说明没有生成独立的当天 08:00 - 08:05 短事件。

---

## 订阅日历

### 方式一：本地导入

可以直接下载或打开生成的文件：

```text
docs/beijing_49_limit.ics
```

然后导入到 Apple 日历、Outlook、Google Calendar 等客户端。

这种方式是一次性导入，后续规则更新后不会自动同步，需要重新导入。

---

### 方式二：URL 订阅，推荐

将 `docs/` 目录通过 GitHub Pages 或其他静态托管服务发布后，可以获得一个公网 HTTPS 地址，例如：

```text
https://xuanhoucas.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

常见客户端添加方式：

| 平台 | 添加方式 |
| --- | --- |
| iOS | 设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历 |
| macOS 日历 | 文件 → 新建日历订阅 |
| Google Calendar | 其他日历 → 通过网址添加 |
| Outlook | 添加日历 → 从 Internet 订阅 |

订阅方式下，日历客户端会定期拉取最新 `.ics` 文件。以后只要更新 GitHub 仓库中的 `.ics` 文件，订阅者无需更换链接。

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

最终订阅链接格式为：

```text
https://你的用户名.github.io/仓库名/beijing_49_limit.ics
```

本仓库对应：

```text
https://xuanhoucas.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

---

## 自定义配置

所有主要配置都集中在 `config.py` 中。

| 配置项 | 说明 |
| --- | --- |
| `CALENDAR_NAME` | 日历显示名称 |
| `TIMEZONE` | 时区，默认 `Asia/Shanghai` |
| `EVENT_UID_VERSION` | 事件 UID 版本号，用于刷新 Apple 日历缓存 |
| `LIMIT_START_HOUR` / `LIMIT_START_MINUTE` | 限行开始时间 |
| `LIMIT_END_HOUR` / `LIMIT_END_MINUTE` | 限行结束时间 |
| `TARGET_TAIL_NUMBERS` | 目标尾号，默认 `4/9` |
| `EVENT_SUMMARY` | 主限行事件标题 |
| `EVENT_DESCRIPTION` | 主限行事件描述 |
| `ENABLE_PREVIOUS_DAY_REMINDER_EVENT` | 是否生成前一天独立提醒事件 |
| `PREVIOUS_DAY_REMINDER_HOUR` / `PREVIOUS_DAY_REMINDER_MINUTE` | 前一天提醒事件时间 |
| `MAIN_EVENT_REMINDER_TRIGGER` | 主限行事件提醒时间，默认 `PT1H` |
| `LIMIT_PERIODS` | 官方限行周期和每个工作日对应的尾号 |
| `EXCLUDE_DATES` | 不限行的特殊日期 |
| `OUTPUT_ICS_PATH` | `.ics` 输出路径 |

---

## 想生成其他尾号的日历？

例如想生成尾号 `1/6` 的日历，只需要修改 `config.py`：

```python
TARGET_TAIL_NUMBERS = "1/6"

CALENDAR_NAME = "北京尾号1/6限行"

EVENT_SUMMARY = "北京尾号1/6限行"

EVENT_DESCRIPTION = (
    "北京工作日机动车尾号限行：尾号1和6，"
    "限行时间7:00-20:00，范围为五环路以内道路，不含五环路。"
)

OUTPUT_ICS_PATH = "docs/beijing_16_limit.ics"
```

然后重新执行：

```bash
python3 generate_ics.py
```

即可生成：

```text
docs/beijing_16_limit.ics
```

如果需要通过 GitHub Pages 订阅，新订阅地址为：

```text
https://xuanhoucas.github.io/beijing-traffic-limit-calendar/beijing_16_limit.ics
```

---

## 更新下一年度规则

当北京市发布下一年度尾号限行通告后，按官方通告更新 `config.py` 中的 `LIMIT_PERIODS`。

例如新增或替换为下一年度的周期配置：

```python
LIMIT_PERIODS = [
    {
        "name": "2027年第1轮限行周期",
        "start": date(2027, 3, 29),
        "end": date(2027, 6, 27),
        "tail_numbers_by_weekday": {
            0: "待填写",
            1: "待填写",
            2: "待填写",
            3: "待填写",
            4: "待填写",
        },
    },
]
```

更新后重新生成：

```bash
python3 generate_ics.py
```

然后提交并推送：

```bash
git add config.py generate_ics.py docs/beijing_49_limit.ics
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

### 1. 为什么不直接用 RRULE 循环规则？

北京尾号限行会按照官方周期轮换，每个周期对应的星期不同，并且每年政策可能调整。

直接使用永久 RRULE 容易在规则变化后产生错误。

本项目选择每年根据官方通告生成明确日期事件，更直观，也更容易维护。

### 2. 为什么访问 GitHub Pages 首页可能是 404？

本项目的核心订阅文件是：

```text
beijing_49_limit.ics
```

如果 `docs/` 目录下没有 `index.html`，访问首页可能没有内容。真正需要订阅的是 `.ics` 文件地址：

```text
https://xuanhoucas.github.io/beijing-traffic-limit-calendar/beijing_49_limit.ics
```

### 3. iOS 订阅后没有马上更新怎么办？

iOS 订阅日历刷新不是实时的，可能需要等待一段时间。

如果想立即验证，可以删除订阅后重新添加一次。

### 4. iOS 里提醒显示不符合预期怎么办？

Apple 日历可能会缓存旧的订阅事件，或者继续显示之前解析过的提醒。

建议：

1. 删除旧订阅后重新添加；
2. 确认 `.ics` 文件中已经包含最新的 `VALARM`；
3. 如果仍然不刷新，修改 `config.py` 中的 `EVENT_UID_VERSION`，例如从 `v4` 改成 `v5`；
4. 重新生成 `.ics` 并推送；
5. 再次删除旧订阅并重新添加。

### 5. 国产安卓手机可以订阅吗？

部分国产安卓日历 App 支持 URL 订阅，可以直接添加 `.ics` 地址。

如果系统日历不支持 URL 订阅，可以下载 `.ics` 文件后导入，但导入是一次性的，后续不会自动更新。

更通用的方式是使用支持 URL 订阅的日历服务或 App，例如 Google Calendar、Outlook 等。

---

## 注意事项

1. 本项目只是根据公开限行规则生成日历提醒，不保证覆盖所有临时交通管理措施。
2. 法定节假日、临时不限行、重大活动交通管制等特殊情况，需要在 `EXCLUDE_DATES` 中额外维护。
3. 不同日历客户端对订阅日历的刷新频率不同，iOS、Google Calendar 等可能不会立即刷新。
4. 如果只是本地导入 `.ics` 文件，后续规则更新不会自动同步，需要重新导入。
5. 本项目仅作为个人出行提醒工具，实际出行请以北京市交通管理部门发布的最新通知为准。

---

## License

MIT