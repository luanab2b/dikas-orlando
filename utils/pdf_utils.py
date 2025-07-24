import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def gerar_pdf_base64(conteudo_texto: str, nome_arquivo: str = "roteiro.pdf") -> str:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    linhas = conteudo_texto.split('\n')
    y = altura - 50
    for linha in linhas:
        pdf.drawString(50, y, linha)
        y -= 15  # Espaço entre linhas
        if y < 50:
            pdf.showPage()
            y = altura - 50

    pdf.save()
    buffer.seek(0)
    pdf_bytes = buffer.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return pdf_base64