import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

def prep_photo(input_path, output_path="source-prepped.png"):
    # 1. Carrega a imagem e remove o fundo
    input_image = Image.open(input_path)
    output_rgba = remove(input_image)
    
    # Converter para array do OpenCV (RGBA)
    rgba_np = np.array(output_rgba)
    
    # Separar os canais de cor e a máscara Alfa (transparência)
    rgb = rgba_np[:, :, :3]
    alpha = rgba_np[:, :, 3]
    
    # Convert para Escala de Cinza
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    
    # 2. Melhora o contraste local com CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    
    # 3. Composição com fundo branco puro (onde era transparente vira branco)
    white_bg = np.full_like(enhanced_gray, 255)
    
    # Aplica a máscara alpha (normalizada entre 0 e 1)
    alpha_norm = alpha / 255.0
    final_img = (enhanced_gray * alpha_norm + white_bg * (1.0 - alpha_norm)).astype(np.uint8)
    
    # Salvar o resultado
    cv2.imwrite(output_path, final_img)
    print(f"Imagem processada com sucesso: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/prep_photo.py <caminho-da-foto.jpg>")
        sys.exit(1)
    
    prep_photo(sys.argv[1])
