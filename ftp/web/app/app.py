from flask import Flask, render_template, request, redirect, url_for
from ftplib import FTP
import socket
from tkinter import filedialog, messagebox

app = Flask(__name__, template_folder=r'C:\Users\bruno\OneDrive\Área de Trabalho\Python\FTP Server\ftp\web\templates')

FTP_HOST = ""
FTP_PORT = 0
FTP_USER = ""
FTP_PASSWORD = ""
selected_files = []  # Lista para armazenar os nomes dos arquivos selecionados

def check_server_status():
    global FTP_HOST, FTP_PORT
    try:
        with FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASSWORD)
            return True
    except (socket.error, socket.timeout):
        return False

def file_exists_on_server(ftp, remote_filename):
    file_list = ftp.nlst()
    return remote_filename in file_list

def upload_or_delete_files(ftp, file_paths, action):
    for file_path in file_paths:
        remote_filename = file_path.split("/")[-1]
        if action == "upload":
            with open(file_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_filename}', file)
        elif action == "delete":
            if file_exists_on_server(ftp, remote_filename):
                ftp.delete(remote_filename)
            else:
                messagebox.showwarning("Arquivo não encontrado", f"O arquivo '{remote_filename}' não foi encontrado no servidor.")
    if action == "upload":
        messagebox.showinfo("Upload Concluído", "Arquivos enviados com sucesso para o servidor FTP!")
    elif action == "delete":
        messagebox.showinfo("Exclusão Concluída", "Arquivos foram excluídos do servidor FTP!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global FTP_USER, FTP_PASSWORD, FTP_HOST, FTP_PORT
    FTP_USER = request.form['username']
    FTP_PASSWORD = request.form['password']
    FTP_HOST = request.form['host']
    FTP_PORT = int(request.form['port'])
    if FTP_USER and FTP_PASSWORD and FTP_HOST and FTP_PORT:
        if check_server_status():
            return redirect(url_for('ftp_client'))
        else:
            return render_template('index.html', error="Não foi possível conectar ao servidor FTP. Verifique o endereço e a porta.")
    else:
        return render_template('index.html', error="Por favor, preencha todos os campos.")

@app.route('/ftp_client')
def ftp_client():
    return render_template('ftp_client.html')

@app.route('/upload', methods=['POST'])
def upload():
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASSWORD)
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        upload_or_delete_files(ftp, file_paths, "upload")
    return redirect(url_for('ftp_client'))

@app.route('/delete', methods=['POST'])
def delete():
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASSWORD)
    files_to_action = selected_files.copy()
    if files_to_action:
        upload_or_delete_files(ftp, files_to_action, "delete")
    return redirect(url_for('ftp_client'))

def list_files():
    global FTP_HOST, FTP_PORT
    with FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASSWORD)
        file_list = ftp.nlst()
        return file_list

@app.route('/select_all', methods=['POST'])
def select_all():
    global selected_files
    selected_files = list_files()
    return redirect(url_for('ftp_client'))

@app.route('/unselect_all', methods=['POST'])
def unselect_all():
    global selected_files
    selected_files = []
    return redirect(url_for('ftp_client'))

if __name__ == "__main__":
    app.run(debug=True)
