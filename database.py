import json
import sqlite3

def obter_user_id():
    with open('id_salvo.json', 'r') as file:
        data = json.load(file)
        return data.get('id')

def atualizar_state_db(estado):
    user_id = obter_user_id()

    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT IDusuario FROM chamada WHERE IDusuario = ?', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.execute('UPDATE chamada SET state = ? WHERE IDusuario = ?', (estado, user_id))
        else:
            cursor.execute('INSERT INTO chamada (IDusuario, state) VALUES (?, ?)', (user_id, estado))
        
        conn.commit()

def atualizar_caller_db(estado):
    user_id = obter_user_id()

    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT IDusuario FROM chamada WHERE IDusuario = ?', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.execute('UPDATE chamada SET caller = ? WHERE IDusuario = ?', (estado, user_id))
        else:
            cursor.execute('INSERT INTO chamada (IDusuario, caller) VALUES (?, ?)', (user_id, estado))
        
        conn.commit()

def atualizar_recive_db(estado):
    user_id = obter_user_id()

    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT IDusuario FROM chamada WHERE IDusuario = ?', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.execute('UPDATE chamada SET recive = ? WHERE IDusuario = ?', (estado, user_id))
        else:
            cursor.execute('INSERT INTO chamada (IDusuario, recive) VALUES (?, ?)', (user_id, estado))
        
        conn.commit()

def get_state_db():
    user_id = obter_user_id()
    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chamada.state FROM chamada INNER JOIN usuario ON chamada.IDusuario = usuario.ID WHERE usuario.ID = ?", (user_id,))
        states = cursor.fetchall()
        if states:
            return states[0][0].strip()
        else:
            return None


def get_callers_db():
    user_id = obter_user_id()
    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chamada.caller FROM chamada INNER JOIN usuario ON chamada.IDusuario = usuario.ID WHERE usuario.ID = ?", (user_id,))
        callers = cursor.fetchall()
        if callers and callers[0][0] is not None:
            return callers[0][0].strip()
        else:
            return ''

def get_recive_db():
    user_id = obter_user_id()
    with sqlite3.connect('SipUserDB.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chamada.recive FROM chamada INNER JOIN usuario ON chamada.IDusuario = usuario.ID WHERE usuario.ID = ?", (user_id,))
        recivers = cursor.fetchall()
        if recivers:
            return recivers[0][0].strip()
        else:
            return None
        