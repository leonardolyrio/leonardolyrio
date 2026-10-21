import json
from datetime import date

# Ajuste aqui a velocidade da animacao (em segundos)
DURATION = 1.0   # duracao da animacao de cada quadradinho
STAGGER = 0.05   # atraso entre quadradinhos vizinhos (efeito de onda)

# Versao desktop: ano inteiro
DESKTOP = {"box": 10, "gap": 4, "weeks": None, "output": "contrib-heatmap.svg"}

# Versao celular: so as ultimas semanas, quadradinhos maiores.
# Menos semanas = quadradinhos maiores na tela do celular.
MOBILE = {"box": 12, "gap": 3, "weeks": 26, "output": "contrib-heatmap-mobile.svg"}

LEFT = 32        # espaco para Mon/Wed/Fri
TOP = 22         # espaco para os meses
FOOTER = 26      # espaco para a legenda
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data():
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    days = sorted(data["days"], key=lambda d: d["date"])
    return days, data.get("total")


def build_weeks(days):
    """Agrupa os dias em colunas (semanas) de verdade: domingo no topo, sabado embaixo."""
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # 0 = domingo
    weeks = [[None] * 7]
    for i, day in enumerate(days):
        pos = i + offset
        week_idx, row = divmod(pos, 7)
        while len(weeks) <= week_idx:
            weeks.append([None] * 7)
        weeks[week_idx][row] = day
    return weeks


def render_heatmap(weeks, box, gap, output, caption):
    pitch = box + gap
    width = LEFT + len(weeks) * pitch + 10
    height = TOP + 7 * pitch + FOOTER

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .box {{ opacity: 0; animation: fadeSlide {DURATION}s ease-out forwards; rx: 2; ry: 2; }}')
    svg.append('    @keyframes fadeSlide { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }')
    svg.append('    .lbl { font: 10px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #57606a; }')
    svg.append('    .cap { font: 700 11px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #1f2328; }')

    # Cores: padrão (modo claro - igual ao original do GitHub)
    svg.append('    .level-0 { fill: #ebedf0; } .level-1 { fill: #9be9a8; } .level-2 { fill: #40c463; } .level-3 { fill: #30a14e; } .level-4 { fill: #216e39; }')

    # Cores: modo escuro (ativado automaticamente pelas preferências do sistema/GitHub)
    svg.append('    @media (prefers-color-scheme: dark) {')
    svg.append('      .level-0 { fill: #1f2630; } .level-1 { fill: #0e4429; } .level-2 { fill: #006d32; } .level-3 { fill: #26a641; } .level-4 { fill: #39d353; }')
    svg.append('      .lbl { fill: #8b949e; } .cap { fill: #e6edf3; }')
    svg.append('    }')
    svg.append('  </style>')

    # Meses no topo: um rotulo onde o mes muda. Se dois rotulos ficariam colados,
    # fica o mais novo (assim o primeiro mes, quando comeca no fim, nao esconde o seguinte).
    labels, last_month = [], None
    for w_idx, week in enumerate(weeks):
        first_day = next((d for d in week if d), None)
        if not first_day:
            continue
        month = int(first_day["date"][5:7])
        if month != last_month:
            labels.append((LEFT + w_idx * pitch, month))
            last_month = month
    for i, (x, month) in enumerate(labels):
        if i + 1 < len(labels) and labels[i + 1][0] - x < 3 * pitch:
            continue
        svg.append(f'  <text class="lbl" x="{x}" y="{TOP - 8}">{MONTHS[month - 1]}</text>')

    # Dias da semana na lateral
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + row * pitch + box - 1
        svg.append(f'  <text class="lbl" x="2" y="{y}">{name}</text>')

    # Quadradinhos
    for w_idx, week in enumerate(weeks):
        x = LEFT + w_idx * pitch
        for d_idx, day in enumerate(week):
            if day is None:
                continue
            y = TOP + d_idx * pitch
            level = min(day["level"], 4)
            delay = (w_idx + d_idx) * STAGGER
            svg.append(f'  <rect class="box level-{level}" x="{x}" y="{y}" width="{box}" height="{box}" style="animation-delay: {delay:.2f}s" />')

    if caption:
        svg.append(f'  <text class="cap" x="{LEFT}" y="{height - 8}">{caption}</text>')

    svg.append('</svg>')

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Heatmap gerado: {output}")


def make_caption(selected_weeks, total, is_full_year):
    if is_full_year:
        return f"{total:,} contributions in the last year" if total is not None else ""
    counts = [d["count"] for w in selected_weeks for d in w if d]
    if any(c is None for c in counts):
        return ""
    return f"{sum(counts):,} contributions in the last {len(selected_weeks)} weeks"


def main():
    days, total = load_data()
    weeks = build_weeks(days)
    for cfg in (DESKTOP, MOBILE):
        selected = weeks[-cfg["weeks"]:] if cfg["weeks"] else weeks
        caption = make_caption(selected, total, cfg["weeks"] is None)
        render_heatmap(selected, cfg["box"], cfg["gap"], cfg["output"], caption)


if __name__ == "__main__":
    main()
