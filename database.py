import sqlite3

# Conectar ao banco de dados (será criado se não existir)
conn = sqlite3.connect('SipUserDB.db')

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

# Comando SQL para criar a tabela usuario
create_usuario_table_sql = '''
CREATE TABLE IF NOT EXISTS usuario (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    ramal TEXT,
    sipServer TEXT
);
'''

# Comando SQL para criar a tabela chamada
create_chamada_table_sql = '''
CREATE TABLE IF NOT EXISTS chamada (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    IDusuario INTEGER,
    state TEXT,
    recive TEXT,
    caller TEXT,
    FOREIGN KEY (IDusuario) REFERENCES usuario (ID)
);
'''

# Executar os comandos SQL para criar as tabelas
cursor.execute(create_usuario_table_sql)
cursor.execute(create_chamada_table_sql)

# Comando SQL para adicionar os novos campos na tabela usuario
alter_table_sql = '''
ALTER TABLE usuario
ADD COLUMN name TEXT,
ADD COLUMN ramal TEXT,
ADD COLUMN sipServer TEXT,
ADD COLUMN senha TEXT;
'''

# Executar o comando SQL de alteração da tabela usuario
cursor.execute(alter_table_sql)

# Confirmar as alterações
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()

print("Banco de dados criado com sucesso.")
