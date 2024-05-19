from configuracion.configuracion import get_db

def insertar_docente(docente):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO usuarios (id, nombre, correo, tipo_usuario) VALUES (%s, %s, %s, %s)',
                    (docente.user_id, docente.user_name, docente.user_email, docente.constante_docente))
        db.commit()
        cur.close()
    except Exception as e:
        print("Error al insertar datos:", e)