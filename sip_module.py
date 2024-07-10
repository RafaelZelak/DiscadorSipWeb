
import pjsua2 as pj
import app
import socket
import datetime
import threading
import tkinter as tk
import time
import re
import configparser
import sqlite3
import base64
import json
import database as db


# Variável global para o endpoint
ep = None
call_onoff = False
incoming_call = None
call_number = None
answer_call = False
caller_number = None
root = None 


def treat_caller_number():
    global caller_number, caller_number_treated
    # Remove everything between < > including the symbols and also the double quotes
    cleaned_number = re.sub(r'<[^>]*>', '', caller_number).replace('"', '').strip()
    
    # Check if it is a phone number or a name
    if cleaned_number.isdigit():  # Check if the cleaned_number is a digit (phone number)
        if len(cleaned_number) == 10:  # Fixed line phone number
            caller_number_treated = f'({cleaned_number[:2]}){cleaned_number[2:6]}-{cleaned_number[6:]}'
        elif len(cleaned_number) == 11:  # Mobile phone number
            caller_number_treated = f'({cleaned_number[:2]}){cleaned_number[2:7]}-{cleaned_number[7:]}'
        else:
            caller_number_treated = cleaned_number  # Return the number as is if it does not match expected lengths
    else:  # It's a name
        caller_number_treated = cleaned_number
    
    db.atualizar_caller_db(caller_number_treated)
        
def wait_for_user_input():
    global caller_number, answer_call, caller_number_treated

    treat_caller_number()
    print("Chamada Recebida:")
    print(caller_number_treated)

    while True:
        
        conteudo = db.get_recive_db
        
        if conteudo == 'Atendida':
            answer_call = True
            atualizar_estado_ligacao('desconectada')
            db.atualizar_recive_db('')
            break
        
        elif conteudo == 'Recusada':
            answer_call = False
            atualizar_estado_ligacao('conectada')
            db.atualizar_recive_db('')
            break
        else:
            time.sleep(1)
            continue

    
# Função para ler configurações do arquivo
def ler_configuracoes_do_arquivo(arquivo):
    configuracoes = {}
    with open(arquivo, 'r') as file:
        for line in file:
            line = line.strip()
            if ': ' in line:
                key, value = line.split(': ', 1)
                configuracoes[key.strip()] = value.strip()
            else:
                print(f"Linha ignorada por estar malformada: {line}")
    return configuracoes

# Lendo as configurações do arquivo
import sqlite3

# Função para ler configurações da base de dados SQLite
def ler_configuracoes_do_banco():
    # Conectar ao banco de dados
    conn = sqlite3.connect('SipUserDB.db')
    cursor = conn.cursor()

    # Solicitar ID do usuário
    with open('id_salvo.json', 'r') as file:
        data = json.load(file)
        user_id = data.get('id')
    # Executar consulta SQL para recuperar as configurações
    cursor.execute('SELECT SipServer, username, password FROM usuario WHERE ID = ?', (user_id,))

    # Recuperar os resultados da consulta
    row = cursor.fetchone()
    if row:
        SIP_SERVER = row[0]
        USERNAME = row[1]
        EXTENSION = row[1]  # Ou outro campo dependendo da sua lógica de uso
        decoded_bytes = base64.b64decode(row[2].encode('utf-8'))
        PASSWORD = decoded_bytes.decode('utf-8')
    else:
        print(f"Erro: Não foi possível encontrar configurações para o usuário com ID {user_id}.")
        SIP_SERVER = None
        USERNAME = None
        EXTENSION = None
        PASSWORD = None

    # Fechar conexão com o banco de dados
    conn.close()

    return SIP_SERVER, USERNAME, EXTENSION, PASSWORD

# Exemplo de utilização
SIP_SERVER, USERNAME, EXTENSION, PASSWORD = ler_configuracoes_do_banco()

if not SIP_SERVER:
    exit(1)


# Lista de codecs a serem utilizados
CODECS = ["PCMA/8000"]

# Função para atualizar o estado da ligação em um arquivo
import configparser

def obter_user_id():
    with open('id_salvo.json', 'r') as file:
        data = json.load(file)
        return data.get('id')

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

# Função para receber ligação e atualizar estado no banco de dados SQLite
def rebeber_ligacao(estado):
    user_id = obter_user_id()

    conn = sqlite3.connect('SipUserDB.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE chamada SET state = ? WHERE IDusuario = ?', (estado, user_id))
    conn.commit()

    conn.close()

