import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

def conectar():
    return sqlite3.connect('SystemAutoFlow.db')

# --- BANCO DE DADOS ---
def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute('''
               CREATE TABLE IF NOT EXISTS vendas(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               produto TEXT NOT NULL,
               valor REAL NOT NULL,
               data TEXT NOT NULL
               )''')
    conn.commit()
    conn.close()          

# --- CRUD ---
def inserir_venda():
    produto = entry_produto.get().strip()
    valor = entry_valor.get().strip()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if produto and valor:
        try:
            conn = conectar()
            c = conn.cursor()
            c.execute('INSERT INTO vendas (produto, valor, data) VALUES (?,?,?)', 
                      (produto, float(valor), data_atual))
            conn.commit()
            conn.close()
            limpar_campos()
            atualizar_tela()
        except ValueError:
            messagebox.showerror('Erro', 'O valor deve ser numérico (ex: 150.50)')
    else:
        messagebox.showwarning('Atenção', 'Preencha o Produto e o Valor')

def atualizar_tela():
    for row in tree.get_children():
        tree.delete(row)
    
    conn = conectar()
    c = conn.cursor()        
    c.execute('SELECT * FROM vendas')
    vendas = c.fetchall()
    
    total_faturado = 0
    contador = 0
    
    for venda in vendas:
        if contador % 2 == 0:
            tree.insert('', 'end', values=venda, tags=('linha_par',))
        else:
            tree.insert('', 'end', values=venda, tags=('linha_impar',))
            
        total_faturado += venda[2] 
        contador += 1
    
    conn.close()
    lbl_total.config(text=f"Faturamento Total: R$ {total_faturado:.2f}")

def editar_venda():
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning('Atenção', 'Selecione uma venda na lista para editar')
        return

    item_id = tree.item(selecao)['values'][0]
    novo_produto = entry_produto.get()
    novo_valor = entry_valor.get()
    
    if novo_produto and novo_valor:
        conn = conectar()
        c = conn.cursor()
        c.execute('UPDATE vendas SET produto = ?, valor = ? WHERE id = ?', 
                  (novo_produto, float(novo_valor), item_id))
        conn.commit()
        conn.close()
        limpar_campos()
        atualizar_tela()
    else:
        messagebox.showwarning('Atenção', 'Preencha os novos dados nos campos de texto acima e clique em Editar')

def deletar_venda():
    selecao = tree.selection()
    if selecao:
        venda_id = tree.item(selecao)['values'][0]
        conn = conectar()
        c = conn.cursor()
        c.execute('DELETE FROM vendas WHERE id = ?', (venda_id,))
        conn.commit()
        conn.close()
        atualizar_tela()
    else:
        messagebox.showerror('Erro', 'Selecione uma venda na lista para excluir')

def limpar_campos():
    entry_produto.delete(0, tk.END)
    entry_valor.delete(0, tk.END)

# --- INTERFACE ---
janela = tk.Tk()
janela.geometry('750x600')
janela.title('SystemAutoflow')

# Paleta de Cores
BG_COLOR = "#C5DFEA"       
ACCENT_COLOR = "#007BFF"   
TEXT_COLOR = "#1A1A1A"     

janela.configure(bg=BG_COLOR)

# Estilização
style = ttk.Style()
style.theme_use('clam')


style.configure('TFrame', background=BG_COLOR)
style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 10))
style.configure('TLabelframe', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 10, 'bold'))
style.configure('TLabelframe.Label', background=BG_COLOR)


style.configure('TButton', 
                background=ACCENT_COLOR, 
                foreground='white', 
                font=('Segoe UI', 10, 'bold'),
                borderwidth=0,
                padding=8)
style.map('TButton', background=[('active', '#0056b3')]) 

# Tabela (Treeview) 
style.configure('Treeview', 
                background="#FFFFFF", 
                foreground=TEXT_COLOR,
                rowheight=35, 
                font=('Segoe UI', 10),
                borderwidth=0)

# Cabeçalho da Tabela
style.configure('Treeview.Heading', 
                background="#82B3EF", 
                foreground=TEXT_COLOR, 
                font=('Segoe UI', 10, 'bold'),
                borderwidth=0,
                padding=5)

# Cor de seleção 
style.map('Treeview', 
          background=[('selected', ACCENT_COLOR)],
          foreground=[('selected', 'white')])

# --- ESTRUTURA DOS FRAMES ---
main_frame = ttk.Frame(janela, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

titulo = ttk.Label(main_frame, text='SystemAutoflow ', font=('Segoe UI', 18, 'bold',), foreground=ACCENT_COLOR)
titulo.grid(row=0, columnspan=2, pady=(0,20), sticky='w')

# --- CAMPOS DE ENTRADA ---
input_frame = ttk.LabelFrame(main_frame, text=' LANÇAMENTO ', padding=15)
input_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,20))

ttk.Label(input_frame, text='Produto:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_produto = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
entry_produto.grid(row=0, column=1, padx=5, pady=5, sticky='w')

ttk.Label(input_frame, text='Valor (R$):').grid(row=1, column=0, padx=5, pady=5, sticky='e')
entry_valor = ttk.Entry(input_frame, width=20, font=('Segoe UI', 11))
entry_valor.grid(row=1, column=1, padx=5, pady=5, sticky='w')

# --- BOTÕES ---
btn_frame = ttk.Frame(main_frame)
btn_frame.grid(row=2, column=0, columnspan=2, pady=(0,20), sticky='w')

ttk.Button(btn_frame, text='➕ SALVAR', command=inserir_venda).pack(side=tk.LEFT, padx=(0, 10))
ttk.Button(btn_frame, text='✏️ EDITAR', command=editar_venda).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text='🗑️ EXCLUIR', command=deletar_venda).pack(side=tk.LEFT, padx=10)

# --- TREEVIEW (TABELA) ---
tree_frame = ttk.Frame(main_frame)
tree_frame.grid(row=3, column=0, columnspan=2, sticky='nsew')

columns = ('ID', 'PRODUTO', 'VALOR', 'DATA/HORA')
tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Centralizando os dados
tree.heading('ID', text='ID')
tree.column('ID', width=50, anchor='center')

tree.heading('PRODUTO', text='PRODUTO')
tree.column('PRODUTO', width=250, anchor='w')

tree.heading('VALOR', text='VALOR (R$)')
tree.column('VALOR', width=120, anchor='center')

tree.heading('DATA/HORA', text='DATA/HORA')
tree.column('DATA/HORA', width=150, anchor='center')


tree.tag_configure('linha_par', background='#FFFFFF')
tree.tag_configure('linha_impar', background="#C3CEDA")

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# --- RODAPÉ ---
lbl_total = ttk.Label(main_frame, text="Faturamento Total: R$ 0.00", font=('Segoe UI', 14, 'bold'), foreground='#28A745') 
lbl_total.grid(row=4, column=0, columnspan=2, pady=15, sticky='e')

main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(3, weight=1)

criar_tabela()
atualizar_tela()

janela.mainloop()