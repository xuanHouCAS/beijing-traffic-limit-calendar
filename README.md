# 北京尾号 4/9 限行日历

一个根据北京市机动车工作日尾号限行规则，自动生成 `.ics` 日历订阅文件的小工具。

订阅生成后的日历后，每个限行日都会在你的手机/电脑日历里自动出现一条 **07:00 - 20:00 的提醒**，再也不用记本月轮到周几限行了。

> 当前版本只针对 **车牌尾号 4 / 9** 的车主（其他尾号请改 `config.py` 中的常量后自行生成）。

---

## 限行规则

北京机动车每 13 周轮换一次尾号对应的限行日，本仓库已经内置 **2026-03-30 ~ 2027-03-28** 这一轮换周期的规则：

| 时间段 | 尾号 4/9 限行日 |
| --- | --- |
| 2026-03-30 ~ 2026-06-28 | 周三 |
| 2026-06-29 ~ 2026-09-27 | 周四 |
| 2026-09-28 ~ 2026-12-27 | 周五 |
| 2026-12-28 ~ 2027-03-28 | 周一 |

- 限行时间：**07:00 - 20:00**
- 限行范围：五环路以内道路（不含五环路）
- 节假日、调休等不限行的日期，可在 `config.py` 的 `EXCLUDE_DATES` 中维护

> 规则下一轮（2027-03-29 之后）官方公布后，更新 `config.py` 中的 `RULES` 即可。

---

## 项目结构

```text
beijing-traffic-limit-calendar/
├── config.py              # 限行规则、时间、文案等所有可配置项
├── generate_ics.py        # 生成 .ics 文件的脚本
├── docs/
│   └── beijing_49_limit.ics  # 生成产物，建议用 GitHub Pages 托管
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.9+（依赖标准库的 `zoneinfo`）
- 无第三方依赖，开箱即用

### 生成 ICS 文件

```bash
python generate_ics.py
```

成功后会看到类似输出：

```text
Generated: docs/beijing_49_limit.ics
Events: 52
```

生成产物默认位于 `docs/beijing_49_limit.ics`。

---

## 订阅日历

### 方式一：本地导入（一次性）

直接把生成的 `docs/beijing_49_limit.ics` 双击导入到 Apple 日历 / Outlook / Google 日历即可。

> 缺点：之后规则更新需要重新导入。

### 方式二：URL 订阅（推荐）

把仓库部署到 GitHub Pages（或任意可公网访问的静态托管），获得一个 `https://xxx.github.io/.../beijing_49_limit.ics` 链接：

- **iOS**：设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历
- **macOS 日历**：文件 → 新建日历订阅
- **Google Calendar**：左侧「其他日历」→ 通过网址添加

订阅方式下，日历客户端会定期拉取最新的 `.ics`，你只需要更新仓库就能让所有订阅者同步到新规则。

---

## 自定义配置

所有可配置项都集中在 [`config.py`](./config.py) 中：

| 配置项 | 说明 |
| --- | --- |
| `CALENDAR_NAME` | 日历显示名称 |
| `TIMEZONE` | 时区，默认 `Asia/Shanghai` |
| `LIMIT_START_HOUR` / `LIMIT_END_HOUR` | 限行起止时间 |
| `EVENT_SUMMARY` / `EVENT_DESCRIPTION` | 事件标题与描述 |
| `RULES` | 各时段对应的限行星期 |
| `EXCLUDE_DATES` | 不限行的特殊日期（节假日、调休等） |
| `OUTPUT_ICS_PATH` | 生成文件的输出路径 |

### 想生成其它尾号的日历？

把 `config.py` 中 `RULES` 各时段的 `weekday` 改成你尾号对应的星期即可。例如尾号 1/6，把每段的 `weekday` 改成对应轮换的星期数（`Monday=0, ..., Friday=4`），然后修改 `CALENDAR_NAME` / `EVENT_SUMMARY` 等文案。

---

## License

MIT
