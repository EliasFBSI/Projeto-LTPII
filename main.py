from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'


# Configurações do banco de dados MySQL
db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'bancossa'
}

def validar_credenciais(cpf, senha):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Consultar o banco de dados para verificar se as credenciais são válidas
    sql = "SELECT * FROM cadastro WHERE cpf = %s AND senha = %s"
    val = (cpf, senha)
    cursor.execute(sql, val)

    # Verificar se existe um registro correspondente às credenciais fornecidas
    result = cursor.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']

        if validar_credenciais( cpf, senha):
            # Credenciais válidas, redirecionar para página de sucesso ou realizar ações adicionais
            return redirect(url_for('sidebar'))
        else:
            error_message = 'Usuário e/ou senha inválidos!'
            return render_template('index.html', error_message=error_message)


    return render_template('index.html')




@app.route('/sidebar')
def sidebar():
    return render_template('sidebar.html')



@app.route('/cadastrar')
def signup():
    return render_template('signup.html')


# Rota para registrar os dados do formulário
@app.route('/registrar', methods=['POST'])
def registrar():
    nome = request.form['nome']
    dn = request.form['dn']
    cargo = request.form['cargo']
    cpf = request.form['cpf']
    sexo = request.form['sexo']
    logradouro = request.form['logradouro']
    cep = request.form['cep']
    numero = request.form['numero']
    senha = request.form['senha']

    dn = datetime.strptime(dn, '%Y-%m-%d').date()



    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Insere os dados na tabela
    sql = "INSERT INTO cadastro (nome, dn, cargo, cpf, sexo, logradouro, cep, numero, senha) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (nome, dn, cargo, cpf, sexo, logradouro, cep, numero, senha)
    cursor.execute(sql, val)

    # Comita as alterações e fecha a conexão
    conn.commit()
    conn.close()
    return render_template('index.html')
    #return 'Dados registrados com sucesso!'


@app.route('/lista_usuarios')
def lista_usuarios():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cadastro')
    cadastro = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('users.html', users=cadastro)


@app.route('/editar/<string:cpf>', methods=['GET', 'POST'])
def editar_usuario(cpf):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()


    sql = "SELECT * FROM cadastro WHERE cpf = %s"
    cursor.execute(sql, (cpf,))
    user = cursor.fetchone()
    cursor.fetchall()
    cursor.close()
    conn.close()

    # Exibe o formulário de edição com os dados do usuário
    return render_template('editar.html', user=user)

@app.route('/atualizar/<string:cpf>', methods=['POST', 'GET'])
def atualizar_usuario(cpf):
    if request.method == 'POST':
        nome = request.form['nome']
        dn = request.form['dn']
        cargo = request.form['cargo']
        cpf = request.form['cpf']
        sexo = request.form['sexo']
        logradouro = request.form['logradouro']
        cep = request.form['cep']
        numero = request.form['numero']
        senha = request.form['senha']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = "UPDATE cadastro SET nome = %s, dn = %s, cargo = %s, sexo = %s, logradouro = %s, cep = %s, numero = %s, senha = %s WHERE cpf = %s"
        val = (nome, dn, cargo, sexo, logradouro, cep, numero, senha, cpf)
        cursor.execute(sql, val)
        cursor.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('lista_usuarios'))

    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta SQL para obter os dados do usuário pelo CPF
        sql = "SELECT * FROM cadastro WHERE cpf = %s"
        cursor.execute(sql, (cpf,))
        cadastro = cursor.fetchone()
        cursor.fetchall()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Renderiza o template HTML com os dados do usuário
        return render_template('users.html', cadastro=cadastro)


@app.route('/gerar_oficio', methods=['POST', 'GET'])
def gerar_oficio():
    if request.method == 'POST':
        assunto = request.form['assunto']
        destinatario = request.form['destinatario']
        remetente = request.form['remetente']
        data_emissao_str = request.form['data_emissao']
        data_emissao = datetime.strptime(data_emissao_str, '%Y-%m-%d')


        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consultar o último número de ofício gerado
        sql = "SELECT MAX(numero_oficio) FROM tabela_oficios"
        cursor.execute(sql)
        ultimo_numero = cursor.fetchone()[0]

        if ultimo_numero is None:
            novo_numero = '1'
        else:
            novo_numero = str(int(ultimo_numero) + 1)

        # Inserir os dados do novo ofício no banco de dados
        sql = "INSERT INTO tabela_oficios (numero_oficio, assunto, destinatario, remetente, data_emissao) VALUES (%s, %s, %s, %s, %s)"
        val = (novo_numero, assunto, destinatario, remetente, data_emissao)
        cursor.execute(sql, val)
        conn.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Renderizar o template generate.html com o número do ofício
        return render_template('generate.html', numero_oficio = (novo_numero))
    else:
        # Lógica para exibir o formulário HTML para o usuário preencher
        return render_template('generate.html')


@app.route('/search_oficios', methods=['GET', 'POST'])
def search_oficios():
    if request.method == 'POST':
        # Obter os dados do formulário de pesquisa
        termo_pesquisa = request.form['termo_pesquisa']

        # Executar a consulta SQL para buscar os ofícios no banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consultar os ofícios com base no termo de pesquisa
        sql = "SELECT * FROM tabela_oficios WHERE assunto LIKE %s OR destinatario LIKE %s OR remetente LIKE %s"
        val = (f'%{termo_pesquisa}%', f'%{termo_pesquisa}%', f'%{termo_pesquisa}%')
        cursor.execute(sql, val)
        oficios = cursor.fetchall()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        mensagem = request.args.get('mensagem')

        # Renderizar a página de resultados de pesquisa com os ofícios encontrados
        return render_template('gerados.html' , oficios=oficios , mensagem=mensagem )
    else:
        return render_template('gerados.html')


@app.route('/editar_oficio/<int:id>', methods=['GET', 'POST'])
def editar_oficio(id):
    if request.method == 'POST':
        # Obter os dados do formulário
        assunto = request.form['assunto']
        destinatario = request.form['destinatario']
        remetente = request.form['remetente']
        data_emissao = request.form['data_emissao']

        # Estabelecer a conexão com o banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Atualizar os dados do ofício no banco de dados
        sql = "UPDATE tabela_oficios SET assunto = %s, destinatario = %s, remetente = %s, data_emissao = %s WHERE id = %s"
        val = (assunto, destinatario, remetente, data_emissao, id)
        cursor.execute(sql, val)
        conn.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Redirecionar para a página de sucesso ou exibir uma mensagem informando a atualização
        return redirect(url_for('search_oficios'))
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consultar o ofício pelo ID
        sql = "SELECT * FROM tabela_oficios WHERE id = %s"
        val = (id,)
        cursor.execute(sql, val)
        oficio = cursor.fetchone()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Verificar se o ofício existe
        if oficio is None:
            # Lógica para lidar com o caso em que o ofício não foi encontrado
            return "Ofício não encontrado."

        # Renderizar o template 'editar.html' com os dados do ofício
        return render_template('editar_oficio.html', oficio=oficio)

@app.route('/excluir_oficio/<int:id>', methods=['POST'])
def excluir_oficio(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Excluir o ofício do banco de dados
    sql = "DELETE FROM tabela_oficios WHERE id = %s"
    val = (id,)
    cursor.execute(sql, val)
    conn.commit()


    cursor.close()
    conn.close()


    return redirect(url_for('search_oficios' , mensagem = "Dados excluidos com sucesso!"))




if __name__ == '__main__':
    app.run(debug=True)

