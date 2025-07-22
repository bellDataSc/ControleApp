"""
EquipeApp - Controle simples de demandas
Requisitos:
  pip install streamlit pandas
Execute localmente:
  streamlit run app.py
"""
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

# ---------- Config inicial ----------
DB_NAME = 'equipeapp.sqlite'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    responsavel TEXT,
                    prioridade TEXT,
                    status TEXT,
                    criado_em TEXT,
                    atualizado_em TEXT)
             """)
    conn.commit()
    conn.close()

@st.cache_data(show_spinner=False)
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

init_db()
conn = get_conn()
c = conn.cursor()

# ---------- Funções de DB ----------

def add_task(titulo, desc, resp, prioridade):
    now = datetime.now().isoformat(' ', 'seconds')
    c.execute("INSERT INTO tasks (titulo, descricao, responsavel, prioridade, status, criado_em, atualizado_em) VALUES (?,?,?,?,?,?,?)",
              (titulo, desc, resp, prioridade, 'Novo', now, now))
    conn.commit()


def update_status(task_id, new_status):
    now = datetime.now().isoformat(' ', 'seconds')
    c.execute("UPDATE tasks SET status=?, atualizado_em=? WHERE id=?", (new_status, now, task_id))
    conn.commit()


def load_tasks():
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    return df

# ---------- UI ----------
st.set_page_config(page_title='EquipeApp', layout='wide')
st.title('📋 EquipeApp - Controle de Demandas')

menu = st.sidebar.selectbox('Menu', ['Dashboard', 'Nova Solicitação', 'Tarefas'])

if menu == 'Nova Solicitação':
    st.header('📝 Nova Solicitação')
    with st.form('nova'):
        titulo = st.text_input('Título')
        desc = st.text_area('Descrição')
        resp = st.selectbox('Responsável', ['Ana', 'Bruno', 'Carlos', 'Diana'])
        prioridade = st.selectbox('Prioridade', ['Alta', 'Média', 'Baixa'])
        submitted = st.form_submit_button('Criar')
    if submitted and titulo:
        add_task(titulo, desc, resp, prioridade)
        st.success('Solicitação criada com sucesso!')

elif menu == 'Tarefas':
    st.header('📑 Lista de Solicitações')
    df = load_tasks()
    if not df.empty:
        status_filter = st.multiselect('Filtrar status', df['status'].unique(), default=list(df['status'].unique()))
        df_f = df[df['status'].isin(status_filter)]
        st.dataframe(df_f, use_container_width=True)
        ids = df_f['id'].tolist()
        if ids:
            sel_id = st.selectbox('Selecionar ID para mudar status', ids)
            new_status = st.selectbox('Novo status', ['Novo', 'Em Andamento', 'Concluído'])
            if st.button('Atualizar'):
                update_status(sel_id, new_status)
                st.success('Status atualizado!')
    else:
        st.info('Nenhuma solicitação cadastrada.')

else:  # Dashboard
    st.header('📊 Dashboard')
    df = load_tasks()
    col1, col2, col3 = st.columns(3)
    col1.metric('Total', len(df))
    col2.metric('Em Andamento', (df['status']=='Em Andamento').sum())
    col3.metric('Concluídas', (df['status']=='Concluído').sum())
    st.dataframe(df.tail(10), use_container_width=True)