# Função para atender ligação e atualizar estado no banco de dados SQLite
def atender_ligacao(estado):
    user_id = obter_user_id()

    conn = sqlite3.connect('SipUserDB.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE chamada SET state = ? WHERE IDusuario = ?', (estado, user_id))
    conn.commit()

    conn.close()

def atualizar_estado_ligacao(estado):
    db.atualizar_state_db(estado)

def rebeber_ligação(estado):
    db.atualizar_state_db(estado)

def atender_ligação(estado):
    db.atualizar_state_db(estado)

         
# Classe para representar uma chamada
class MyCall(pj.Call):
    def __init__(self, account, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, account, call_id)
    
    def onCallState(self, prm):
        global call_info, call_number, answer_call
        call_info = self.getInfo()
        print(f"Call state changed to {call_info.stateText} for call ID: {self.getId()}")
        if call_info.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            print("Call disconnected")
            
            db.atualizar_caller_db('')
                
            answer_call = False
            atualizar_estado_ligacao('desconectada')
            atualizar_estado_ligacao_db('desconectada')
            global incoming_call
            global call_number
            incoming_call = None
            now = datetime.datetime.now()
            datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")
            with open('call.txt', 'r+') as file:
                lines = file.readlines()
                if len(lines) >= 4:
                    lines[3] = datetime_string + "\n"
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
                else:
                    lines.extend(['\n'] * (4 - len(lines)))  # Adiciona linhas vazias se não houver 5 linhas
                    lines[3] = datetime_string + "\n"
                    file.seek(0)
                    file.writelines(lines)
                if len(lines) >= 5:
                    lines[4] = "Encerrado" + "\n"
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
                else:
                    lines.extend(['\n'] * (5 - len(lines)))  # Adiciona linhas vazias se não houver 5 linhas
                    lines[4] = "Encerrado" + "\n"
                    file.seek(0)
                    file.writelines(lines)

        elif call_info.state == pj.PJSIP_INV_STATE_CONFIRMED:
            print("Call connected")
            atualizar_estado_ligacao('conectada')
            atualizar_estado_ligacao_db('conectada')
            print(f"Call number: {call_number}")  # Imprimir o número da chamada conectada
            now = datetime.datetime.now()
            datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")
            with open('call.txt', 'r+') as file:
                lines = file.readlines()
                if len(lines) >= 3:
                    lines[2] = datetime_string + "\n"
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
                else:
                    lines.extend(['\n'] * (3 - len(lines)))  # Adiciona linhas vazias se não houver 5 linhas
                    lines[2] = datetime_string + "\n"
                    file.seek(0)
                    file.writelines(lines)
                if len(lines) >= 1:
                    lines[0] = "True" + "\n"
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
                else:
                    lines.extend(['\n'] * (1 - len(lines)))  # Adiciona linhas vazias se não houver 5 linhas
                    lines[0] = "True" + "\n"
                    file.seek(0)
                    file.writelines(lines)
                if len(lines) >= 5:
                    lines[4] = "Andamento" + "\n"
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
                else:
                    lines.extend(['\n'] * (5 - len(lines)))  # Adiciona linhas vazias se não houver 5 linhas
                    lines[4] = "Andamento" + "\n"
                    file.seek(0)
                    file.writelines(lines)
            
    def onCallMediaState(self, prm):
        global call_onoff
        call_info = self.getInfo()
        for media_info in call_info.media:
            if media_info.type == pj.PJMEDIA_TYPE_AUDIO:
                if media_info.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print("Call media active")
                    call_onoff = True
                    # Corrigindo a chamada para getAudioMedia() com índice 0
                    media = self.getAudioMedia(0)
                    if media:
                        # Usando a variável global ep
                        media.startTransmit(ep.audDevManager().getCaptureDevMedia())
                        ep.audDevManager().getPlaybackDevMedia().startTransmit(media)
                elif media_info.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD:
                    print("Remote hold")
                    self.answer()
                elif media_info.status == pj.PJSUA_CALL_MEDIA_ERROR:
                    print("Error in call media")
                    self.hangup()

    def answer(self):
        prm = pj.CallOpParam()
        prm.statusCode = pj.PJSIP_SC_OK
        super(MyCall, self).answer(prm)

