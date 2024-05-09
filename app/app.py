import os
import re
import pathlib
import requests
from flask import Flask, make_response, redirect, render_template, session, abort, request
import pymysql
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

app = Flask(__name__)
app.secret_key = "leo"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'estructuras'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

if mysql is not None:
    print("Conexión exitosa")
else:
    print("Error al conectar")

constante_estudiante = 'ESTUDIANTE'
constante_docente = 'DOCENTE'

GOOGLE_CLIENT_ID = "425381355940-a7s2hq5bup3vo9v3sjr3f36u18lsmbcl.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()

    return wrapper

@app.route('/')
def index():
    user_token = request.cookies.get("user_token")
    user_type = request.cookies.get("user_type")
    if user_token:
        session["google_id"] = user_token
        if user_type == 'DOCENTE':
            return render_template('indexDocente.html')
        else:
            return render_template('index.html')
    else:
     return render_template('login.html')

@app.route('/login')
def login():
    nonce = os.urandom(16).hex()
    authorization_url, state = flow.authorization_url(prompt="select_account", nonce=nonce)
    session["state"] = state
    session["nonce"] = nonce 
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    token_request = google.auth.transport.requests.Request(session=requests.Session())
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    user_id = id_info.get('sub')
    user_name = id_info.get('name')
    user_email = id_info.get('email')

    #if not re.search(r'@elpoli.edu.co', user_email):
        #return render_template('mensaje_error.html')

    cur2 = mysql.cursor()
    cur2.execute('SELECT nombre,correo,tipo_usuario FROM usuarios WHERE id = %s', (user_id,))
    result = cur2.fetchone()
    cur2.close()

    if result is not None:
        if result[2] == constante_docente:
            response = make_response(render_template('indexDocente.html'))
            response.set_cookie('user_token', user_id, max_age=3600)
            response.set_cookie('user_type', result[2], max_age=3600)
        else:
            insertar_reporte_usuario(result[0],result[1])
            response = make_response(render_template('index.html'))
            response.set_cookie('user_token', user_id, max_age=3600)
            response.set_cookie('user_type', result[2], max_age=3600)

        return response
    else:
        
        if re.search(r'\d', user_email):
            insertar_reporte_usuario(user_name,user_email)
            cur = mysql.cursor()
            cur.execute('INSERT INTO usuarios (id, nombre, correo, tipo_usuario) VALUES (%s, %s, %s, %s)', (user_id, user_name, user_email, constante_estudiante))
            mysql.commit()
            cur.close()
            response = make_response(redirect("/"))
            response.set_cookie("user_token", user_id, max_age=3600)
            response.set_cookie('user_type', constante_estudiante, max_age=3600)
            #return response

        else:
            cur = mysql.cursor()
            cur.execute('INSERT INTO usuarios (id, nombre, correo, tipo_usuario) VALUES (%s, %s, %s, %s)', (user_id, user_name, user_email, constante_docente))
            mysql.commit()
            cur.close()
            response = make_response(redirect("/"))
            response.set_cookie("user_token", user_id, max_age=3600)
            response.set_cookie('user_type', constante_docente, max_age=3600)
            #return response
    return response

def insertar_reporte_usuario(user_name, user_email):
    try:
        cur = mysql.cursor()
        cur.execute('INSERT INTO registro_ingresos (nombre, correo) VALUES (%s, %s)', (user_name, user_email))
        mysql.commit()
        cur.close()
    except Exception as e:
        print("Error al insertar datos:", e)

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect("/"))
    response.delete_cookie("oauthlib_state")
    response.delete_cookie("session")
    response.delete_cookie("user_token")

    return response

@app.route('/seccion1.html')
def seccion1():
    return render_template('./secciones/seccion1.html')

@app.route('/seccion2.html')
def seccion2():
    return render_template('./secciones/seccion2.html')

@app.route('/seccion3.html')
def seccion3():
    return render_template('./secciones/seccion3.html')

@app.route('/seccion4.html')
def seccion4():
    return render_template('./secciones/seccion4.html')

@app.route('/seccion5.html')
def seccion5():
    return render_template('./secciones/seccion5.html')

@app.route('/seccion6.html')
def seccion6():
    return render_template('./secciones/seccion6.html')

@app.route('/seccion7.html')
def seccion7():
    return render_template('./secciones/seccion7.html')

@app.route('/seccion8.html')
def seccion8():
    return render_template('./secciones/seccion8.html')

@app.route('/generar_reporte')
def generar_reporte():
    cur = mysql.cursor()
    cur.execute('SELECT * FROM registro_ingresos')
    data = cur.fetchall()
    cur.close()
    return render_template('./secciones/reporte.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)