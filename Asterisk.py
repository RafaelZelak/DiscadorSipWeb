from cryptography.fernet import Fernet
import paramiko
import re
import warnings

def suppress_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_key():
    # Carregue a chave do arquivo
    return open('secret.key', 'rb').read()

def decrypt_password():
    # Carregue a chave e a senha criptografada
    key = load_key()
    cipher_suite = Fernet(key)
    with open('encrypted_password.bin', 'rb') as file:
        encrypted_password = file.read()
    return cipher_suite.decrypt(encrypted_password).decode()

hostname = '192.168.15.252'
port = 22
username = 'root'
password = decrypt_password()

def get_ramal_password(ramal):
    suppress_warnings()
    senha_ramal = None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)

        stdin, stdout, stderr = client.exec_command('cat /etc/asterisk/sip_additional.conf')
        output = stdout.read().decode()

        pattern = rf'\[{ramal}\]\s+.*?secret=(\S+)'
        match = re.search(pattern, output, re.DOTALL)

        if match:
            senha_ramal = match.group(1)

    finally:
        client.close()

    return senha_ramal
