from flask import render_template, request, redirect, session, flash, url_for, send_from_directory
from listaCompras import app, db
from models import Lista
from helpers import recupera_imagem, deleta_arquivo, FormularioJogo
import time


@app.route('/')
def index():
    lista = Lista.query.order_by(Lista.id)
    return render_template('lista.html', titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioJogo()
    return render_template('novo.html', titulo='Novo Jogo', form=form)

@app.route('/criar', methods=['POST',])
def criar():
    form = FormularioJogo(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('novo'))

    nome = form.nome.data
    categoria = form.categoria.data
    console = form.console.data

    compra = Lista.query.filter_by(nome=nome).first()

    if compra:
        flash('compra já existente!')
        return redirect(url_for('index'))

    nova_compra = Lista(nome=nome, categoria=categoria, console=console)
    db.session.add(nova_compra)
    db.session.commit()

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    arquivo.save(f'{upload_path}/capa{nova_compra.id}-{timestamp}.jpg')

    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))
    compra = Lista.query.filter_by(id=id).first()
    form = FormularioJogo()
    form.nome.data = compra.nome
    form.categoria.data = compra.categoria
    form.console.data = compra.console
    capa_compra = recupera_imagem(id)
    return render_template('editar.html', titulo='Editando Jogo', id=id, capa_jogo=capa_compra, form=form)

@app.route('/atualizar', methods=['POST',])
def atualizar():
    form = FormularioJogo(request.form)

    if form.validate_on_submit():
        compra = Lista.query.filter_by(id=request.form['id']).first()
        compra.nome = form.nome.data
        compra.categoria = form.categoria.data
        compra.console = form.console.data

        db.session.add(compra)
        db.session.commit()

        arquivo = request.files['arquivo']
        upload_path = app.config['UPLOAD_PATH']
        timestamp = time.time()
        deleta_arquivo(id)
        arquivo.save(f'{upload_path}/capa{compra.id}-{timestamp}.jpg')

    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    Lista.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Item deletado com sucesso!')

    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)