import json
import urllib.request

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

# Cria uma instância da classe Flask
app = Flask(__name__)

# Configuração da URI para banco de dados SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cursos.sqlite3"
app.config['SECRET_KEY'] = "random string"

# Inicialização da instância do SQLAlchemy com base nas configurações do aplicativo Flask
db = SQLAlchemy(app)

# Escopo global: Listas vazias para armazenar frutas e registros de notas
frutas = []
registros = []

# Definição da classe 'cursos' que representa uma tabela no banco de dados


class cursos(db.Model):
    # Definição das colunas da tabela 'cursos'
    id = db.Column(db.Integer, primary_key=True)  # Coluna de chave primária
    nome = db.Column(db.String(50))  # Coluna para armazenar o nome do curso
    # Coluna para armazenar a descrição do curso
    descricao = db.Column(db.String(100))
    # Coluna para armazenar a carga horária do curso
    ch = db.Column(db.Integer)

    # Método construtor da classe 'cursos' para inicializar objetos desta classe
    def __init__(self, nome, descricao, ch):
        self.nome = nome
        self.descricao = descricao
        self.ch = ch

# metodo para adiciona frutas a nossa lista via metodo de requisição(request method) POST
# Define a rota principal ('/') e especifica que aceita os métodos GET e POST


@app.route('/', methods=["GET", "POST"])
def principal():
    # frutas = ["Morango", "Uva", "Laranja", "Mamão", "Maçã", "Pêra", "Melão", "Abacaxi"]
    # Se o método da requisição for POST, ou seja, se um formulário foi enviado
    if request.method == "POST":
        # Verifica se há um campo 'fruta' no formulário enviado
        if request.form.get("fruta"):
            # Adiciona a fruta enviada para a lista de frutas
            frutas.append(request.form.get("fruta"))
    # Renderiza o template 'index.html' e passa a lista de frutas para ele
    return render_template("index.html", frutas=frutas)


# Define a rota '/sobre' e especifica que aceita os métodos GET e POST
@app.route('/sobre', methods=["GET", "POST"])
def sobre():
    # notas = {"Fulano":5.0, "Beltrano":6.0, "Aluno":7.0, "Sicrano":8.5, "Rodrigo":9.5}
    # se o metodo da requisição for POST verifica se existe o aluno e existe anota
    # Se o método da requisição for POST, ou seja, se um formulário foi enviado
    if request.method == "POST":
        # Verifica se há campos 'aluno' e 'nota' no formulário enviado
        if request.form.get("aluno") and request.form.get("nota"):
            # se existir, chama a lista registros e dentro dela passa um dicionario
            # e dicionario tem a chave aluno e o valor nota
            registros.append({"aluno": request.form.get(
                "aluno"), "nota": request.form.get("nota")})

    # Renderiza o template 'sobre.html' e passa a lista de registros para ele
    return render_template("sobre.html", registros=registros)

# Define a rota '/filme'


@app.route('/filmes<propriedade>')
def filmes(propriedade):

    if propriedade == 'populares':
        url = "https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=dbaa26daf76b4135a4395ff16587c2b2"
    elif propriedade == 'kids':
        url = "https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=dbaa26daf76b4135a4395ff16587c2b2"
    elif propriedade == '2010':
        url = "https://api.themoviedb.org/3/discover/movie?primary_release_year=2010&sort_by=vote_average.desc&api_key=dbaa26daf76b4135a4395ff16587c2b2"
    elif propriedade == 'drama':
        url = "https://api.themoviedb.org/3/discover/movie?with_genres=18&sort_by=vote_average.desc&vote_count.gte=10&api_key=dbaa26daf76b4135a4395ff16587c2b2"
    elif propriedade == 'tom_cruise':
        url = "https://api.themoviedb.org/3/discover/movie?with_genres=878&with_cast=500&sort_by=vote_average.desc&api_key=dbaa26daf76b4135a4395ff16587c2b2"

    # Abre a conexão com a URL e obtem resposta
    resposta = urllib.request.urlopen(url)

    # Lê os dados da resposta
    dados = resposta.read()

    # Converte os dados Json em um objeto Python
    jsondata = json.loads(dados)

    # Extrai a lista de filmes do objeto Python convertido
    # filmes = jsondata['results']

    # Renderiza o tamplete 'filmes.html' e passa a lista de filmes para ele
    return render_template("filmes.html", filmes=jsondata['results'])


@app.route('/cursos')
def lista_cursos():
    # Obtém o número da página da query string da URL, se não estiver presente, usa 1 como padrão
    page = request.args.get('page', 1, type=int)
    per_page = 4  # Define quantos cursos mostrar por página
    # Realiza a consulta ao banco de dados para obter os cursos paginados
    todos_cursos = cursos.query.paginate(page=page, per_page=per_page)
    # Renderiza o template 'cursos.html' e passa a lista de cursos para o template
    return render_template("cursos.html", cursos=todos_cursos)


@app.route('/cria_curso', methods=["GET", "POST"])
def cria_curso():
    # Obtém os dados do formulário HTML enviado
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    ch = request.form.get('ch')

    # Se o método da requisição for POST, processa o formulário
    if request.method == 'POST':
        # Verifica se todos os campos do formulário estão preenchidos
        if not nome or not descricao or not ch:
            # Se algum campo estiver vazio, exibe uma mensagem de erro
            flash("Preencha todos os campos do formulário", "error")
        else:
            # Cria um novo curso com os dados fornecidos
            curso = cursos(nome, descricao, ch)
            # Adiciona o novo curso ao banco de dados
            db.session.add(curso)
            # Confirma a transação
            db.session.commit()
            # Redireciona o usuário para a página de listagem de cursos
            return redirect(url_for('lista_cursos'))
    # Renderiza o template 'novo_curso.html' para exibir o formulário
    return render_template("novo_curso.html")


@app.route('/<int:id>/atualiza_curso', methods=["GET", "POST"])
def atualiza_curso(id):
    # Obtém o curso correspondente ao ID fornecido na URL
    curso = cursos.query.filter_by(id=id).first()
    # Se o método da requisição for POST, atualiza os dados do curso
    if request.method == 'POST':
        # Obtém os dados atualizados do formulário HTML
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        ch = request.form["ch"]

        # Atualiza os dados do curso no banco de dados
        cursos.query.filter_by(id=id).update(
            {"nome": nome, "descricao": descricao, "ch": ch})
        # Confirma a transação
        db.session.commit()
        # Redireciona o usuário para a página de listagem de cursos
        return redirect(url_for('lista_cursos'))
    # Renderiza o template 'atualiza_curso.html' e passa o curso para ser editado
    return render_template("atualiza_curso.html", curso=curso)


@app.route('/<int:id>/remove_curso')
def remove_curso(id):
    # Obtém o curso correspondente ao ID fornecido na URL
    curso = cursos.query.filter_by(id=id).first()
    # Remove o curso do banco de dados
    db.session.delete(curso)
    # Confirma a transação
    db.session.commit()
    # Redireciona o usuário para a página de listagem de cursos
    return redirect(url_for('lista_cursos'))


if __name__ == "__main__":
    # Inicia o servidor Flask em modo de depuração
    with app.app_context():
        # Cria todas as tabelas do banco de dados, se não existirem
        db.create_all()
    # Inicia o servidor Flask
    app.run(debug=True)
