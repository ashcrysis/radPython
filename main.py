import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Conectar ao banco de dados
conn = sqlite3.connect('escola.db')
cursor = conn.cursor()

# Criação das tabelas de alunos e notas
cursor.execute('''
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    materia TEXT NOT NULL,
    nota REAL NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
)
''')
conn.commit()

# Funções para manipular dados
def adicionar_aluno():
    nome = entry_nome.get()
    if nome:
        cursor.execute("INSERT INTO alunos (nome) VALUES (?)", (nome,))
        conn.commit()
        entry_nome.delete(0, tk.END)
        atualizar_lista_alunos()
    else:
        messagebox.showwarning("Atenção", "Digite o nome do aluno.")

def adicionar_nota():
    aluno_id = combo_alunos.get().split('-')[0]
    materia = entry_materia.get()
    nota = entry_nota.get()
    if aluno_id and materia and nota:
        cursor.execute("INSERT INTO notas (aluno_id, materia, nota) VALUES (?, ?, ?)", (aluno_id, materia, float(nota)))
        conn.commit()
        entry_materia.delete(0, tk.END)
        entry_nota.delete(0, tk.END)
        atualizar_lista_notas()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos para adicionar uma nota.")

def atualizar_lista_alunos():
    lista_alunos.delete(*lista_alunos.get_children())
    for row in cursor.execute("SELECT * FROM alunos"):
        lista_alunos.insert("", tk.END, values=row)
    atualizar_combo_alunos()  # Atualiza o combo de alunos após a lista de alunos ser atualizada

def atualizar_combo_alunos():
    combo_alunos['values'] = [f"{row[0]} - {row[1]}" for row in cursor.execute("SELECT * FROM alunos")]
    if combo_alunos['values']:  # Se houver alunos, seleciona o primeiro automaticamente
        combo_alunos.set(combo_alunos['values'][0])  # Seleciona o primeiro aluno

def atualizar_lista_notas():
    lista_notas.delete(*lista_notas.get_children())
    aluno_id = combo_alunos.get().split('-')[0]
    # Modificando a consulta para pegar o nome do aluno junto com as notas
    query = '''
    SELECT notas.id, alunos.id, alunos.nome, notas.materia, notas.nota 
    FROM notas 
    JOIN alunos ON alunos.id = notas.aluno_id 
    WHERE notas.aluno_id = ?
    '''
    for row in cursor.execute(query, (aluno_id,)):
        lista_notas.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4]))  # Adicionando o nome do aluno (row[2])

def editar_aluno():
    try:
        selected_item = lista_alunos.selection()[0]
        aluno_id = lista_alunos.item(selected_item)['values'][0]
        novo_nome = entry_nome.get()
        if novo_nome:
            cursor.execute("UPDATE alunos SET nome = ? WHERE id = ?", (novo_nome, aluno_id))
            conn.commit()
            atualizar_lista_alunos()
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione um aluno para editar.")

def editar_nota():
    try:
        selected_item = lista_notas.selection()[0]
        nota_id = lista_notas.item(selected_item)['values'][0]
        nova_materia = entry_materia.get()
        nova_nota = entry_nota.get()
        if nova_materia and nova_nota:
            cursor.execute("UPDATE notas SET materia = ?, nota = ? WHERE id = ?", (nova_materia, float(nova_nota), nota_id))
            conn.commit()
            atualizar_lista_notas()
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione uma nota para editar.")

def deletar_aluno():
    try:
        selected_item = lista_alunos.selection()[0]
        aluno_id = lista_alunos.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        cursor.execute("DELETE FROM notas WHERE aluno_id = ?", (aluno_id,))
        conn.commit()
        atualizar_lista_alunos()
        atualizar_lista_notas()
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione um aluno para deletar.")

def deletar_nota():
    try:
        selected_item = lista_notas.selection()[0]
        nota_id = lista_notas.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM notas WHERE id = ?", (nota_id,))
        conn.commit()
        atualizar_lista_notas()
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione uma nota para deletar.")

# Interface gráfica
root = tk.Tk()
root.title("Gerenciamento de Notas")

# Widgets para Aluno
frame_aluno = tk.LabelFrame(root, text="Gerenciar Alunos")
frame_aluno.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_aluno, text="Nome do Aluno:").grid(row=0, column=0)
entry_nome = tk.Entry(frame_aluno)
entry_nome.grid(row=0, column=1)

tk.Button(frame_aluno, text="Adicionar Aluno", command=adicionar_aluno).grid(row=0, column=2)
tk.Button(frame_aluno, text="Editar Aluno", command=editar_aluno).grid(row=0, column=3)
tk.Button(frame_aluno, text="Deletar Aluno", command=deletar_aluno).grid(row=0, column=4)

# Lista de Alunos
lista_alunos = ttk.Treeview(frame_aluno, columns=("ID", "Nome"), show="headings")
lista_alunos.heading("ID", text="ID")
lista_alunos.heading("Nome", text="Nome")
lista_alunos.grid(row=1, column=0, columnspan=5, pady=10)

# Widgets para Notas
frame_notas = tk.LabelFrame(root, text="Gerenciar Notas")
frame_notas.pack(fill="both", expand="yes", padx=10, pady=10)

tk.Label(frame_notas, text="Aluno:").grid(row=0, column=0)
combo_alunos = ttk.Combobox(frame_notas, state="readonly")
combo_alunos.grid(row=0, column=1)
combo_alunos.bind("<<ComboboxSelected>>", lambda e: atualizar_lista_notas())  # Atualiza notas ao selecionar um aluno

tk.Label(frame_notas, text="Matéria:").grid(row=1, column=0)
entry_materia = tk.Entry(frame_notas)
entry_materia.grid(row=1, column=1)

tk.Label(frame_notas, text="Nota:").grid(row=1, column=2)
entry_nota = tk.Entry(frame_notas)
entry_nota.grid(row=1, column=3)

tk.Button(frame_notas, text="Adicionar Nota", command=adicionar_nota).grid(row=1, column=4)
tk.Button(frame_notas, text="Editar Nota", command=editar_nota).grid(row=2, column=4)
tk.Button(frame_notas, text="Deletar Nota", command=deletar_nota).grid(row=3, column=4)

lista_notas = ttk.Treeview(frame_notas, columns=("ID", "Aluno ID", "Nome", "Matéria", "Nota"), show="headings")
lista_notas.heading("ID", text="ID")
lista_notas.heading("Aluno ID", text="Aluno ID")
lista_notas.heading("Nome", text="Nome")  # Agora mostra o nome do aluno
lista_notas.heading("Matéria", text="Matéria")
lista_notas.heading("Nota", text="Nota")
lista_notas.grid(row=2, column=0, columnspan=4, pady=10)
# Atualizar lista de alunos e notas ao iniciar
atualizar_lista_alunos()

root.mainloop()
conn.close()
