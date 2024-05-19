from configuracion.configuracion import get_db

def insertar_reporte_usuario(user_name, user_email):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO registro_ingresos (nombre, correo) VALUES (%s, %s)', (user_name, user_email))
        db.commit()
        cur.close()
    except Exception as e:
        print("Error al insertar datos:", e)

def generar_reporte_ingreso():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM registro_ingresos ORDER BY fecha_ingreso DESC')
    data = cur.fetchall()
    cur.close()
    return data