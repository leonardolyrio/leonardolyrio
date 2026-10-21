import json

BOX_SIZE = 10
GAP = 4

# Ajuste aqui a velocidade da animacao (em segundos)
DURATION = 1.0   # duracao da animacao de cada quadradinho
STAGGER = 0.05   # atraso entre quadradinhos vizinhos (efeito de onda)

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
    svg.append(f'    .box {{ opacity: 0; animation: fadeSlide {DURATION}s ease-out forwards; rx: 2; ry: 2; }}')
    svg.append('    @keyframes fadeSlide { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }')
    
    # Cores Dinâmicas: Padrão (Modo Claro - igual ao original do GitHub)
    svg.append('    .level-0 { fill: #ebedf0; } .level-1 { fill: #9be9a8; } .level-2 { fill: #40c463; } .level-3 { fill: #30a14e; } .level-4 { fill: #216e39; }')
    
    # Cores Dinâmicas: Modo Escuro (Ativado automaticamente pelas preferências do sistema/GitHub)
    svg.append('    @media (prefers-color-scheme: dark) {')
    svg.append('      .level-0 { fill: #161b22; } .level-1 { fill: #0e4429; } .level-2 { fill: #006d32; } .level-3 { fill: #26a641; } .level-4 { fill: #39d353; }')
    svg.append('    }')
    svg.append('  </style>')

    # Desenhar os quadradinhos
    for w_idx, week in enumerate(weeks):
        x = 10 + w_idx * (BOX_SIZE + GAP)
        for d_idx, day in enumerate(week):
            y = 10 + d_idx * (BOX_SIZE + GAP)
            level = min(day["level"], 4)
            delay = (w_idx + d_idx) * STAGGER
            svg.append(f'  <rect class="box level-{level}" x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" style="animation-delay: {delay:.2f}s" />')

    svg.append('</svg>')

    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("Heatmap atualizado com sucesso e cores dinâmicas!")

if __name__ == "__main__":
    render_heatmap()
