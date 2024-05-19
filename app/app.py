import os
import re
import pathlib
import requests
from flask import Flask, make_response, redirect, render_template, session, abort, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from configuracion.configuracion import get_db, init_app
from repositorio.reporte import *
from repositorio.usuario import *
from repositorio.docente import *
from modelo.usuario import *
from modelo.docente import *
from controlador.reporteControlador import controladorReporte
from controlador.vigaControlador import controladorViga
from controlador.seccionControlador import controladorSeccion

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'vista')
app = Flask(__name__, template_folder='vista')
app.secret_key = "leo"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'estructuras'

init_app(app)
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
        if user_type == constante_docente:
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

    if not re.search(r'@elpoli.edu.co', user_email):
        return render_template('mensaje_error.html')

    result = validar_usuario_existente(user_id)

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
            insertar_usuario(Usuario(user_id, user_name, user_email))
            response = make_response(redirect("/"))
            response.set_cookie("user_token", user_id, max_age=3600)
            response.set_cookie('user_type', constante_estudiante, max_age=3600)
        else:
            insertar_docente(Docente(user_id, user_name, user_email))
            response = make_response(redirect("/"))
            response.set_cookie("user_token", user_id, max_age=3600)
            response.set_cookie('user_type', constante_docente, max_age=3600)
    return response

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect("/"))
    response.delete_cookie("oauthlib_state")
    response.delete_cookie("session")
    response.delete_cookie("user_token")

    return response

controladorSeccion(app)
controladorViga(app)
controladorReporte(app,generar_reporte_ingreso)

if __name__ == '__main__':
    app.run(debug=True, port=5000)