# Classe para representar uma conta
class MyAccount(pj.Account):
    def __init__(self):
        super().__init__()
    
    def onRegState(self, prm):
        print("Registration status: ", prm.code)
        if prm.code == 200:
            print("Registrado com sucesso!")
            atualizar_login_status(1)
        else:
            print("Falha no registro.")
            print(f"Código de erro: {prm.code}")
            print(f"Razão da falha: {prm.reason}")
            atualizar_login_status(0)
            
    def onIncomingCall(self, prm):
        global incoming_call, call_number, answer_call, caller_number
        call_id = prm.callId
        incoming_call = MyCall(self, call_id)
        answer_call = None
        call_info = incoming_call.getInfo()
        caller_number = call_info.remoteUri
        print(f"Incoming call from: {caller_number}")
        # Use um thread para aguardar a entrada do usuário sem bloquear o loop principal
        threading.Thread(target=wait_for_user_input).start()

        # Bloquear até que o usuário tome uma decisão, mas com sleep para não consumir CPU excessiva
        while answer_call is None:
            time.sleep(0.1)

        if answer_call:
            incoming_call.answer()
        else:
            prm = pj.CallOpParam()
            incoming_call.hangup(prm)




def atualizar_login_status(status):
    with open('config.cfg', 'r') as file:
        lines = file.readlines()
    if len(lines) < 6:
        lines.extend(['\n'] * (6 - len(lines)))
    lines[5] = f'login: {status}\n'
    with open('config.cfg', 'w') as file:
        file.writelines(lines)


incoming_call = None

# Função para verificar se uma porta está em uso
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Função para encontrar uma porta disponível
def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

# Função para criar transporte
def create_transport():
    global ep
    ep = pj.Endpoint()
    ep.libCreate()
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 0

    try:
        ep.libInit(ep_cfg)
    except pj.Error as e:
        print(f"Erro na inicialização do endpoint: {e}")
        return None, None

    transport_cfg = pj.TransportConfig()
    transport_cfg.port = find_available_port(5060)

    try:
        transport = ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, transport_cfg)
        ep.libStart()
    except pj.Error as e:
        print(f"Erro ao criar transporte: {e}")
        return None, None

    return ep, transport

# Função para criar uma conta
def create_account(ep):
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = f"sip:{EXTENSION}@{SIP_SERVER}"
    acc_cfg.regConfig.registrarUri = f"sip:{SIP_SERVER}"
    acc_cfg.sipConfig.authCreds.append(pj.AuthCredInfo("digest", "*", USERNAME, 0, PASSWORD))

    # Configurando codecs
    acc_cfg.codecIds = pj.StringVector()
    for codec in CODECS:
        acc_cfg.codecIds.push_back(codec)

    try:
        account = MyAccount()
        account.create(acc_cfg)
    except pj.Error as e:
        print(f"Erro ao criar a conta: {e}")
        return None

    return account

# Função principal para organizar a execução do código
def main():
    global ep
    ep, transport = create_transport()
    if not ep or not transport:
        print("Erro ao criar transporte. Verifique as configurações.")
        return

    account = create_account(ep)
    if not account:
        print("Erro ao criar a conta. Verifique as configurações.")
        return

    destination_number = configuracoes.get('Destination Number')
    if destination_number:
        threading.Thread(target=make_call, args=(account, destination_number)).start()
        print(f"Chamada para {destination_number} iniciada.")
    else:
        print("Número de destino não especificado nas configurações.")

    try:
        while True:
            time.sleep(1)  # Reduz a carga da CPU
    except KeyboardInterrupt:
        print("Finalizando...")

    account.shutdown()
    ep.libDestroy()
    atualizar_estado_ligacao('desconectada')    
    

# Função para fazer uma chamada
def make_call(account, destination_number):
    global call_number
    if not account:
        print("Conta não está registrada. Não é possível fazer chamada.")
        return
    destination = f"sip:{destination_number}@{SIP_SERVER}"
    call = MyCall(account)
    prm = pj.CallOpParam()
    prm.opt.audioCount = 1
    prm.opt.videoCount = 0
    call.makeCall(destination, prm)
    atualizar_estado_ligacao('conectada')
    print(f"Chamada para {destination_number} iniciada.")
    return call

def clear_call_cache():
    global incoming_call, call_number, caller_number, answer_call, call_info, call_onoff
    incoming_call = None
    call_number = None
    caller_number = None
    answer_call = False
    call_info = None
    call_onoff = False
    print("Cache de chamadas limpo.")

# Chamar a função principal
if __name__ == "__main__":
    main()
    