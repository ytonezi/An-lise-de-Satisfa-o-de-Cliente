# -*- coding: utf-8 -*-
# 🎀 Sistema de Satisfação do Cliente 🎀 #

# 📚 IMPORTAÇÃO DE BIBLIOTECAS 📚 #

import streamlit as st # Streamlit: Framework de interface web
import sqlite3 # SQLite: Banco de dados
import nltk # Natural Language Tool Kit: ferramentas de NLP
from nltk.sentiment.vader import SentimentIntensityAnalyzer # Analisador de sentimento da NLTK
from googletrans import Translator # Tradutor do google
import pandas as pd # Pandas: para a manipulação de dados e gráficos

# Instalação do analisador 'VADER'
nltk.download("vader_lexicon")

# 📩 FUNÇÃO PARA TRADUÇÃO DE COMENTÁRIO 📩 #
def traduzir_para_ingles(texto):
    tradutor = Translator()
    try:
        traducao = tradutor.translate(texto, src='pt', dest='en')
        return traducao.text
    except Exception as e:
        st.error(f"Erro na tradução: {e}") # Mostra erro em caso de falha na tradução
        return texto # Retorna texto original para evitar falha completa da análise

# 🎲 BANCO DE DADOS 🎲 #

# Função para criação de tabelas no banco de dados, caso não existam
def criar_tabelas():
    conexao = sqlite3.connect('banco1.db') # Conexão com o banco de dados SQLite
    cursor = conexao.cursor() # Execução de comandos SQL

# Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

# Tabela de contagem de sentimentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analise_sentimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentimento TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')

