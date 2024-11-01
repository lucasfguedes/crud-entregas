import os
import time
import subprocess
import win32print
import win32api
import datetime
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, ttk
import sqlite3



# Dicionário com os bairros e valores vazios
enderecos_bairros = {
    "Aeroporto": None,
    "Ana Jacinta": None,
    "Bosque": None,
    "Brasil Novo": None,
    "Cecap": None,
    "Centro": None,
    "Jardim América": None,
    "Jardim das Oliveiras": None,
    "Jardim Itapura I e II": None,
    "Jardim Maracanã": None,
    "Jardim Mediterrâneo": None,
    "Jardim Monte Alto": None,
    "Jardim Novo Bongiovani": None,
    "Jardim Novo Eldorado": None,
    "Jardim Novo Horizonte": None,
    "Jardim Novo Prudentino": None,
    "Jardim Novo Wenzel": None,
    "Jardim Panorama": None,
    "Jardim Paulista": None,
    "Jardim Planalto": None,
    "Jardim Prudentino": None,
    "Jardim Regina": None,
    "Jardim Rosas do Sul": None,
    "Jardim Santa Eliza": None,
    "Jardim Santa Mônica": None,
    "Jardim São Bento": None,
    "Jardim São Domingos": None,
    "Jardim São Gabriel": None,
    "Jardim São Lucas": None,
    "Jardim São Pedro": None,
    "Jardim São Sebastião": None,
    "Jardim Sumaré": None,
    "Jardim Vale do Sol": None,
    "Jardim Vale Verde": None,
    "Jardim Vila Real": None,
    "Jardim das Paineiras": None,
    "Jardim das Primaveras": None,
    "Jardim das Rosas": None
}

