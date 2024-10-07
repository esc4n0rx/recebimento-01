from PIL import Image, ImageDraw, ImageFont
import os

def criar_imagem_pendencias(pendencias):
    # Definir fonte
    font_path = 'arial.ttf'  # Certifique-se de que esta fonte existe no sistema
    font_size = 14
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Definir títulos das colunas
    headers = ['Departamento', 'Fornecedor', 'Pedido', 'Hora', 'Status', 'Motivo']
    # Definir largura das colunas
    column_widths = [120, 150, 80, 80, 100, 200]

    # Calcular largura e altura da imagem
    image_width = sum(column_widths) + 40  # 20 de margem em cada lado
    row_height = font_size + 10
    image_height = row_height * (len(pendencias) + 2) + 20  # +2 para o cabeçalho e margem

    imagem = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(imagem)

    y_position = 20
    x_start = 20

    # Desenhar o cabeçalho
    x_position = x_start
    for i, header in enumerate(headers):
        draw.text((x_position, y_position), header, fill='black', font=font)
        x_position += column_widths[i]

    y_position += row_height

    # Desenhar linhas das pendências
    for pendencia in pendencias:
        x_position = x_start
        campos = [pendencia[1], pendencia[2], pendencia[3], pendencia[4], pendencia[5], pendencia[6]]
        for i, campo in enumerate(campos):
            draw.text((x_position, y_position), str(campo), fill='black', font=font)
            x_position += column_widths[i]
        y_position += row_height

    # Desenhar linhas horizontais
    x_end = image_width - 20
    for i in range(len(pendencias) + 2):
        y = 20 + i * row_height
        draw.line([(x_start, y), (x_end, y)], fill='grey')

    # Desenhar linhas verticais
    x_position = x_start
    for width in column_widths:
        draw.line([(x_position, 20), (x_position, y_position - row_height)], fill='grey')
        x_position += width
    draw.line([(x_position, 20), (x_position, y_position - row_height)], fill='grey')

    # Salvar a imagem na área de trabalho
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    imagem.save(os.path.join(desktop_path, 'pendencias.png'))
