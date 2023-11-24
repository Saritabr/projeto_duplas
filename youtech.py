from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid
import os


app = Flask(__name__)
app.secret_key ="empresayoutech"

#USUÁRIO
usuario="usuario"
senha="lindinhas"
login= False

# ---------------  FUNÇÕES
#VERIFICA A SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

#CONEXAO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_youtech.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()



# ----------------- ROTAS -----------------
#ROTA DA PÁGINA INICIAL
@app.route('/')
def index():
    iniciar_db() #chamando o BD
    conexao = conecta_database()
    vagas= conexao.execute('SELECT * FROM vagas ORDER BY id_vagas DESC').fetchall()#colocar na ordem os post (o último por primeiro)
    conexao.close()   
    title= "Faça parte dessa equipe"
    return render_template("trabalho.html", vagas=vagas, title=title)


#ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    title="Login"
    return render_template("login.html",title=title)

# ROTA DA PÁGINA DE BUSCA
@app.route("/busca", methods=["post"])
def busca():
    busca=request.form['Buscar']
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE cargo_vagas LIKE "%" || ? ||  "%"',(busca,)).fetchall() 
    title="Trabalhe conosco"
    return render_template("trabalho.html", vagas =vagas, title=title)

# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")
    
#ROTA DO ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vagas DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", vagas=vagas, title=title)
    else:
        return redirect("/login")
    
#ROTA LOGOUT
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')
    
#ROTA  DA PÁGINA DE CADASTRO
@app.route("/cadvagas")
def cadvagas():
    if verifica_sessao():
        iniciar_db()
        title = "Cadastro de vagas"
        return render_template("cadvagas.html", title=title)
    else:
        return redirect('/login')

# ROTA DA PÁGINA DE CADASTRO NO BANCO 
@app.route("/cadastro", methods=["POST"])
def cadastro():
    if verifica_sessao():
        cargo_vagas = request.form['cargo_vagas']
        requisitos_vagas = request.form['requisitos_vagas']
        salario_vagas = request.form['salario_vagas']
        local_vagas = request.form ['local_vagas']
        email_vagas = request.form ['email_vagas']
        img_vagas = request.files.get('img_vagas')  # Use get para evitar erros se a chave 'img_prod' não estiver presente
        if img_vagas:  # Se foi enviada uma imagem
            id_foto = str(uuid.uuid4().hex)
            filename = (id_foto + cargo_vagas + '.png')
            img_vagas.save(os.path.join("static/img/vagas/", filename))
        else:  # Caso contrário, use uma imagem padrão
            filename = 'imagem_padrao.png'  # Substitua 'imagem_padrao.png' pelo nome do seu arquivo de imagem padrão
        conexao = conecta_database()
        conexao.execute('INSERT INTO vagas (cargo_vagas, requisitos_vagas, salario_vagas, local_vagas, email_vagas, img_vagas) VALUES (?, ?, ?, ?, ?, ?)', (cargo_vagas, requisitos_vagas, salario_vagas, local_vagas, email_vagas, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/trabalho")
#ROTA DE EXCLUSÃO
@app.route("/excluir/<id_vagas>")
def excluir(id_vagas):
    conexao = conecta_database()
    conexao.execute("DELETE FROM vagas WHERE id_vagas = ?",(id_vagas,))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

#CRIAR A ROTA DO EDITAR
@app.route("/editvagas/<id_vagas>")
def editar(id_vagas):  
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas =conexao.execute('SELECT * FROM vagas WHERE id_vagas = ?',(id_vagas,)).fetchall()
        conexao.close()
        title = "Edição de vagas"
        return render_template("editar.html", vagas=vagas, title=title)
    else:
        return redirect("/login")
    
#CRIAR A ROTA PARA TRATAR A EDIÇÃO
@app.route("/editarvagas", methods=['POST'])
def editvagas():
    id_vagas = request.form['id_vagas']
    cargo_vagas=request.form['cargo_vagas']
    requisitos_vagas=request.form['requisitos_vagas']
    salario_vagas=request.form['salario_vagas']
    local_vagas=request.form['local_vagas']
    email_vagas=request.form['email_vagas']
    nome_imagem = request.form['nome_imagem']
    img_vagas=request.files['img_vagas']
    conexao = conecta_database()
    conexao.execute( 'UPDATE vagas SET cargo_vagas = ?,  requisitos_vagas = ?, salario_vagas = ?, local_vagas = ?, email_vagas = ?, img_vagas = ? WHERE id_vagas= ?', (cargo_vagas, requisitos_vagas, salario_vagas, local_vagas, email_vagas, nome_imagem, id_vagas))
    conexao.commit()
    conexao.close()
    if img_vagas:  # Se foi enviada uma imagem
        img_vagas.save(os.path.join("static/img/vagas/", nome_imagem))
    
    return redirect('/adm')
    
#CRIAR A ROTA PARA VER AS VAGAS
@app.route("/vervagas/<id_vagas>")
def vervagas(id_vagas):  
    iniciar_db()
    id_vagas = int(id_vagas)
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE id_vagas = ?',(id_vagas,)).fetchall()
    conexao.close()
    title = "Ver vagas"
    return render_template("vervagas.html", vagas = vagas, title=title)

app.run(debug=True)
    


   