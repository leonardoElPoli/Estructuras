from configuracion.configuracion import get_db
from modelo.usuario import *

def insertar_usuario(usuario):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO usuarios (id, nombre, correo, tipo_usuario) VALUES (%s, %s, %s, %s)',
                     (usuario.user_id, usuario.user_name, usuario.user_email, usuario.constante_estudiante))
        db.commit()
        cur.close()
    except Exception as e:
        print("Error al insertar datos:", e)

def validar_usuario_existente(user_id):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT nombre,correo,tipo_usuario FROM usuarios WHERE id = %s', (user_id,))
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        print("Error al validar usuario:", e)
        return 
    