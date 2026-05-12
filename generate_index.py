from pathlib import Path
from html import escape

from config import (
    CALENDAR_NAME,
    TARGET_TAIL_NUMBERS,
    OUTPUT_ICS_PATH,
    ACTUAL_LIMIT_START_HOUR,
    ACTUAL_LIMIT_START_MINUTE,
    ACTUAL_LIMIT_END_HOUR,
    ACTUAL_LIMIT_END_MINUTE,
    LIMIT_PERIODS,
    SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES,
    PREVIOUS_DAY_REMINDER_TARGET_HOUR,
    PREVIOUS_DAY_REMINDER_TARGET_MINUTE,
    PREVIOUS_DAY_REMINDER_EVENT_HOUR,
    PREVIOUS_DAY_REMINDER_EVENT_MINUTE,
    MAIN_EVENT_START_HOUR,
    MAIN_EVENT_START_MINUTE,
    MAIN_EVENT_END_HOUR,
    MAIN_EVENT_END_MINUTE,
)

# GitHub Pages 基础地址
SITE_BASE_URL = "https://lxuanhou.github.io/beijing-traffic-limit-calendar"

# 输出 HTML 路径
OUTPUT_HTML_PATH = "docs/index.html"


def fmt_time(hour: int, minute: int) -> str:
    return f"{hour:02d}:{minute:02d}"


def build_period_rows() -> str:
    rows = []

    weekday_names = {
        0: "周一",
        1: "周二",
        2: "周三",
        3: "周四",
        4: "周五",
    }

    target = TARGET_TAIL_NUMBERS

    for period in LIMIT_PERIODS:
        target_weekday = None
        for weekday, tail_numbers in period["tail_numbers_by_weekday"].items():
            if tail_numbers == target:
                target_weekday = weekday
                break

        weekday_text = weekday_names.get(target_weekday, "未知")

        rows.append(
            f"""
            <tr>
              <td>{escape(str(period["start"]))} ~ {escape(str(period["end"]))}</td>
              <td>{escape(weekday_text)}</td>
            </tr>
            """
        )

    return "\n".join(rows)


def generate_html() -> str:
    ics_filename = Path(OUTPUT_ICS_PATH).name
    subscribe_url = f"{SITE_BASE_URL}/{ics_filename}"
    webcal_url = subscribe_url.replace("https://", "webcal://", 1)

    actual_limit_time = (
        f"{fmt_time(ACTUAL_LIMIT_START_HOUR, ACTUAL_LIMIT_START_MINUTE)}"
        f" - "
        f"{fmt_time(ACTUAL_LIMIT_END_HOUR, ACTUAL_LIMIT_END_MINUTE)}"
    )

    previous_target_time = fmt_time(
        PREVIOUS_DAY_REMINDER_TARGET_HOUR,
        PREVIOUS_DAY_REMINDER_TARGET_MINUTE,
    )
    previous_event_time = fmt_time(
        PREVIOUS_DAY_REMINDER_EVENT_HOUR,
        PREVIOUS_DAY_REMINDER_EVENT_MINUTE,
    )
    main_event_start = fmt_time(MAIN_EVENT_START_HOUR, MAIN_EVENT_START_MINUTE)
    main_event_end = fmt_time(MAIN_EVENT_END_HOUR, MAIN_EVENT_END_MINUTE)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{escape(CALENDAR_NAME)}</title>
  <style>
    :root {{
      --primary: #d92323;
      --text: #222;
      --muted: #666;
      --bg: #ffffff;
      --card: #fafafa;
      --border: #eeeeee;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      max-width: 820px;
      margin: 0 auto;
      padding: 28px 18px 52px;
      line-height: 1.68;
      color: var(--text);
      background: var(--bg);
    }}

    h1 {{
      font-size: 28px;
      margin: 0 0 8px;
      line-height: 1.25;
    }}

    h2 {{
      margin-top: 30px;
      font-size: 20px;
    }}

    p {{
      margin: 10px 0;
    }}

    .subtitle {{
      color: var(--muted);
      margin-bottom: 20px;
    }}

    .card {{
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 18px;
      margin: 18px 0;
      background: var(--card);
    }}

    code,
    pre {{
      background: #f2f2f2;
      border-radius: 8px;
      padding: 2px 6px;
      word-break: break-all;
    }}

    pre {{
      padding: 12px;
      overflow-x: auto;
      white-space: pre-wrap;
    }}

    .btn {{
      display: inline-block;
      padding: 10px 14px;
      margin: 8px 8px 8px 0;
      border-radius: 10px;
      background: var(--primary);
      color: #fff;
      text-decoration: none;
      font-weight: 700;
    }}

    .btn.secondary {{
      background: #333;
    }}

    .btn.light {{
      background: #666;
    }}

    .muted {{
      color: var(--muted);
      font-size: 14px;
    }}

    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 12px;
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
    }}

    th,
    td {{
      border: 1px solid var(--border);
      padding: 10px;
      text-align: left;
    }}

    th {{
      background: #f7f7f7;
    }}

    ul,
    ol {{
      padding-left: 22px;
    }}

    .warning {{
      border-left: 4px solid var(--primary);
      padding-left: 12px;
      color: #7a1111;
      background: #fff3f3;
    }}
  </style>
