import sys

def txt_to_svg(txt_path="ascii_art.txt"):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f.readlines()]

    if not lines:
        print("Erro: O arquivo de texto está vazio!")
        return

    max_width = max(len(line) for line in lines)
    height = len(lines)

    char_width = 7.2
    line_height = 12

    svg_w = int(max_width * char_width)
    svg_h = int(height * line_height)

    row_count = len(lines)
    duration = 3.0
    row_delay = duration / max(row_count, 1)

    def generate_single_svg(bg_color, text_color, output_path):
        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
        svg.append('  <style>')
        svg.append(f'    .bg {{ fill: {bg_color}; }}')
        svg.append(f'    .ascii {{ font-family: "Courier New", Courier, monospace; font-size: 12px; fill: {text_color}; white-space: pre; }}')
        svg.append('  </style>')
        svg.append(f'  <rect class="bg" width="100%" height="100%" />')
        
        svg.append('  <defs>')
        for i in range(row_count):
            y_pos = i * line_height
            begin_time = i * row_delay
            svg.append(f'    <clipPath id="clip-{i}">')
            svg.append(f'      <rect x="0" y="{y_pos}" width="0" height="{line_height}">')
            svg.append(f'        <animate attributeName="width" from="0" to="{svg_w}" dur="{row_delay:.2f}s" begin="{begin_time:.2f}s" fill="freeze" />')
            svg.append(f'      </rect>')
            svg.append(f'    </clipPath>')
        svg.append('  </defs>')

        for i, line in enumerate(lines):
            y_pos = (i + 1) * line_height - 2
            escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg.append(f'  <text x="0" y="{y_pos}" class="ascii" clip-path="url(#clip-{i})">{escaped_line}</text>')

        svg.append('</svg>')

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        print(f"SVG gerado: {output_path}")

    # 1. Versão Modo Escuro (Dark Mode)
    generate_single_svg(bg_color="#0d1117", text_color="#c9d1d9", output_path="dark_mode.svg")

    # 2. Versão Modo Claro (Light Mode)
    generate_single_svg(bg_color="#ffffff", text_color="#1f2328", output_path="light_mode.svg")

if __name__ == "__main__":
    txt_path = sys.argv[1] if len(sys.argv) > 1 else "ascii_art.txt"
    txt_to_svg(txt_path)
