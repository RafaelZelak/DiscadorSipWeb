import base64

# Função para criptografar a senha antes de salvar no banco de dados
def encrypt_password(password):
    encoded_bytes = base64.b64encode(password.encode('utf-8'))
    encrypted_password = encoded_bytes.decode('utf-8')
    return encrypted_password

# Função para descriptografar a senha antes de usar no SIP
def decrypt_password(encrypted_password):
    decoded_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
    original_password = decoded_bytes.decode('utf-8')
    return original_password

# Exemplo de uso:
password = "a91a27aac3f148a84696d2de6049aea1"

# Criptografar a senha antes de salvar no banco de dados
encrypted = encrypt_password(password)
print("Senha criptografada:", encrypted)

# Simular o processo de descriptografar a senha antes de enviar para o SIP
decrypted = decrypt_password(encrypted)
print("Senha descriptografada:", decrypted)