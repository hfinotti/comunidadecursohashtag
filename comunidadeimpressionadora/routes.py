from flask import render_template, request, redirect, url_for, flash, abort
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
import secrets
import os

@app.route("/")  # Decorator
def home():
    # db.session.query(Usuario, Post).join(Post).all()
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("home.html", posts=posts)


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/usuarios")
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios = lista_usuarios)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_enviar_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login efetuado com suceesso para o e-mail: {form_login.email_login.data}', 'alert-success')
            parm_next = request.args.get("next")
            if parm_next:
                return redirect(url_for(parm_next.replace("/", "")))
            else:
                return redirect(url_for("home"))
        else:
            flash(f'Falha do login, e-mail ou senha invalidos!', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_enviar_criarconta' in request.form:
        # bcrypt.check_password_hash(senha_crypt, senha) verifica se a senha é valida
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Criar conta efetuado com suceesso para o e-mail {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for("home"))

    return render_template("login.html", form_login = form_login, form_criarconta = form_criarconta)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f'Logout efetuado com suceesso!', 'alert-success')
    return redirect(url_for("home"))


@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template("perfil.html", foto_perfil = foto_perfil)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static\\fotos_perfil', nome_arquivo)
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    if lista_cursos:
        return ';'.join(lista_cursos)
    else:
        return 'Não Informado'

@app.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form_editarperfil = FormEditarPerfil()
    if form_editarperfil.validate_on_submit():
        current_user.username = form_editarperfil.username.data
        current_user.email = form_editarperfil.email.data
        if form_editarperfil.foto_perfil.data:
            nome_imagem = salvar_imagem(form_editarperfil.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form_editarperfil)
        database.session.commit()
        flash('Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for("perfil"))
    elif request.method == "GET":
        form_editarperfil.username.data = current_user.username
        form_editarperfil.email.data = current_user.email
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template("editarperfil.html", foto_perfil=foto_perfil, form_editarperfil=form_editarperfil)


@app.route("/post/criar", methods=["GET", "POST"])
@login_required
def criar_post():
    form_criarpost = FormCriarPost()
    if form_criarpost.validate_on_submit():
        post = Post(titulo=form_criarpost.titulo.data, corpo=form_criarpost.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso!', 'alert-success')
        return redirect(url_for("home"))
    return render_template("criarpost.html", form_criarpost=form_criarpost)


@app.route('/post/<post_id>', methods=["GET", "POST"])
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso!', 'alert-success')
            return redirect(url_for("home"))
    else:
        form = None
    return render_template("post.html", post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=["GET", "POST"])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post deletado com sucesso!', 'alert-danger')
        return redirect(url_for("home"))
    else:
        abort(403)