# Tabela de armazenamento de comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL, 
            comentario TEXT NOT NULL, 
            sentimento TEXT NOT NULL 
        )
    ''')

    conexao.commit() # Salva as alterações no banco de dados
    conexao.close() # Fecha a conexão com o banco de dados

# Função para o cadastro de um novo usuário
def cadastrar_usuario(nome, email, senha):
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM cadastro WHERE email = ?', (email,)) # Verifica a existÊncia do usuário
    if cursor.fetchone(): # Se encontra um registro, significa que o email do usuário já existe
        conexao.close()
        return False # Usuário já cadastrado !
    cursor.execute('INSERT INTO cadastro (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha)) # Cria novo usuário
    conexao.commit()
    conexao.close()
    return True # Cadastro bem sucedido !

# Função para a validação do login do usuário
def login_usuario(nome, email, senha):
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM cadastro WHERE nome = ? AND email = ? AND senha = ?', (nome, email, senha)) # Verifica existência de usuário de acordo com estes dados
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None # Retorna True se encontra o usuário

# Função para atualização da contagem de sentimento na tabela do banco de dados
def atualizar_sentimento(sentimento):
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT quantidade FROM analise_sentimentos WHERE sentimento = ?', (sentimento,))
    resultado = cursor.fetchone()
    if resultado:
        nova_quantidade = resultado[0] + 1
        cursor.execute('UPDATE analise_sentimentos SET quantidade = ? WHERE sentimento = ?', (nova_quantidade, sentimento))
    else:
        cursor.execute('INSERT INTO analise_sentimentos (sentimento, quantidade) VALUES (?, ?)', (sentimento, 1))
    conexao.commit()
    conexao.close()

# Função para  aconsulta de dados de sentimentos para a montagem do gráfico
def consultar_sentimentos():
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT sentimento, quantidade FROM analise_sentimentos')
    dados = cursor.fetchall()
    conexao.close()
    return dados

# Função para salvar o comentário individual juntamente ao seu sentimento
def salvar_comentario(usuario, comentario, sentimento):
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO comentarios (usuario, comentario, sentimento) VALUES (?, ?, ?)', (usuario, comentario, sentimento))
    conexao.commit()
    conexao.close()

# Função para a consulta de todos os comentários salvos
def consultar_comentarios():
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT id, usuario, comentario, sentimento FROM comentarios')
    dados = cursor.fetchall()
    conexao.close()
    return dados

# Função para exclusão de comentário
def excluir_comentario(id_comentario):
    conexao = sqlite3.connect('banco1.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM comentarios WHERE id = ?', (id_comentario,))
    conexao.commit()
    conexao.close()

# Inicializa as tabelas ao carregar o sistema
criar_tabelas()

# 🔎 CONSULTA DE SENTIMENTOS 🔎 #

# Identifica a presença de login na sessão, e define como falso casi não haja
if 'logado' not in st.session_state:
    st.session_state.logado = False

# Interface inicial de Login e Cadastro
if st.session_state.logado == False:
    st.title("Sistema de Satisfação") # Título principal

    aba = st.sidebar.selectbox("Escolha a opção:", ["Login", "Cadastro"]) # Criação de aba lateral de navegação

    if aba == "Cadastro":
        st.subheader("Criar Conta")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if nome and email and senha:
                sucesso = cadastrar_usuario(nome, email, senha)
                if sucesso:
                    st.success("✅ Cadastro realizado com sucesso! Vá para a aba Login.")
                else:
                    st.error("❌ Este email já está cadastrado.")
            else:
                st.warning("⚠️ Preencha todos os campos.")

    elif aba == "Login":
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Login"):
            if nome and email and senha:
                sucesso = login_usuario(nome, email, senha)
                if sucesso:
                    st.success("✅ Login realizado com sucesso!")
                    st.session_state.logado = True
                    st.session_state.nome_usuario = nome
                else:
                    st.error("❌ Dados incorretos. Verifique e tente novamente.")
            else:
                st.warning("⚠️ Preencha todos os campos.")

# Interface da página principal
else:
    st.title("Sistema de Satisfação do Cliente")

    menu = st.sidebar.selectbox("Menu", ["Fazer Comentário", "Dashboard"])  # Criação de aba lateral de navegação

    # Tela de envio de comentário
    if menu == "Fazer Comentário":
        st.subheader("Envie seu comentário")

        user_input = st.text_input("Por favor, avalie o nosso atendimento:")

        if user_input:
            texto_traduzido = traduzir_para_ingles(user_input)
            s = SentimentIntensityAnalyzer()
            score = s.polarity_scores(texto_traduzido)

            st.subheader("Comentário:")

            # Detecção de sentimento com base na pontuação
            if score["compound"] >= 0.05:
                sentimento_detectado = "Positivo"
                st.write("🟩 Muito obrigado pela sua avaliação, vamos trabalhar para continuar assim!")
            elif score["compound"] <= -0.05:
                sentimento_detectado = "Negativo"
                st.write("🟥 Sentimos muito pela sua experiência, vamos trabalhar para melhorar isso.")
            else:
                sentimento_detectado = "Neutro"
                st.write("🟨 Agradecemos a sua avaliação, estamos buscando melhora em nossos serviços!")

            atualizar_sentimento(sentimento_detectado) # Atualiza contagem agregada
            salvar_comentario(st.session_state.nome_usuario, user_input, sentimento_detectado)

    # Tela DASHBOARD
    elif menu == "Dashboard":
        st.subheader("Dashboard de Sentimentos")

        dados = consultar_sentimentos()
        if dados:
            df = pd.DataFrame(dados, columns=['Sentimento', 'Quantidade'])  # Biblioteca PANDAS para criação de tabela
            st.bar_chart(df.set_index('Sentimento')) # Exibe gráfico de sentimentos
        else:
            st.write("Nenhum dado de sentimento registrado ainda.")

        st.subheader("Gerenciar Comentários")
        comentarios = consultar_comentarios()

        if comentarios:
            for id_coment, usuario, texto, sentimento in comentarios:
                with st.expander(f"Comentário de {usuario} - {sentimento}"):
                    st.write(texto)
                    if st.button(f"Excluir comentário {id_coment}", key=id_coment):
                        excluir_comentario(id_coment)
                        st.success("Comentário excluído com sucesso.")
                        st.rerun() # Recarrega a pagina para atualizar a lista
        else:
            st.write("Nenhum comentário registrado.")