</head>
<body>
  <h1>{escape(CALENDAR_NAME)}</h1>
  <p class="subtitle">
    北京机动车尾号 {escape(TARGET_TAIL_NUMBERS)} 限行日历订阅文件。
  </p>

  <div class="card">
    <h2>订阅 / 下载</h2>
    <p>订阅链接：</p>
    <pre>{escape(subscribe_url)}</pre>

    <p>
      <a class="btn" href="./{escape(ics_filename)}">下载 ICS 文件</a>
      <a class="btn secondary" href="{escape(webcal_url)}">尝试用日历订阅打开</a>
      <a class="btn light" href="{escape(subscribe_url)}">直接打开 ICS</a>
    </p>

    <p class="muted">
      如果手机不支持 webcal 或 URL 订阅，请点击“下载 ICS 文件”，然后用系统日历导入。
    </p>
  </div>

  <div class="card">
    <h2>日历内容</h2>
    <ul>
      <li>尾号：{escape(TARGET_TAIL_NUMBERS)}</li>
      <li>实际限行时间：{escape(actual_limit_time)}</li>
      <li>限行范围：五环路以内道路，不含五环路</li>
      <li>当前规则周期：{escape(str(LIMIT_PERIODS[0]["start"]))} 至 {escape(str(LIMIT_PERIODS[-1]["end"]))}</li>
    </ul>

    <table>
      <thead>
        <tr>
          <th>时间段</th>
          <th>尾号 {escape(TARGET_TAIL_NUMBERS)} 限行日</th>
        </tr>
      </thead>
      <tbody>
        {build_period_rows()}
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>提醒策略</h2>
    <p class="warning">
      当前版本不写入 VALARM，而是反向利用客户端系统默认提醒。
    </p>

    <p>
      当前假设日历客户端默认提醒为：
      <strong>开始前 {SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES} 分钟提醒</strong>。
    </p>

    <table>
      <thead>
        <tr>
          <th>目标提醒</th>
          <th>实际创建的日历事件</th>
          <th>说明</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>前一天 {escape(previous_target_time)}</td>
          <td>前一天 {escape(previous_event_time)} - {escape(previous_event_time[:-2] + "05" if previous_event_time.endswith("00") else previous_event_time)}</td>
          <td>系统提前 {SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES} 分钟提醒，所以实际在 {escape(previous_target_time)} 弹出</td>
        </tr>
        <tr>
          <td>当天 08:00</td>
          <td>当天 {escape(main_event_start)} - {escape(main_event_end)}</td>
          <td>系统提前 {SYSTEM_DEFAULT_ALERT_BEFORE_MINUTES} 分钟提醒，所以实际在 08:00 弹出；实际限行时间写在标题和描述中</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>iPhone / iPad</h2>
    <p>添加订阅路径：</p>
    <pre>设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历</pre>
    <p>服务器填入上面的订阅链接。</p>
  </div>

  <div class="card">
    <h2>国产安卓手机</h2>
    <p>不同品牌系统日历支持不完全一致，建议按顺序尝试：</p>
    <ol>
      <li>在系统日历 App 中寻找“订阅日历 / URL 导入 / 网络日历 / 添加日历”。</li>
      <li>如果没有 URL 订阅入口，点击上方“下载 ICS 文件”，然后用系统日历打开并导入。</li>
      <li>如果系统日历不支持导入，可以使用 Outlook、Google Calendar 或其他支持 ICS 的日历 App 中转。</li>
    </ol>
    <p class="muted">
      注意：下载导入是一次性的，后续规则更新后需要重新下载导入；URL 订阅才会自动更新。
    </p>
  </div>

  <div class="card">
    <h2>更新说明</h2>
    <p>
      后续北京市发布新一轮尾号限行规则后，只需要更新项目中的
      <code>config.py</code>，重新生成 <code>.ics</code> 和本页面，然后推送到 GitHub。
    </p>
  </div>
</body>
</html>
"""


def main() -> None:
    output_path = Path(OUTPUT_HTML_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = generate_html()
    output_path.write_text(html, encoding="utf-8")

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()