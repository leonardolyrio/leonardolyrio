import json

# A paleta clássica do GitHub (do vazio ao mais claro)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX_SIZE = 10
GAP = 4

def render_heatmap():
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)["days"]

    # Separar os dados em semanas (7 dias por coluna)
    weeks = []
    current_week = []
    for day in data:
        current_week.append(day)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)

    width = len(weeks) * (BOX_SIZE + GAP) + 20
    height = 7 * (BOX_SIZE + GAP) + 20

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <style>')
    # Animação que faz os quadradinhos caírem/deslizarem suavemente
    svg.append('    .box { opacity: 0; animation: fadeSlide 0.6s forwards; rx: 2; ry: 2; }')
    svg.append('    @keyframes fadeSlide { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }')
    svg.append('  </style>')

    # Desenhar os quadradinhos
    for w_idx, week in enumerate(weeks):
        x = 10 + w_idx * (BOX_SIZE + GAP)
        for d_idx, day in enumerate(week):
            y = 10 + d_idx * (BOX_SIZE + GAP)
            level = min(day["level"], len(PALETTE) - 1)
            color = PALETTE[level]
            # O truque visual do tutorial: atraso baseado na diagonal (coluna + linha)
            delay = (w_idx + d_idx) * 0.02
            
            svg.append(f'  <rect class="box" x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" fill="{color}" style="animation-delay: {delay:.2f}s" />')

    svg.append('</svg>')

    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("Heatmap SVG gerado com sucesso: contrib-heatmap.svg")

if __name__ == "__main__":
    render_heatmap()
