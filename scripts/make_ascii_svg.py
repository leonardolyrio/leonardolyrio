import cv2
import numpy as np

RAMP = " .`:-=+*cs#%@"  # Do claro (espaço) ao escuro (@)

def image_to_ascii_grid(image_path, width=100):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Imagem {image_path} não encontrada. Execute o prep_photo.py primeiro.")
    
    # Calcular altura mantendo a proporção aproximada dos caracteres (caracteres são mais altos do que largos, ~1:2)
    h, w = img.shape
    aspect_ratio = h / w
    height = int(width * aspect_ratio * 0.53)
    
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    
    # Mapear pixels (0-255) para os caracteres da RAMP
    num_chars = len(RAMP)
    lines = []
    for row in resized:
        line = ""
        for pixel in row:
            # 0 (preto) -> escuro / 255 (branco) -> claro
            # Invertemos o índice para que 255 mapeie para o início da RAMP (espaços)
            char_idx = int((255 - pixel) / 256.0 * num_chars)
            char_idx = min(char_idx, num_chars - 1)
            line += RAMP[char_idx]
        lines.append(line)
    
    return lines, width, height

def generate_svg(lines, width, height, output_path="avi-ascii.svg"):
    font_size = 12
    char_width = 7.2
    line_height = 12
    
    svg_w = int(width * char_width)
    svg_h = int(height * line_height)
    
    row_count = len(lines)
    duration = 3.0  # Duração total da animação em segundos
    row_delay = duration / max(row_count, 1)
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg.append('  <style>')
    svg.append('    .bg { fill: #0d1117; }')
    svg.append('    .ascii { font-family: "Courier New", Courier, monospace; font-size: 12px; fill: #c9d1d9; white-space: pre; }')
    svg.append('  </style>')
    svg.append(f'  <rect class="bg" width="100%" height="100%" />')
    
    # Criar clipPaths para o efeito de digitação linha por linha
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
    
    # Renderizar cada linha de texto
    for i, line in enumerate(lines):
        y_pos = (i + 1) * line_height - 2
        # Escapar caracteres HTML especiais se necessário
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg.append(f'  <text x="0" y="{y_pos}" class="ascii" clip-path="url(#clip-{i})">{escaped_line}</text>')
        
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    
    print(f"SVG gerado com sucesso: {output_path}")

if __name__ == "__main__":
    lines, w, h = image_to_ascii_grid("source-prepped.png", width=100)
    generate_svg(lines, w, h)
