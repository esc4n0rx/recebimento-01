import win32com.client
import os
import datetime
import pandas as pd
import pythoncom  # Adicionado

def importar_agendamentos():
    pythoncom.CoInitialize()  # Inicializa a biblioteca COM
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)  # 6 é a pasta de entrada
        messages = inbox.Items

        # Obter a data atual no formato desejado
        data_atual = datetime.datetime.now().strftime("%d.%m")
        assunto_procurado = f"Agendamento {data_atual} - CDRJ"

        mensagem_encontrada = None

        for message in messages:
            if message.Subject == assunto_procurado:
                mensagem_encontrada = message
                break

        if not mensagem_encontrada:
            return False

        anexos = mensagem_encontrada.Attachments
        for anexo in anexos:
            caminho = os.path.join(os.getcwd(), anexo.FileName)
            anexo.SaveAsFile(caminho)

            # Ler o anexo e extrair as colunas necessárias
            df = pd.read_excel(caminho, usecols="A,G,I")
            df.columns = ['Departamento', 'Fornecedor', 'Pedido']
            df.to_csv('agendamentos.csv', index=False)
            os.remove(caminho)  # Remover o anexo após processar

        return True
    finally:
        pythoncom.CoUninitialize()  # Desinicializa a biblioteca COM
