import json
from collections import OrderedDict
from datetime import date

OUTPUT = "stats.svg"
USERNAME = "leonardolyrio"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

WIDTH, HEIGHT = 400, 360
SANS = '-apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
MONO = '"SF Mono", Menlo, Consolas, "Courier New", monospace'


def plural(n):
    return "day" if n == 1 else "days"


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}"


def load_days():
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return sorted(data["days"], key=lambda d: d["date"]), data.get("total")


def is_active(day):
    # Sem contagem (plano B do fetch), usa o nivel de cor: nivel > 0 = teve contribuicao
    if day["count"] is not None:
        return day["count"] > 0
    return day["level"] > 0


def compute_stats(days, total):
    has_counts = all(d["count"] is not None for d in days)

    # Streak atual: o dia de hoje so quebra a sequencia depois que acaba, entao ignora hoje se for zero
    end = len(days) - 1
    if not is_active(days[end]):
        end -= 1
    cur_len, start = 0, end
    while start >= 0 and is_active(days[start]):
        cur_len += 1
        start -= 1
    current = {
        "len": cur_len,
        "range": f"{fmt_date(days[start + 1]['date'])} – {fmt_date(days[end]['date'])}" if cur_len else "no active streak",
    }

    # Maior streak
    best_len, best_start, run, run_start = 0, 0, 0, 0
    for i, day in enumerate(days):
        if is_active(day):
            if run == 0:
                run_start = i
            run += 1
            if run > best_len:
                best_len, best_start = run, run_start
        else:
            run = 0
    longest = {
        "len": best_len,
        "range": f"{fmt_date(days[best_start]['date'])} – {fmt_date(days[best_start + best_len - 1]['date'])}" if best_len else "—",
    }

    active_days = sum(1 for d in days if is_active(d))
    stats = {
        "current": current,
        "longest": longest,
        "active_days": active_days,
        "n_days": len(days),
        "has_counts": has_counts,
    }

    if has_counts:
        total = total if total is not None else sum(d["count"] for d in days)
        best_day = max(days, key=lambda d: d["count"])
        months = OrderedDict()
        for d in days:
            key = d["date"][:7]
            months[key] = months.get(key, 0) + d["count"]
        stats.update({
            "total": total,
            "best_count": best_day["count"],
            "best_date": fmt_date(best_day["date"]),
            "avg": total / active_days if active_days else 0,
            "months": [(int(k[5:7]), v) for k, v in months.items()],
        })
    return stats


def tile(x, y, i, label, value, unit, sub, accent=False):
    value_class = "value accent" if accent else "value"
    unit_part = f'<tspan class="unit" dx="5">{unit}</tspan>' if unit else ""
    return f'''  <g class="tile" style="animation-delay: {i * 0.12:.2f}s">
    <rect class="panel" x="{x}" y="{y}" width="181" height="62" rx="6" />
    <text class="label" x="{x + 10}" y="{y + 16}">$ {label}</text>
    <text class="{value_class}" x="{x + 10}" y="{y + 41}">{value}{unit_part}</text>
    <text class="sub" x="{x + 10}" y="{y + 56}">{sub}</text>
  </g>'''


