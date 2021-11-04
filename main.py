from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import sqlite3

enotas = Flask(__name__)
banco_de_dados = 'banco_enotas.db'


############################################################################
# FUNÇÕES AUXILIARES
####################
def exibir_registros(registros):
    html = ''
    if len(registros) == 0:
        html = '''
        <p>Nenhuma nota encontrada, cadastre sua primeira nota
        <a href="/notas">LINK</a>.</p>'''
        return html
    else:
        html = '<ul>'
        for registro in registros:
            html += '''
            <li>ID: {2}</li>
            <li><strong>Título</strong>: {0}</li>
            <br>
            <li>Descrisão: {1}</li>
            <br><br>'''.format(registro[0],registro[1],registro[2])
        html += '</ul>'
        html += '''
        <br><br>
        <p>Adicionar mais notas <a href="/notas">LINK</a></p>
        <br>
        <p>Para exluir a nota, passe como rota da URL o ID da Nota
        na URL "ip:8081/ExcluirNotas/id".</p>'''
        return html


###########################################################################
# ROTAS FLASK
###################
@enotas.route('/')
def principal():
    conexao = sqlite3.connect(banco_de_dados)
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM Notas')
    registros = cursor.fetchall()
    retorno = exibir_registros(registros)
    cursor.close()
    conexao.close()
    
    return render_template('principal.html', dados=retorno, okey=len(registros)), 200

@enotas.route('/notas')
def notas():
    i_titulo = '''
    <input type="text" name="titulo" />'''
    i_descricao = '''
    <input style="height:300px; width:300px;" type="text" name="descricao" 
    value="" />'''

    return render_template(
            'notas.html', 
            input_titulo=i_titulo,
            input_descricao=i_descricao
            ), 200

@enotas.route('/salvar_notas', methods=['POST'])
def salvar_notas():
    conexao = sqlite3.connect(banco_de_dados)
    cursor = conexao.cursor()
    cursor.execute('SELECT titulo FROM Notas')
    registros = cursor.fetchall()
    L_titulos = list()
    if len(registros) != 0:
        for registro in registros:
            L_titulos.append(registro[0])
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        if titulo not in L_titulos and descricao != '':
            cursor.execute('INSERT INTO Notas (titulo, descricao) VALUES (?,?)',
                    (titulo, descricao))
            conexao.commit()
            cursor.close()
            conexao.close()
            return redirect(url_for('principal'))
        elif titulo in L_titulos and descricao == '':
            # Retornar a descrição existente
            cursor.execute('SELECT descricao FROM Notas WHERE titulo = ?', (titulo,))
            registro_descricao = cursor.fetchall()
            i_titulo = '''
            <input type="text" name="titulo" value="{0}" />'''.format(titulo)
            i_descricao = '''
            <input style="height:300px; width:300px;" type="text" name="descricao" 
            value="{0}" />'''.format(registro_descricao[0][0])

            cursor.close()
            conexao.close()
            
            return render_template(
                    'notas.html',
                    input_titulo = i_titulo,
                    input_descricao = i_descricao
                    ), 200

        elif titulo in L_titulos and descricao != '':
            # UPDATE na Nota
            cursor.execute('UPDATE Notas SET descricao = ? WHERE titulo = ?', 
                    (descricao, titulo))
            conexao.commit()
            cursor.close()
            conexao.close()
            return redirect(url_for('principal'))
    else:
        cursor.close()
        conexao.close()
        redirect(url_for('principal'))

@enotas.route('/ExcluirNotas/<int:id_nota>')
def Excluir_Notas(id_nota=None):
    try:
        if id_nota != None:
            conexao = sqlite3.connect(banco_de_dados)
            comando = '''
            DELETE FROM Notas WHERE id = ?'''
            conexao.execute(comando, (id_nota,))
            conexao.commit()
            conexao.close()
    except:
        pass
    return redirect(url_for('principal'))

if __name__ == '__main__':
    conexao = sqlite3.connect(banco_de_dados)
    try:
        tabela = '''
        CREATE TABLE Notas (
        titulo text,
        descricao text,
        id integer primary key autoincrement
        )'''
        conexao.execute(tabela)
    except:
        pass
    conexao.close()
    enotas.run(host='0.0.0.0', port='8081', use_reloader=True)
