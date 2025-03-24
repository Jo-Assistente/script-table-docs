import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from dotenv import load_dotenv

import os

load_dotenv()

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SHEET_ID = os.getenv('SHEET_ID')
SHEET_NAME = os.getenv('SHEET_NAME')


# Obtém os dados do Google Sheets
def get_google_sheets_data():
    """Obtém os dados da planilha do Google Sheets."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def generate_dynamic_text(profissional):
    """Gera um texto dinâmico baseado nas informações do profissional no formato desejado, evitando duplicidades."""
    texto = f"O Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()}, especialista na área de {profissional['ESPECIALIDADE'].lower()}.\n\n"
    
    texto += f"Durante as consultas, realizadas em um ambiente acolhedor e profissional, o Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()} "
    texto += "não realiza atendimento clínico. " if profissional['ATENDIMENTO_CLÍNICO'] == 'NÃO REALIZA' else "realiza atendimento clínico.\n\n"
    
    if profissional.get('PRÉ-NATAL') and profissional['PRÉ-NATAL']:
        texto += f"Para o acompanhamento pré-natal, o Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()} atende nos convênios: {profissional['PRÉ-NATAL']}.\n\n"
    
    texto += "Uma informação importante é que "
    if profissional.get('PARTO_NORMAL') and profissional['PARTO_NORMAL'] and 'REALIZA PARTO NORMAL SOMENTE PARTICULAR' not in profissional['PARTO_NORMAL']:
        texto += f"o Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()} realiza parto normal no(s) convênio(s): {profissional['PARTO_NORMAL']}, "
    else:
        texto += f"o Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()} realiza parto normal somente particular, "
    
    if profissional.get('PARTO_CESÁREA') and profissional['PARTO_CESÁREA'] and 'REALIZA PARTO CESÁREA SOMENTE PARTICULAR' not in profissional['PARTO_CESÁREA']:
        texto += f"e realiza parto cesárea no(s) convênio(s): {profissional['PARTO_CESÁREA']}.\n\n"
    else:
        texto += f"e realiza parto cesárea somente particular.\n\n"
    
    texto += f"Já nos convênios profissionais, o Dr./Dra. {profissional['NOME_DO_PROFISSIONAL'].title()} "
    convenios_pro = []
    
    if profissional.get('ATENDIMENTO_CLÍNICO_PRO') and profissional['ATENDIMENTO_CLÍNICO_PRO']:
        convenios_pro.append(f"Atendimento clínico: {profissional['ATENDIMENTO_CLÍNICO_PRO']}")
    
    if profissional.get('PRÉ-NATAL_PRO') and profissional['PRÉ-NATAL_PRO']:
        convenios_pro.append(f"Pré-natal: {profissional['PRÉ-NATAL_PRO']}")
    
    if profissional.get('PARTO_NORMAL_PRO') and profissional['PARTO_NORMAL_PRO']:
        convenios_pro.append(f"Parto normal: {profissional['PARTO_NORMAL_PRO']}")
    
    if profissional.get('PARTO_CESÁREA_PRO') and profissional['PARTO_CESÁREA_PRO']:
        convenios_pro.append(f"Parto cesárea: {profissional['PARTO_CESÁREA_PRO']}")
    
    if convenios_pro:
        texto += "realiza nos seguintes convênios profissionais:\n\n" + "\n".join(convenios_pro) + "\n\n"
    
    return texto

def generate_pdf(texto, output_file):
    """Gera um PDF formatado corretamente."""
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    text = c.beginText(50, height - 80)
    text.setFont("Helvetica", 12)

    # Divide o texto em linhas menores para caber no PDF
    wrapped_text = simpleSplit(texto, "Helvetica", 12, width - 100)
    for linha in wrapped_text:
        text.textLine(linha)

    c.drawText(text)
    c.save()

def main():
    df = get_google_sheets_data()

    for _, profissional in df.iterrows():
        output_pdf = f"contrato_{profissional['NOME_DO_PROFISSIONAL'].replace(' ', '_')}.pdf"
        texto = generate_dynamic_text(profissional)
        generate_pdf(texto, output_pdf)
        print(f"✅ PDF gerado: {output_pdf}")

if __name__ == "__main__":
    main()
