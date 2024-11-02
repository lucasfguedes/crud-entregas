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



class appEntregas:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x550")
        self.root.title("Sistema de Entregas")
        self.conn = self.conectar_banco()
        if self.conn is None:
            print("Falha na conexão com o banco de dados.")
            self.root.destroy()
            return
        

        self.root = root
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='indigo')
        self.main_frame.pack(side=tk.LEFT, fill='both', expand=True)

        # Inicializa a lista de entregas realizadas
        self.entregas_realizadas = []

        # Configura a interface
        self.configurar_interface()

        # Atualiza combobox e treeview
        self.atualizar_combobox_e_treeview()

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()
            print("Conexão fechada.")

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
                # Não inicializa com valores fixos

            conn.commit()
            return conn
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None  # Retorna None em caso de erro

    def atualizar_combobox_e_treeview(self):
        # Atualiza o Combobox com dados do banco
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome FROM bairros")
        bairros = [row[0] for row in cursor.fetchall()]
        self.combobox_bairro['values'] = bairros

        # Atualiza o Treeview com dados do banco
        self.tree.delete(*self.tree.get_children())
        cursor.execute("SELECT nome, valor FROM bairros")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        cursor.close()

    def atualizar_treeview(self):
        self.atualizar_combobox_e_treeview()

    def buscar_bairros(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome FROM bairros")
        bairros = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return bairros

    def atualizar_troco_display(self, *args):
        if self.var_pagamento.get() == "Dinheiro":
            # Mostra os campos de valor recebido e troco se o pagamento for em dinheiro
            self.label_valor_recebido.grid()
            self.entry_valor_recebido.grid()
            self.label_troco.grid()
            self.entry_troco.grid()
        else:
            # Esconde os campos de valor recebido e troco para outras opções de pagamento
            self.label_valor_recebido.grid_remove()
            self.entry_valor_recebido.grid_remove()
            self.label_troco.grid_remove()
            self.entry_troco.grid_remove()

    def atualizar_valor(self, event):
        bairro = self.combobox_bairro.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT valor FROM bairros WHERE nome = ?", (bairro,))
        valor = cursor.fetchone()
        if valor:
            # Permite ao usuário inserir seu próprio valor
            self.entry_valor.config(state='normal')  # Permite edição
            self.entry_valor.delete(0, tk.END)
            # Se você quiser mostrar a taxa de entrega, você pode fazer isso,
            # mas não precisa sobrescrever o valor que o usuário digitar.
            #self.entry_valor.insert(0, valor[0])  # Pode ser removido se você não quiser mostrar o valor automaticamente
            self.entry_valor.config(state='normal')  # Permite edição
        cursor.close()


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
            nome_cliente = self.entry_nome_cliente.get().strip()
            endereco = self.entry_endereco.get().strip()
            bairro = self.combobox_bairro.get().strip()
            
            # Mensagens de depuração
            print(f"Nome do Cliente: '{nome_cliente}'")
            print(f"Endereço: '{endereco}'")
            print(f"Bairro: '{bairro}'")

            # Validação dos campos obrigatórios
            if not nome_cliente:
                raise ValueError("O campo 'Nome do Cliente' não pode estar vazio.")
            if not endereco:
                raise ValueError("O campo 'Endereço' não pode estar vazio.")
            if not bairro:
                raise ValueError("O campo 'Bairro' não pode estar vazio.")

            valor_produto_str = self.entry_valor.get().strip()
            print(f"Valor do Produto: '{valor_produto_str}'")
            if not valor_produto_str:
                raise ValueError("O valor do produto não pode estar vazio.")
            
            valor_produto = float(valor_produto_str)
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT valor FROM bairros WHERE nome = ?", (bairro,))
            taxa_entrega = cursor.fetchone()
            taxa_entrega = taxa_entrega[0] if taxa_entrega else 0
            
            valor_total = valor_produto + taxa_entrega

            valor_recebido_str = self.entry_valor_recebido.get().strip() if self.var_pagamento.get() == "Dinheiro" else "0"
            print(f"Valor Recebido: '{valor_recebido_str}'")

            if self.var_pagamento.get() == "Dinheiro":
                if not valor_recebido_str:
                    raise ValueError("O valor recebido não pode estar vazio quando a opção de pagamento é 'Dinheiro'.")
                valor_recebido = float(valor_recebido_str)
            else:
                valor_recebido = 0  # Ou outro valor padrão que você deseje

            # Salvar entrega em arquivo TXT
            self.salvar_entrega_em_arquivo(nome_cliente, endereco, bairro, valor_total, valor_recebido)

            # Imprimir recibo
            self.imprimir_recibo(nome_cliente, endereco, bairro, valor_total, valor_recebido)

            self.limpar_campos()
            messagebox.showinfo("Sucesso", "Entrega realizada com sucesso!")

        except ValueError as ve:
            messagebox.showerror("Erro de Validação", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")




    def salvar_entrega_em_arquivo(self, nome_cliente, endereco, bairro, valor_total, valor_recebido):
        data_hora_atual = datetime.now()
        nome_arquivo = data_hora_atual.strftime("%Y-%m-%d") + ".txt"
        
        with open(nome_arquivo, "a") as file:
            file.write(f"Data: {data_hora_atual}\n")
            file.write(f"Nome do Cliente: {nome_cliente}\n")
            file.write(f"Endereço: {endereco}\n")
            file.write(f"Bairro: {bairro}\n")
            file.write(f"Valor Total: R${valor_total:.2f}\n")
            file.write(f"Valor Recebido: R${valor_recebido:.2f}\n")
            file.write("\n")

    def imprimir_recibo(self, nome_cliente, endereco, bairro, valor_total, valor_recebido):
        # Define a impressora
        printer_name = win32print.GetDefaultPrinter()
        
        # Cria um contexto de impressão
        hdc = win32print.CreateDC("WINSPOOL", printer_name, None)
        hdc.StartDoc("Recibo de Entrega")
        hdc.StartPage()

        # Formata o texto a ser impresso
        text = (f"Recibo de Entrega\n\n"
                f"Nome do Cliente: {nome_cliente}\n"
                f"Endereço: {endereco}\n"
                f"Bairro: {bairro}\n"
                f"Valor Total: R${valor_total:.2f}\n"
                f"Valor Recebido: R${valor_recebido:.2f}\n")

        # Escreve o texto no contexto de impressão
        hdc.TextOut(100, 100, text)

        # Finaliza a página e o documento
        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

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

    #############################################
    #           segunda janela                  #
    #############################################
    #janela para configurar banco de dados

    def abrir_janela_adicionar_bairro(self):
        # Cria uma nova janela
        janela = tk.Toplevel(self.root)
        janela.title("Configurar Bairros")
        janela.geometry("400x230")

        # Campo para selecionar o bairro
        label_bairro = tk.Label(janela, text="Bairro:")
        label_bairro.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.combobox_bairro = ttk.Combobox(janela, values=self.buscar_bairros(), width=30)
        self.combobox_bairro.grid(row=0, column=1, padx=5, pady=5)

        # Campo para valor do bairro
        label_valor = tk.Label(janela, text="Taxa de Entrega: R$")
        label_valor.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.entry_valor = tk.Entry(janela)
        self.entry_valor.grid(row=1, column=1, padx=5, pady=5)

        # Botões de funcionalidade
        button_frame = tk.Frame(janela)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(button_frame, text="Adicionar", command=lambda: self.adicionar_bairro_no_banco(self.combobox_bairro.get(), self.entry_valor.get(), janela), width=11, height=2).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Atualizar", command=self.atualizar_valor_bairro, width=11, height=2).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Apagar", command=self.apagar_bairro, width=11, height=2, bg="red", fg="white").grid(row=0, column=2, padx=5)

    def atualizar_valor_bairro_combobox(self):
        bairro_selecionado = self.combobox_bairro.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT valor FROM bairros WHERE nome=?", (bairro_selecionado,))
        valor = cursor.fetchone()
        self.entry_valor.delete(0, tk.END)
        if valor:
            self.entry_valor.insert(0, valor[0])
        else:
            self.entry_valor.insert(0, "")



    def adicionar_bairro_no_banco(self, nome_bairro, valor_entrega, janela):
        if not nome_bairro or not valor_entrega:
            tk.messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            valor_entrega = float(valor_entrega)

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO bairros (nome, valor) VALUES (?, ?)", (nome_bairro, valor_entrega))
            self.conn.commit()
            cursor.close()

            tk.messagebox.showinfo("Sucesso", "Bairro adicionado com sucesso!")
            janela.destroy()
            self.combobox_bairro['values'] = self.buscar_bairros()
        except ValueError:
            tk.messagebox.showerror("Erro", "O valor de entrega deve ser um número.")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def atualizar_valor_bairro(self):
        bairro = self.combobox_bairro.get()
        valor = self.entry_valor.get().strip()
        
        if bairro and valor:
            try:
                valor = float(valor)
                cursor = self.conn.cursor()
                cursor.execute("UPDATE bairros SET valor = ? WHERE nome = ?", (valor, bairro))
                self.conn.commit()
                cursor.close()
                messagebox.showinfo("Sucesso", f"Valor do bairro '{bairro}' atualizado para '{valor}'!")
                self.entry_valor.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Erro", "O valor de entrega deve ser um número.")
        else:
            messagebox.showwarning("Atenção", "Por favor, selecione um bairro e preencha o valor.")

    def apagar_bairro(self):
        bairro = self.combobox_bairro.get()
        if bairro:
            confirmacao = messagebox.askyesno("Confirmação", f"Você realmente deseja apagar o bairro '{bairro}'?")
            if confirmacao:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM bairros WHERE nome = ?", (bairro,))
                self.conn.commit()
                cursor.close()
                messagebox.showinfo("Sucesso", f"Bairro '{bairro}' apagado com sucesso!")
                
                # Atualiza a lista de bairros no combobox
                self.atualizar_combobox()
                
                self.combobox_bairro.set('')  # Limpa a seleção do combobox
        else:
            messagebox.showwarning("Atenção", "Nenhum bairro selecionado.")

    def atualizar_combobox(self):
        # Limpa o menu do combobox e repopula com novos bairros
        self.combobox_bairro['values'] = self.buscar_bairros()

    def buscar_bairros(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nome FROM bairros")
        bairros = [row[0] for row in cursor.fetchall()]
        return bairros

    def atualizar_combobox(self):
        # Atualiza a lista de bairros no combobox
        self.combobox_bairro['values'] = self.buscar_bairros()

    def carregar_bairros(self):
        # Carregar bairros do banco de dados
        self.cursor.execute("SELECT * FROM bairros")
        bairros = self.cursor.fetchall()
        
        # Atualizar a lista de bairros no combobox
        self.combobox_bairro['values'] = [bairro[0] for bairro in bairros]

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

                    ######################################################
                    #                   parte grafica                    #
                    ######################################################
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

        # Combobox para bairros
        self.combobox_bairro = ttk.Combobox(self.main_frame, width=37)
        self.combobox_bairro.grid(row=3, column=1)
        self.combobox_bairro.bind("<<ComboboxSelected>>", self.atualizar_valor)  # Atualiza o valor ao selecionar um bairro

        # Campo de Valor de Entrega
        self.label_valor = tk.Label(self.main_frame, text="Valor de Entrega: R$", bg='indigo', fg='white')
        self.label_valor.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        self.entry_valor = tk.Entry(self.main_frame, width=40)
        self.entry_valor.grid(row=4, column=1)
        self.entry_valor.bind("<KeyRelease>", lambda event: self.atualizar_total())  # Atualiza total ao digitar

        # Campos de pagamento
        self.label_pagamento = tk.Label(self.main_frame, text="Forma de Pagamento:", bg='indigo', fg='white')
        self.label_pagamento.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.var_pagamento = StringVar(value=" ")
        self.combo_pagamento = tk.OptionMenu(self.main_frame, self.var_pagamento, "PIX", "Débito", "Crédito", "Dinheiro", command=self.atualizar_troco_display)
        self.combo_pagamento.grid(row=5, column=1, sticky="ew", padx=20, pady=10)

        # Botão Serviço
        self.label_servico = tk.Label(self.main_frame, text="Serviço:", bg='indigo', fg='white')
        self.label_servico.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        self.var_servico = StringVar(value=" ")
        self.combo_servico = tk.OptionMenu(self.main_frame, self.var_servico, "delivery", "retirada")
        self.combo_servico.grid(row=6, column=1, sticky="ew", padx=20, pady=10)

        # Caixa de Troco
        self.label_valor_recebido = tk.Label(self.main_frame, text="Valor Recebido: R$", bg='indigo', fg='white')
        self.label_valor_recebido.grid(row=7, column=0, sticky="w", padx=10, pady=5)

        self.entry_valor_recebido = tk.Entry(self.main_frame, width=40)
        self.entry_valor_recebido.grid(row=7, column=1)

        self.label_troco = tk.Label(self.main_frame, text="Troco:", bg='indigo', fg='white')
        self.label_troco.grid(row=8, column=0, sticky="w", padx=10, pady=5)

        self.entry_troco = tk.Entry(self.main_frame, width=40, state='readonly')
        self.entry_troco.grid(row=8, column=1)

        # Label para o Total
        self.label_total = tk.Label(self.main_frame, text="Total: R$", bg='indigo', fg='white')
        self.label_total.grid(row=8, column=0, sticky="w", padx=10, pady=(5, 0))  # Ajuste no pady

        # Caixa para mostrar o valor total
        self.entry_total = tk.Entry(self.main_frame, width=40, state='readonly')
        self.entry_total.grid(row=8, column=1, pady=(5, 0))  # Ajuste no pady


        # Inicialmente escondidos
        self.label_valor_recebido.grid_remove()
        self.entry_valor_recebido.grid_remove()
        self.label_troco.grid_remove()
        self.entry_troco.grid_remove()

        # Botões
        self.btn_exibir_entregas = tk.Button(self.main_frame, text="Exibir Entregas", command=self.exibir_entregas)
        self.btn_exibir_entregas.grid(row=10, column=1, padx=5, pady=10, sticky='ew')

        self.btn_repetir_entrega = tk.Button(self.main_frame, text="Repetir Última Entrega", command=self.repetir_entrega)
        self.btn_repetir_entrega.grid(row=10, column=0, padx=5, pady=10, sticky='ew')

        self.btn_realizar_entrega = tk.Button(self.main_frame, text="Realizar Entrega", command=self.realizar_entrega)
        self.btn_realizar_entrega.grid(row=11, columnspan=2, padx=5, pady=10, sticky='ew')

        # Configurar bairros
        botao_adicionar_bairro = tk.Button(self.main_frame, text="Configurações de Bairro", command=self.abrir_janela_adicionar_bairro, width=20, height=1)
        botao_adicionar_bairro.grid(row=11, column=2, padx=5, pady=(5, 0))  # Ajuste no pady


        # Ajuste de tamanho da Treeview e posicionamento à direita
        self.tree = ttk.Treeview(self.main_frame, columns=("Nome", "Valor"), show='headings', height=20)
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Valor", text="Valor")
        self.tree.column("Nome", width=200)
        self.tree.column("Valor", width=100)
        self.tree.grid(row=0, column=2, rowspan=10, padx=10, pady=10, sticky='nsew')

        # Configuração de colunas
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=3)
        self.main_frame.columnconfigure(3, weight=0)  # Para a coluna do separador

        # Chamar a função para atualizar o total
        self.atualizar_total()

    # Função para atualizar o total
    def atualizar_total(self):
        try:
            valor_produto_str = self.entry_valor.get().strip()
            taxa_entrega = self.obter_taxa_entrega()  # Função que deve retornar a taxa de entrega com base no bairro

            if valor_produto_str:
                valor_produto = float(valor_produto_str)
                total = valor_produto + taxa_entrega
            else:
                total = taxa_entrega  # Se não houver valor do produto, apenas a taxa é considerada

            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, f"{total:.2f}")  # Formatar o total para 2 casas decimais
            self.entry_total.config(state='readonly')
        except ValueError:
            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.config(state='readonly')

    def obter_taxa_entrega(self):
        try:
            bairro = self.combobox_bairro.get().strip()
            cursor = self.conn.cursor()
            cursor.execute("SELECT valor FROM bairros WHERE nome = ?", (bairro,))
            taxa_entrega = cursor.fetchone()
            return taxa_entrega[0] if taxa_entrega else 0  # Retorna 0 se não encontrar a taxa
        except Exception as e:
            return 0  # Retorna 0 em caso de erro


if __name__ == "__main__":
    root = tk.Tk()
    app = appEntregas(root)
    root.mainloop()