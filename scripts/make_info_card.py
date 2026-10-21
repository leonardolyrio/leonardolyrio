import sys

def make_info_card(bg_color, text_color, highlight_color, output_path):
    width = 490
    height = 500
    line_height = 22
    font_size = 14
    
    # Seus dados personalizados do GitHub
    lines = [
        f'<tspan fill="{highlight_color}">leonardolyrio</tspan>@<tspan fill="{highlight_color}">github</tspan>',
        '------------------------------------------------',
        f'<tspan fill="{highlight_color}">Uptime:</tspan>     19 years',
        f'<tspan fill="{highlight_color}">Location:</tspan>   Espírito Santo, Brazil',
        f'<tspan fill="{highlight_color}">Languages:</tspan>  HTML, CSS, JS, React',
        f'<tspan fill="{highlight_color}">OS:</tspan>          Windows, Linux',
        f'<tspan fill="{highlight_color}">Tools:</tspan>       Tailwind, Git, VSCode',
        f'<tspan fill="{highlight_color}">Focus:</tspan>       JavaScript &amp; React',
        '',
        f'<tspan fill="{highlight_color}">Contact</tspan>',
        '------------------------------------------------',
        f'<tspan fill="{highlight_color}">GitHub:</tspan>     github.com/leonardolyrio',
        f'<tspan fill="{highlight_color}">LinkedIn:</tspan>   linkedin.com/in/leonardolyrio',
        f'<tspan fill="{highlight_color}">Email:</tspan>      leonardolyrio.contato@gmail.com',
        f'<tspan fill="{highlight_color}">Discord:</tspan>    lhziin',
    ]

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('  <style>')
    svg.append(f'    .bg {{ fill: {bg_color}; }}')
    svg.append(f'    .text {{ font-family: "Courier New", Courier, monospace; font-size: {font_size}px; fill: {text_color}; white-space: pre; }}')
    # Animação de fade-in e slide vindo da esquerda, como o tutorial sugere
    svg.append('    .line { opacity: 0; animation: fadeIn 0.4s forwards; }')
    svg.append('    @keyframes fadeIn { to { opacity: 1; transform: translateX(0); } from { opacity: 0; transform: translateX(-15px); } }')
    svg.append('  </style>')
    svg.append(f'  <rect class="bg" width="100%" height="100%" />')
    
    # Renderiza cada linha com um pequeno atraso (stagger) para o efeito de digitação em cascata
    delay_step = 0.15
    y_start = 40
    for i, line in enumerate(lines):
        y = y_start + (i * line_height)
        delay = i * delay_step
        if line.strip() != "":
            svg.append(f'  <text x="20" y="{y}" class="text line" style="animation-delay: {delay}s">{line}</text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Info Card gerado: {output_path}")

if __name__ == "__main__":
    # Gera a versão Modo Escuro (Fundo escuro, texto claro, destaque azul)
    make_info_card(bg_color="#0d1117", text_color="#c9d1d9", highlight_color="#58a6ff", output_path="dark_info.svg")
    
    # Gera a versão Modo Claro (Fundo branco, texto escuro, destaque azul escuro)
    make_info_card(bg_color="#ffffff", text_color="#1f2328", highlight_color="#0969da", output_path="light_info.svg")
