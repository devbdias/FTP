from ftplib import FTP
import tkinter as tk
import socket
from tkinter import filedialog, messagebox
import os

FTP_HOST = ""
FTP_PORT = 0
FTP_USER = ""
FTP_PASSWORD = ""

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

def get_unique_filename(ftp, original_filename):
    file_name, file_extension = os.path.splitext(original_filename)
    new_filename = original_filename
    counter = 1
    while file_exists_on_server(ftp, new_filename):
        new_filename = f"{file_name} ({counter}){file_extension}"
        counter += 1
    return new_filename

def upload_or_delete_files(file_paths, action):
    with FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASSWORD)
        for file_path in file_paths:
            remote_filename = file_path.split("/")[-1]
            if action == "upload":
                if file_exists_on_server(ftp, remote_filename):
                    remote_filename = get_unique_filename(ftp, remote_filename)
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

def confirm_delete_files(file_paths):
    result = messagebox.askokcancel("Confirmação de Exclusão", "Tem certeza de que deseja excluir os arquivos selecionados?")
    if result:
        upload_or_delete_files(file_paths, "delete")

def choose_local_files_for_action(action):
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        upload_or_delete_files(file_paths, action)

def choose_remote_files_for_action(action):
    remote_file_names = list_files_listbox.curselection()
    if remote_file_names:
        files_to_action = [list_files_listbox.get(index) for index in remote_file_names]
        if action == "upload":
            upload_or_delete_files(files_to_action, "upload")
        elif action == "delete":
            confirm_delete_files(files_to_action)

def list_files():
    global FTP_HOST, FTP_PORT
    with FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASSWORD)
        file_list = ftp.nlst()
        list_files_listbox.delete(0, tk.END)  # Limpar a lista para atualização
        if file_list:
            for file_name in file_list:
                list_files_listbox.insert(tk.END, file_name)
        else:
            list_files_listbox.insert(tk.END, "Não há arquivos no servidor.")

    # Agendar a próxima atualização após 10 segundos
    list_files_listbox.after(10000, list_files)

def login():
    global FTP_USER, FTP_PASSWORD, FTP_HOST, FTP_PORT
    FTP_USER = username_entry.get()
    FTP_PASSWORD = password_entry.get()
    FTP_HOST = host_entry.get()
    FTP_PORT = int(port_entry.get())
    if FTP_USER and FTP_PASSWORD and FTP_HOST and FTP_PORT:
        if check_server_status():
            try:
                login_window.destroy()  # Fechar a janela de login após o login bem-sucedido
                create_gui()
            except Exception as e:
                messagebox.showerror("Erro de Login", "Falha ao fazer login. Verifique suas credenciais.")
        else:
            messagebox.showerror("Erro de Conexão", "Não foi possível conectar ao servidor FTP. Verifique o endereço e a porta.")
    else:
        messagebox.showerror("Erro de Login", "Por favor, preencha todos os campos.")

def create_login_gui():
    global login_window, username_entry, password_entry, host_entry, port_entry, status_label
    login_window = tk.Tk()
    login_window.title('Login - Cliente FTP')
    login_window.geometry("500x200")

    frame = tk.Frame(login_window)
    frame.pack(pady=20)

    label_username = tk.Label(frame, text="Usuário:")
    label_username.grid(row=0, column=0, pady=5)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, pady=5)

    label_password = tk.Label(frame, text="Senha:")
    label_password.grid(row=0, column=2, pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=0, column=3, pady=5)

    label_host = tk.Label(frame, text="Host:")
    label_host.grid(row=1, column=0, pady=5)
    host_entry = tk.Entry(frame)
    host_entry.grid(row=1, column=1, pady=5)

    label_port = tk.Label(frame, text="Porta:")
    label_port.grid(row=1, column=2, pady=5)
    port_entry = tk.Entry(frame)
    port_entry.grid(row=1, column=3, pady=5)

    status_label = tk.Label(login_window, text="", fg="red")
    status_label.pack()

    button_login = tk.Button(frame, text="Login", command=login)
    button_login.grid(row=2, columnspan=4, pady=10)

    login_window.mainloop()

def create_gui():
    global list_files_listbox
    window = tk.Tk()
    window.title('Cliente FTP')
    window.geometry("700x500")

    frame_buttons = tk.Frame(window)
    frame_buttons.pack(pady=10)

    button_upload = tk.Button(frame_buttons, text="Enviar", command=lambda: choose_local_files_for_action("upload"), width=15)
    button_upload.pack(side=tk.LEFT, padx=5)

    button_download = tk.Button(frame_buttons, text="Baixar", command=lambda: choose_remote_files_for_action("download"), width=20)
    button_download.pack(side=tk.LEFT, padx=5)

    button_delete = tk.Button(frame_buttons, text="Excluir", command=lambda: choose_remote_files_for_action("delete"), width=20)
    button_delete.pack(side=tk.LEFT, padx=5)

    button_refresh = tk.Button(frame_buttons, text="Atualizar", command=list_files, width=15)
    button_refresh.pack(side=tk.LEFT, padx=5)

    list_files_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE)
    list_files_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    list_files()

    frame_select_buttons = tk.Frame(window)  # Novo frame para os botões "Selecionar Tudo" e "Desmarcar Tudo"
    frame_select_buttons.pack(pady=5)

    # Botão "Selecionar Tudo"
    button_select_all = tk.Button(frame_select_buttons, text="Selecionar Tudo", command=select_all_files)
    button_select_all.pack(side=tk.LEFT, padx=5)

    # Botão "Desmarcar Tudo"
    button_unselect_all = tk.Button(frame_select_buttons, text="Desmarcar Tudo", command=unselect_all_files)
    button_unselect_all.pack(side=tk.LEFT, padx=5)

    window.mainloop()

def select_all_files():
    global list_files_listbox
    for i in range(list_files_listbox.size()):
        list_files_listbox.select_set(i)

def unselect_all_files():
    global list_files_listbox
    list_files_listbox.selection_clear(0, tk.END)

if __name__ == "__main__":
    create_login_gui()
