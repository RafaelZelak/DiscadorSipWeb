from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
from flask_cachebuster import CacheBuster
import json
import os
import re
import sip_module as sip
import pjsua2 as pj
from functools import wraps
import logging
import configparser
import hashlib
import time
import sqlite3
import base64
import database as db

#logger

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Inicialização das variaveis globais
ep = None
transport = None
account = None
call = None
sip_is_active = False

def obter_user_id():
    with open('id_salvo.json', 'r') as file:
        data = json.load(file)
        return data.get('id')

def conectar_bd():
    conn = sqlite3.connect('SipUserDB.db')
    return conn

def disable_logging(route):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.path == route:
                log.disabled = True
            else:
                log.disabled = False
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def recebendo_ligacao():
    caller = db.get_callers_db()
    return caller

def atualizar_estado_ligacao_db(estado):
    user_id = obter_user_id()

    conn = sqlite3.connect('SipUserDB.db')
    cursor = conn.cursor()

    # Verifica se o IDusuario já existe na tabela chamada
    cursor.execute('SELECT IDusuario FROM chamada WHERE IDusuario = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Se o usuário já existir, atualiza o estado
        cursor.execute('UPDATE chamada SET state = ? WHERE IDusuario = ?', (estado, user_id))
    else:
        # Se o usuário não existir, insere um novo registro
        cursor.execute('INSERT INTO chamada (IDusuario, state) VALUES (?, ?)', (user_id, estado))

    conn.commit()
    conn.close()
    
def verificar_estado_conexao():
    estado = db.get_state_db()
    if estado == 'conectada':
        return True
    elif estado == 'desconectada':
        return False
    else:
        raise ValueError("O arquivo tem um estado inválido.")

def clean_phone_number(phone_number):
    # Remove parênteses, hifens e espaços usando regex
    cleaned_number = re.sub(r'[()\-\s]', '', phone_number)
    return cleaned_number

def initialize_sip():
    global ep, transport, account
    try:
        ep, transport = sip.create_transport()
        print(f"\n\nEndpoint: {ep}, {transport}\n")
        account = sip.create_account(ep)
        print(f"\n\nAccount: {account}\n")
        if ep is None or transport is None:
            raise RuntimeError("Failed to initialize SIP endpoint")
        print("SIP endpoint initialized successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize SIP endpoint: {e}")

def clean_up():
    global ep, transport
    # Limpar recursos SIP
    try:
        if transport:
            transport = None
        if ep:
            ep.libDestroy()
            ep = None
    except Exception as e:
        print(f"Error cleaning up SIP resources: {e}")

# Função para registrar a thread atual no PJSIP
def register_thread():
    global ep
    if ep:
        ep.libRegisterThread("flask_thread")

# Inicialização do Flask
app = Flask(__name__)

@app.context_processor
def inject_timestamp():
    def timestamp():
        # Retorna o timestamp atual como uma string
        return str(int(time.time()))
    return dict(timestamp=timestamp)

@app.after_request
def add_header(response):
    # Para arquivos estáticos, define cabeçalhos de cache
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

cachebuster = CacheBuster(config={
    'extensions': ['.js', '.css'],
    'hash_size': 5
})
cachebuster.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def configPage():
    return render_template('config.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('.', 'service-worker.js')

@app.route('/trigger-sip', methods=['GET'])
def trigger_sip_route():
    global sip_is_active
    if sip_is_active == False:
        initialize_sip()
        sip_is_active = True
    else:
        pass
    
    return 'Sinal enviado com sucesso para trigger_sip!'

@app.route('/recuse_call', methods=['POST'])
def recuse_call():
    db.atualizar_recive_db('Recusada')
    db.atualizar_caller_db('')
    
    return jsonify({'result': True}), 200

@app.route('/make_call', methods=['POST'])
def make_call():
    global ep, transport, call
    data = request.json
    phone_number = data.get('phone_number')
    
    destination_number = clean_phone_number(phone_number)

    register_thread()
    caller = recebendo_ligacao()
    print(caller)
    if caller == "":
        if verificar_estado_conexao() == False:
            if destination_number:
                call = sip.make_call(account, destination_number) 
            else:
                print("Destination Number :: NULL")
                return jsonify({'success': False})
        else:
            prm = pj.CallOpParam()
            call.hangup(prm)
    else:
        db.atualizar_recive_db('Atendida')
        db.atualizar_caller_db('')
        
    return jsonify({'success': True})

@app.route('/recebendo_true', methods=['POST'])
def recebendo_true():
    global call, caller
    data = request.get_json()
    recebendo = data.get('recebendo')
    if recebendo:
        call = None
        caller = None

        # Salvando as alterações de volta para o arquivo
        db.atualizar_recive_db('Recusada')
        db.atualizar_caller_db('')
            
            
        return jsonify({'message': 'Recebendo é verdadeiro após 8 segundos!'}), 200
    return jsonify({'message': 'Recebendo não é verdadeiro.'}), 400

@app.route('/estado_conexao', methods=['GET'])
@disable_logging('/estado_conexao')
def estado_conexao():
    estado = verificar_estado_conexao()
    return jsonify({'conectado': estado})

@app.route('/recebendo_ligacao', methods=['GET'])
@disable_logging('/recebendo_ligacao')
def handle_recebendo_ligacao():
    global call
    caller = recebendo_ligacao()
    if caller != "":
        call = sip.incoming_call
        db.atualizar_state_db('conectada')
        return jsonify({"caller": caller})
    else:
        return '', 204
    
@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        ramal = request.form.get('ramal')
        sip_server = request.form.get('sip_server')
        senha = request.form.get('senha')

        # Criptografar a senha
        encoded_bytes = base64.b64encode(senha.encode('utf-8'))
        senha_criptografada = encoded_bytes.decode('utf-8')
        # Conectar ao banco de dados
        conn = conectar_bd()
        cursor = conn.cursor()

        insert_usuario_sql = '''
        INSERT INTO usuario (name, username, password, sipServer)
        VALUES (?, ?, ?, ?)
        '''

        try:
            cursor.execute(insert_usuario_sql, (nome, ramal, senha_criptografada, sip_server))
            conn.commit()
            conn.close()
            resposta = {'status': 'ok', 'message': 'Dados inseridos com sucesso no banco de dados.'}
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            resposta = {'status': 'erro', 'message': f'Erro ao inserir dados no banco de dados: {str(e)}'}

        return jsonify(resposta)

@app.route('/lista_usuarios')
def lista_usuarios():
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('SipUserDB.db')
    cursor = conn.cursor()

    # Executar a consulta para selecionar todos os registros
    cursor.execute('SELECT ID, username, name FROM usuario')

    # Recuperar todos os resultados da consulta
    rows = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    conn.close()

    # Converter os resultados para um formato JSON e retornar como resposta
    return jsonify(rows)

def salvar_id_em_arquivo(id):
    data = {'id': id}
    with open('id_salvo.json', 'w') as file:
        json.dump(data, file)

@app.route('/botao_clicado/<int:id>', methods=['POST'])
def botao_clicado(id):
    salvar_id_em_arquivo(id)
    return jsonify({'message': f'{id} salvo com sucesso'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/icons'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to start Flask app: {e}")
    finally:
        clean_up()