def build_svg(stats):
    has_counts = stats["has_counts"]

    def num(key, formatter=lambda v: f"{v:,}"):
        return formatter(stats[key]) if has_counts else "—"

    pct = round(100 * stats["active_days"] / stats["n_days"])
    tiles = [
        tile(12, 30, 0, "current streak", stats["current"]["len"], plural(stats["current"]["len"]), stats["current"]["range"], accent=True),
        tile(207, 30, 1, "longest streak", stats["longest"]["len"], plural(stats["longest"]["len"]), stats["longest"]["range"]),
        tile(12, 98, 2, "contributions", num("total"), "", "in the last year"),
        tile(207, 98, 3, "active days", stats["active_days"], f'/ {stats["n_days"]}', f"{pct}% of the year"),
        tile(12, 166, 4, "best day", num("best_count"), "", stats["best_date"] if has_counts else "—"),
        tile(207, 166, 5, "avg / active day", num("avg", lambda v: f"{v:.1f}"), "", "contributions"),
    ]

    # Grafico de barras por mes
    chart_y, chart_h = 234, 118
    base_y = chart_y + chart_h - 18
    max_bar = 62
    chart = [
        f'  <g class="tile" style="animation-delay: 0.72s">',
        f'    <rect class="panel" x="12" y="{chart_y}" width="376" height="{chart_h}" rx="6" />',
        f'    <text class="label" x="22" y="{chart_y + 16}">$ contributions / month</text>',
        '  </g>',
    ]
    if has_counts:
        months = stats["months"]
        peak = max(v for _, v in months) or 1
        slot = (376 - 20) / len(months)
        bar_w = 17
        for i, (month, value) in enumerate(months):
            h = max(2, round(value / peak * max_bar)) if value else 1
            x = 22 + i * slot + (slot - bar_w) / 2
            cls = "bar hi" if value == peak else "bar"
            chart.append(f'  <rect class="{cls}" x="{x:.1f}" y="{base_y - h}" width="{bar_w}" height="{h}" rx="2" style="animation-delay: {0.9 + i * 0.05:.2f}s" />')
            if value == peak:
                chart.append(f'  <text class="peak" x="{x + bar_w / 2:.1f}" y="{base_y - h - 4}" text-anchor="middle">{value:,}</text>')
            chart.append(f'  <text class="month" x="{x + bar_w / 2:.1f}" y="{chart_y + chart_h - 6}" text-anchor="middle">{MONTHS[month - 1][0]}</text>')
    else:
        chart.append(f'  <text class="sub" x="200" y="{chart_y + 70}" text-anchor="middle">waiting for the first workflow run…</text>')

    style = f'''  <style>
    .frame {{ fill: #ffffff; stroke: #d0d7de; }}
    .panel {{ fill: #f6f8fa; stroke: #d0d7de; stroke-width: 1; }}
    .title {{ font: 9px {MONO}; fill: #57606a; }}
    .label {{ font: 10px {MONO}; fill: #57606a; }}
    .sub, .unit, .month {{ font: 10px {SANS}; fill: #57606a; }}
    .value {{ font: 700 26px {SANS}; fill: #1f2328; }}
    .value .unit {{ font-weight: 400; }}
    .accent {{ fill: #1a7f37; }}
    .bar {{ fill: #2da44e; }}
    .bar.hi {{ fill: #1a7f37; }}
    .peak {{ font: 700 9px {SANS}; fill: #1f2328; }}
    .tile {{ opacity: 0; animation: fadeIn 0.6s ease-out forwards; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .bar {{ transform-box: fill-box; transform-origin: bottom; transform: scaleY(0); animation: grow 0.8s ease-out forwards; }}
    @keyframes grow {{ to {{ transform: scaleY(1); }} }}
    @media (prefers-color-scheme: dark) {{
      .frame {{ fill: #0d1117; stroke: #30363d; }}
      .panel {{ fill: #161b22; stroke: #30363d; }}
      .title, .label, .sub, .unit, .month {{ fill: #8b949e; }}
      .value, .peak {{ fill: #e6edf3; }}
      .accent {{ fill: #3fb950; }}
      .bar {{ fill: #2ea043; }}
      .bar.hi {{ fill: #56d364; }}
    }}
  </style>'''

    chrome = f'''  <rect class="frame" x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8" />
  <circle cx="16" cy="14" r="4" fill="#ff5f56" />
  <circle cx="29" cy="14" r="4" fill="#ffbd2e" />
  <circle cx="42" cy="14" r="4" fill="#27c93f" />
  <text class="title" x="200" y="17" text-anchor="middle">{USERNAME}@github: ~ $ ./stats.sh</text>'''

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">',
        style,
        chrome,
        *tiles,
        *chart,
        '</svg>',
    ])


def main():
    days, total = load_days()
    stats = compute_stats(days, total)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(build_svg(stats))
    print(f"Stats gerado: {OUTPUT}")


if __name__ == "__main__":
    main()
