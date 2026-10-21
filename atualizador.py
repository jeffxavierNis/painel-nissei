import os
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pdf2image import convert_from_path

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

EMAIL_CORPORATIVO = 'jefferson.souza@nissei.com.br'  # Coloque o seu e-mail
ID_DRIVE_COMPARTILHADO = '0AP4rIXpE1wnkUk9PVA' # ID da raiz do Drive Compartilhado

credenciais_json = os.environ.get('GCP_CREDENTIALS')
info_credenciais = json.loads(credenciais_json)

# Autentica-se como se fosse o seu e-mail
creds = service_account.Credentials.from_service_account_info(
    info_credenciais, scopes=SCOPES
).with_subject(EMAIL_CORPORATIVO)

service = build('drive', 'v3', credentials=creds)

print(f"A aceder ao Drive Compartilhado como {EMAIL_CORPORATIVO}...")

# Procura o PDF mais recente diretamente na raiz do Drive Compartilhado
query = f"'{ID_DRIVE_COMPARTILHADO}' in parents and mimeType='application/pdf' and trashed=false"
resultados = service.files().list(
    q=query, 
    orderBy="createdTime desc", 
    fields="files(id, name)",
    corpora="drive",
    driveId=ID_DRIVE_COMPARTILHADO,
    includeItemsFromAllDrives=True,
    supportsAllDrives=True
).execute()

arquivos = resultados.get('files', [])

if not arquivos:
    print("Nenhum ficheiro PDF encontrado na raiz do Drive Compartilhado!")
    exit(1)

pdf_recente = arquivos[0]
id_arquivo = pdf_recente['id']
print(f"Ficheiro encontrado: {pdf_recente['name']}. A iniciar download...")

# Faz o download do ficheiro (com suporte a Drive Compartilhado ativado)
request = service.files().get_media(fileId=id_arquivo)
# É necessário adicionar supportsAllDrives também no download
request.uri = request.uri + "&supportsAllDrives=true"

fh = io.FileIO('relatorio_diario.pdf', 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()

print("A converter o PDF para as imagens da TV...")
imagens = convert_from_path('relatorio_diario.pdf')

for i, imagem in enumerate(imagens):
    if i < 4:
        nome_arquivo = f'slide_0{i+1}.jpg'
        imagem.save(nome_arquivo, 'JPEG')
        print(f'{nome_arquivo} gerado com sucesso.')
