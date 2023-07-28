from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

# Configurações do servidor FTP
FTP_HOST = "127.0.0.1"
FTP_PORT = 2121
FTP_USER = "1"
FTP_PASSWORD = "1"
FTP_DIRECTORY = r"C:\Users\bruno\OneDrive\Área de Trabalho\Python\Python FIAP\socket\ftp\data"  # Diretório que será usado como servidor FTP

def run_ftp_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    server = servers.FTPServer((FTP_HOST, FTP_PORT), handler)
    server.serve_forever()

if __name__ == "__main__":
    print("Iniciando servidor FTP...")
    run_ftp_server()