class appEntregas:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x500") 
        self.root.title("Sistema de Entregas")
        self.root = root
        self.conn = None  # Inicializa como None
        self.main_frame = tk.Frame(self.root, bg='indigo')
        self.main_frame.pack(fill='both', expand=True)
        self.conn = self.conectar_banco()  # Certifique-se de que isso não retorna None
        if self.conn is None:
            print("Falha na conexão com o banco de dados.")
            self.root.destroy()  # Fecha a aplicação se não houver conexão
            return


        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='indigo')
        self.main_frame.pack(side=tk.LEFT, fill='both', expand=True)

        # Inicializa a lista de entregas realizadas
        self.entregas_realizadas = []

        # Configura a interface
        self.configurar_interface()

        self.criar_conexao()  # Chama a função para criar a conexão
        self.criar_tabela()  # Agora a conexão deve estar disponível
        
    def criar_conexao(self):
        try:
            self.conn = sqlite3.connect('bairros.db')  # substitua pelo seu banco de dados
            self.cursor = self.conn.cursor()
            print("Conexão criada com sucesso.")
        except Exception as e:
            print(f"Erro ao criar conexão: {e}")

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()
            print("Conexão fechada.")

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='indigo')
        self.main_frame.pack(fill='both', expand=True)

        # Inicializa a lista de entregas realizadas
        self.entregas_realizadas = []

        # Configura a interface
        self.configurar_interface()

    def conectar_banco(self):
        try:
            db_file = 'bairros.db'
            db_exists = os.path.exists(db_file)
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            if not db_exists:
                cursor.execute('''
                    CREATE TABLE bairros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        valor REAL
                    )
                ''')
                print("Banco de dados e tabela 'bairros' criados.")
                for bairro in enderecos_bairros.keys():
                    cursor.execute('''
                        INSERT INTO bairros (nome, valor) VALUES (?, ?)
                    ''', (bairro, 0))  # Valor inicial como 0

            conn.commit()
            return conn
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None  # Retorna None em caso de erro



    def criar_tabela(self):
        if self.conn is not None:
            cursor = self.conn.cursor()
            # Criação da tabela
            cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
                id INTEGER PRIMARY KEY,
                endereco TEXT,
                cliente TEXT
                )''')
            self.conn.commit()
            print("Tabela criada com sucesso.")
        else:
            print("A conexão com o banco de dados não foi estabelecida.")

    def inicializar_bairros(self):
        enderecos_bairros = {
            "Aeroporto": None,
            "Ana Jacinta": None,
            "Bosque": None,
            # Continue com os outros bairros...
        }

        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM bairros")
        count = cursor.fetchone()[0]

        if count == 0:
            for bairro, valor in enderecos_bairros.items():
                cursor.execute("INSERT INTO bairros (nome, valor) VALUES (?, ?)", (bairro, valor))
            self.conn.commit()
            print("Dados dos bairros inicializados no banco de dados.")

    def configurar_interface(self):
        # Título
        self.title_label = tk.Label(self.main_frame, text="Sistema de Entregas", font=("Arial", 14), bg='indigo', fg='white')
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Campo de Nome do Cliente
        self.label_nome_cliente = tk.Label(self.main_frame, text="Nome do Cliente:", bg='indigo', fg='white')
        self.label_nome_cliente.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.entry_nome_cliente = tk.Entry(self.main_frame, width=40)
        self.entry_nome_cliente.grid(row=1, column=1)

        # Campo de Endereço
        self.label_endereco = tk.Label(self.main_frame, text="Endereço:", bg='indigo', fg='white')
        self.label_endereco.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.entry_endereco = tk.Entry(self.main_frame, width=40)
        self.entry_endereco.grid(row=2, column=1)

        # Campo de Bairro
        self.label_bairro = tk.Label(self.main_frame, text="Bairro:", bg='indigo', fg='white')
        self.label_bairro.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        self.combobox_bairro = ttk.Combobox(self.main_frame, values=self.buscar_bairros(), width=37)
        self.combobox_bairro.grid(row=3, column=1)
        self.combobox_bairro.bind("<<ComboboxSelected>>", self.atualizar_valor)  # Atualiza o valor ao selecionar um bairro

        # Campo de Valor de Entrega
        self.label_valor = tk.Label(self.main_frame, text="Valor de Entrega: R$", bg='indigo', fg='white')
        self.label_valor.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        self.entry_valor = tk.Entry(self.main_frame, width=40, state='readonly')
        self.entry_valor.grid(row=4, column=1)

        # Campos de pagamento
        self.label_pagamento = tk.Label(self.main_frame, text="Forma de Pagamento:", bg='indigo', fg='white')
        self.label_pagamento.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.var_pagamento = StringVar(value=" ")
        self.combo_pagamento = tk.OptionMenu(self.main_frame, self.var_pagamento, "PIX", "Débito", "Crédito", "Dinheiro", command=self.atualizar_troco_display)
        self.combo_pagamento.grid(row=5, column=1, sticky="ew", padx=20, pady=10)

        # Caixa de troco
        self.label_valor_recebido = tk.Label(self.main_frame, text="Valor Recebido: R$", bg='indigo', fg='white')
        self.label_valor_recebido.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        self.entry_valor_recebido = tk.Entry(self.main_frame, width=40)
        self.entry_valor_recebido.grid(row=6, column=1)

        self.label_troco = tk.Label(self.main_frame, text="Troco:", bg='indigo', fg='white')
        self.label_troco.grid(row=7, column=0, sticky="w", padx=10, pady=5)

        self.entry_troco = tk.Entry(self.main_frame, width=40, state='readonly')
        self.entry_troco.grid(row=7, column=1)

        # Inicialmente escondidos
        self.label_valor_recebido.grid_remove()
        self.entry_valor_recebido.grid_remove()
        self.label_troco.grid_remove()
        self.entry_troco.grid_remove()

        # Botões
        self.btn_realizar_entrega = tk.Button(self.main_frame, text="Realizar Entrega", command=self.realizar_entrega)
        self.btn_realizar_entrega.grid(row=8, column=0, padx=5, pady=10, sticky='ew')

        self.btn_exibir_entregas = tk.Button(self.main_frame, text="Exibir Entregas", command=self.exibir_entregas)
        self.btn_exibir_entregas.grid(row=8, column=1, padx=5, pady=10, sticky='ew')

        self.btn_repetir_entrega = tk.Button(self.main_frame, text="Repetir Última Entrega", command=self.repetir_entrega)
        self.btn_repetir_entrega.grid(row=9, column=0, columnspan=2, padx=5, pady=10, sticky='ew')

        # Ajuste de tamanho da Treeview e posicionamento à direita
        self.tree = ttk.Treeview(self.main_frame, columns=("Nome", "Valor"), show='headings', height=20)  # Aumentar o height para mudar a altura da tabela
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Valor", text="Valor")
        self.tree.column("Nome", width=200)  # Ajuste a largura das colunas
        self.tree.column("Valor", width=100)  # Ajuste a largura das colunas
        self.tree.grid(row=0, column=2, rowspan=10, padx=10, pady=10, sticky='nsew')  # Posicionar à direita e aumentar o tamanho

        self.atualizar_treeview()  # Atualiza a Treeview com dados do banco

        # Configuração de colunas
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=3)



    def buscar_bairros(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome FROM bairros")
        bairros = [row[0] for row in cursor.fetchall()]
        return bairros

    def atualizar_valor_bairro(self, bairro, novo_valor):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE bairros SET valor = ? WHERE nome = ?
        ''', (novo_valor, bairro))
        self.conn.commit()

    def fechar_conexao(self):
        self.conn.close()  # Fecha a conexão quando não for mais necessária


    def atualizar_troco_display(self, *args):
        mostrar = (self.var_pagamento.get() == "Dinheiro")
        widgets = [self.label_valor_recebido, self.entry_valor_recebido, self.label_troco, self.entry_troco]
        for widget in widgets:
            widget.grid() if mostrar else widget.grid_remove()

    def atualizar_valor(self, event):
        bairro = self.combobox_bairro.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT valor FROM bairros WHERE nome = ?", (bairro,))
        valor = cursor.fetchone()
        if valor:
            self.entry_valor.config(state='normal')
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.insert(0, valor[0])  # Insere o valor no campo
            self.entry_valor.config(state='readonly')  # Retorna para readonly


    def atualizar_troco(self, event):
        if self.var_pagamento.get() == "Dinheiro":
            try:
                valor_produto = float(self.entry_valor.get())  # Valor da entrega
                valor_recebido = float(self.entry_valor_recebido.get())
                troco = valor_recebido - valor_produto
                self.entry_troco.config(state='normal')
                self.entry_troco.delete(0, tk.END)
                self.entry_troco.insert(0, f"{troco:.2f}")
                self.entry_troco.config(state='readonly')
            except ValueError:
                self.entry_troco.config(state='normal')
                self.entry_troco.delete(0, tk.END)
                self.entry_troco.insert(0, "Erro")
                self.entry_troco.config(state='readonly')


    def realizar_entrega(self):
        try:
            nome_cliente = self.entry_nome_cliente.get()
            endereco = self.entry_endereco.get()
            bairro = self.combobox_bairro.get()
            valor = float(self.entry_valor.get())
            valor_recebido = float(self.entry_valor_recebido.get())
            
            # Salvar entrega no banco de dados
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO entregas (nome_cliente, endereco, bairro, valor, valor_recebido)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome_cliente, endereco, bairro, valor, valor_recebido))
            self.conn.commit()
            
            # Limpa os campos após a entrega
            self.entry_nome_cliente.delete(0, tk.END)
            self.entry_endereco.delete(0, tk.END)
            self.combobox_bairro.set('')
            self.entry_valor.configure(state='normal')
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.configure(state='readonly')
            self.entry_valor_recebido.delete(0, tk.END)
            self.entry_troco.configure(state='normal')
            self.entry_troco.delete(0, tk.END)
            self.entry_troco.configure(state='readonly')
            
            messagebox.showinfo("Sucesso", "Entrega realizada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")



    def limpar_campos(self):
        self.entry_nome_cliente.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.combobox_bairro.set('')  # Reseta o combobox
        self.entry_valor.delete(0, tk.END)
        self.entry_valor_recebido.delete(0, tk.END)
        self.entry_troco.delete(0, tk.END)

    def exibir_entregas(self):
        if not self.entregas_realizadas:
            messagebox.showinfo("Entregas", "Nenhuma entrega realizada.")
            return
        entregas_str = "\n".join(self.entregas_realizadas)
        messagebox.showinfo("Entregas Realizadas", entregas_str)

    def repetir_entrega(self):
        """Repete a última entrega realizada."""
        if not self.entregas_realizadas:
            messagebox.showerror("Erro", "Nenhuma entrega foi realizada anteriormente.")
            return

        ultima_entrega = self.entregas_realizadas[-1]
        # Aqui você pode implementar a lógica de repetir a entrega, preenche os campos conforme necessário.
        messagebox.showinfo("Repetir Entrega", f"Última entrega: {ultima_entrega}")

    

    def criar_tabela_bairros(self):
        self.tree = ttk.Treeview(self.main_frame, columns=('ID', 'Nome', 'Valor'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Valor', text='Valor')
        self.tree.column('ID', width=50)
        self.tree.column('Nome', width=50)
        self.tree.column('Valor', width=50)
        
        self.tree.pack(fill='both', expand=True, side='right')  # Alinha à direita

        # Preencher a tabela com dados do banco de dados
        self.atualizar_tabela_bairros()



    def atualizar_treeview(self):
        # Limpa a Treeview antes de adicionar novos dados
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.conn.cursor()
        cursor.execute("SELECT nome, valor FROM bairros")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)



    def adicionar_bairro(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Adicionar Bairro")
        
        tk.Label(new_window, text="Nome do Bairro:").pack()
        entry_nome = tk.Entry(new_window)
        entry_nome.pack()

        tk.Label(new_window, text="Valor:").pack()
        entry_valor = tk.Entry(new_window)
        entry_valor.pack()

    def salvar_bairro():
        nome_bairro = entry_nome.get()
        valor = float(entry_valor.get())
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO bairros (nome, valor) VALUES (?, ?)", (nome_bairro, valor))
        self.conn.commit()
        self.atualizar_treeview()
        new_window.destroy()
        messagebox.showinfo("Sucesso", "Bairro adicionado com sucesso!")

        tk.Button(new_window, text="Salvar", command=salvar_bairro).pack()



if __name__ == "__main__":
    root = tk.Tk()
    app = appEntregas(root)
    root.mainloop()