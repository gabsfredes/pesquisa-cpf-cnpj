import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import multiprocessing
import os
import sys
import time
import socket
import secrets
import json
from waitress import serve

from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_cors import CORS

app = Flask(__name__)


CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)
jwt = JWTManager(app)

db = SQLAlchemy()

search_CPFdb_engine = None
search_CNPJdb_engine = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

def get_request_payload():
    if request.is_json:
        try:
            return request.get_json()
        except Exception as e:
            print(f"Erro ao analisar JSON: {e}")
            pass

    if request.form:
        return request.form.to_dict()

    data = request.get_data(as_text=True)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Erro ao analisar dados brutos como JSON: {e}")
            pass

    return {}

@app.route("/ping")
def ping():
    return {"status": "ok"}

@app.route("/validate_token", methods=["GET"])
@jwt_required()
def validate_token():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Token válido. Usuário: {current_user}"}), 200

@app.route("/register", methods=["POST"])
def register():
    data = get_request_payload()
    username = data.get("username", None)
    password = data.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Username e password são obrigatórios."}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "Usuário já existe."}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": f"Usuário {username} criado com sucesso."}), 201

@app.route("/login", methods=["POST"])
def login():
    data = get_request_payload()
    username = data.get("username", None)
    password = data.get("password", None)

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Usuário ou senha inválidos."}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token)

@app.route("/search_CPFdb", methods=["GET"])
@jwt_required()
def search_CPFdb():
    global search_CPFdb_engine
    global search_CNPJdb_engine

    if search_CPFdb_engine is None:
        return jsonify({"msg": "Banco de dados de CPF não configurado ou não inicializado."}), 500

    if search_CNPJdb_engine is None:
        return jsonify({"msg": "Banco de dados de CNPJ não configurado ou não inicializado."}), 500

    cpf_value = request.args.get("cpf", None)

    if not cpf_value:
        return jsonify({"msg": "Parâmetro 'cpf' é obrigatório."}), 400

    cpf_name = None
    result_data = {}

    try:
        with search_CPFdb_engine.connect() as connection:
            query_sql = text("SELECT nome, cpf, sexo, nasc FROM cpf WHERE cpf = :search_value")
            cpf_result = connection.execute(query_sql, {"search_value": cpf_value})

            cpf_row = cpf_result.fetchone()
            if cpf_row:
                result_data = {
                    "nome": cpf_row.nome,
                    "cpf": cpf_row.cpf,
                    "sexo": cpf_row.sexo,
                    "nasc": cpf_row.nasc,
                    "empresas_associadas": []
                }
                cpf_name = cpf_row.nome
            else:
                return jsonify({"msg": "CPF não encontrado."}), 200

    except Exception as e:
        print(f"Erro ao consultar Banco de Dados de CPF: {e}")
        return jsonify({"msg": f"Erro interno ao consultar Banco de Dados de CPF: {str(e)}"}), 500

    if cpf_name:
        try:
            with search_CNPJdb_engine.connect() as connection:
                query_sql = text("""
                    SELECT s.cnpj, s.cnpj_basico, s.data_entrada_sociedade, qs.descricao AS qualificacao_socio_descricao
                    FROM socios s
                    JOIN qualificacao_socio qs ON s.qualificacao_socio = qs.codigo
                    WHERE s.nome_socio = :search_value LIMIT 100
                """)
                cnpj_results = connection.execute(query_sql, {"search_value": cpf_name})

                for row in cnpj_results:
                    cnpj_object = {
                        "cnpj": row.cnpj,
                        "qualificacao_socio": row.qualificacao_socio_descricao,
                        "data_entrada_sociedade": row.data_entrada_sociedade
                    }

                    company_query_sql = text("""
                        SELECT e.razao_social, e.capital_social, nj.descricao AS natureza_juridica_descricao
                        FROM empresas e
                        JOIN natureza_juridica nj ON e.natureza_juridica = nj.codigo
                        WHERE e.cnpj_basico = :cnpj_basico
                    """)
                    company_result = connection.execute(company_query_sql, {"cnpj_basico": row.cnpj_basico}).fetchone()

                    if company_result:
                        cnpj_object["razao_social"] = company_result.razao_social
                        cnpj_object["capital_social"] = company_result.capital_social
                        cnpj_object["natureza_juridica"] = company_result.natureza_juridica_descricao
                    else:
                        cnpj_object["razao_social"] = "Nome da empresa não encontrado"
                        cnpj_object["capital_social"] = "Capital social não encontrado"
                        cnpj_object["natureza_juridica"] = "Natureza juridica não encontrado"

                    result_data["empresas_associadas"].append(cnpj_object)

        except Exception as e:
            print(f"Erro ao consultar Banco de Dados de CNPJ ou Empresas: {e}")
            return jsonify({"msg": f"Erro interno ao consultar Banco de Dados de CNPJ ou Empresas: {str(e)}"}), 500

    print(f"[MAIN] PID do processo principal: {os.getpid()}")

    return jsonify({"results": [result_data]}), 200

@app.route("/search_Name", methods=["GET"])
@jwt_required()
def search_CPFdb_by_name():
    global search_CPFdb_engine
    global search_CNPJdb_engine

    if search_CPFdb_engine is None:
        return jsonify({"msg": "Banco de dados de CPF não configurado ou não inicializado."}), 500

    if search_CNPJdb_engine is None:
        return jsonify({"msg": "Banco de dados de CNPJ não configurado ou não inicializado."}), 500

    name_value = request.args.get("name", None)

    if not name_value:
        return jsonify({"msg": "Parâmetro 'name' é obrigatório."}), 400

    search_name = name_value.replace(" ", "%") + "%"

    all_results = []

    try:
        with search_CPFdb_engine.connect() as connection:
            query_sql = text("SELECT nome, cpf, sexo, nasc FROM cpf WHERE nome LIKE :search_value LIMIT 100")
            cpf_results = connection.execute(query_sql, {"search_value": search_name})

            for cpf_row in cpf_results:
                result_data = {
                    "nome": cpf_row.nome,
                    "cpf": cpf_row.cpf,
                    "sexo": cpf_row.sexo,
                    "nasc": cpf_row.nasc,
                    "empresas_associadas": []
                }
                cpf_name_for_cnpj_search = cpf_row.nome

                if cpf_name_for_cnpj_search:
                    try:
                        with search_CNPJdb_engine.connect() as cnpj_connection:
                            query_socios_sql = text("""
                                SELECT s.cnpj, s.cnpj_basico, s.data_entrada_sociedade, qs.descricao AS qualificacao_socio_descricao
                                FROM socios s
                                JOIN qualificacao_socio qs ON s.qualificacao_socio = qs.codigo
                                WHERE s.nome_socio = :search_value LIMIT 100
                            """)
                            cnpj_socios_results = cnpj_connection.execute(query_socios_sql, {"search_value": cpf_name_for_cnpj_search})

                            for row in cnpj_socios_results:
                                cnpj_object = {
                                    "cnpj": row.cnpj,
                                    "qualificacao_socio": row.qualificacao_socio_descricao,
                                    "data_entrada_sociedade": row.data_entrada_sociedade
                                }

                                company_query_sql = text("""
                                    SELECT e.razao_social, e.capital_social, nj.descricao AS natureza_juridica_descricao
                                    FROM empresas e
                                    JOIN natureza_juridica nj ON e.natureza_juridica = nj.codigo
                                    WHERE e.cnpj_basico = :cnpj_basico
                                """)
                                company_result = cnpj_connection.execute(company_query_sql, {"cnpj_basico": row.cnpj_basico}).fetchone()

                                if company_result:
                                    cnpj_object["razao_social"] = company_result.razao_social
                                    cnpj_object["capital_social"] = company_result.capital_social
                                    cnpj_object["natureza_juridica"] = company_result.natureza_juridica_descricao
                                else:
                                    cnpj_object["razao_social"] = "Nome da empresa não encontrado"
                                    cnpj_object["capital_social"] = "Capital social não encontrado"
                                    cnpj_object["natureza_juridica"] = "Natureza jurídica não encontrada"

                                result_data["empresas_associadas"].append(cnpj_object)

                    except Exception as e:
                        print(f"Erro ao consultar Banco de Dados de CNPJ ou Empresas para o nome '{cpf_name_for_cnpj_search}': {e}")
                        pass 

                all_results.append(result_data)

            if not all_results:
                return jsonify({"msg": "Nenhum CPF encontrado com o nome fornecido."}), 200

    except Exception as e:
        print(f"Erro ao consultar Banco de Dados de CPF: {e}")
        return jsonify({"msg": f"Erro interno ao consultar Banco de Dados de CPF: {str(e)}"}), 500

    print(f"[MAIN] PID do processo principal: {os.getpid()}")

    return jsonify({"results": all_results}), 200

@app.route("/search_CNPJdb", methods=["GET"])
@jwt_required()
def search_CNPJdb():
    global search_CPFdb_engine
    global search_CNPJdb_engine

    if search_CPFdb_engine is None:
        return jsonify({"msg": "Banco de dados de CPF não configurado ou não inicializado."}), 500

    if search_CNPJdb_engine is None:
        return jsonify({"msg": "Banco de dados de CNPJ não configurado ou não inicializado."}), 500

    cnpj_value = request.args.get("cnpj", None)

    if not cnpj_value:
        return jsonify({"msg": "Parâmetro 'cnpj' é obrigatório."}), 400

    if len(cnpj_value) >= 8:
        cnpj_basico = cnpj_value[:8]
    else:
        return jsonify({"msg": "CNPJ inválido. Deve ter pelo menos 8 dígitos."}), 400

    company_data = {}

    try:
        with search_CNPJdb_engine.connect() as connection:
            query_company_sql = text("""
                    SELECT e.razao_social,
                    e.capital_social,
                    e.porte_empresa,
                    e.ente_federativo_responsavel,
                    nj.descricao AS natureza_juridica_descricao
                    FROM empresas e JOIN natureza_juridica nj ON e.natureza_juridica = nj.codigo
                    WHERE e.cnpj_basico = :cnpj_basico
            """)
            company_result = connection.execute(query_company_sql, {"cnpj_basico": cnpj_basico}).fetchone()

            if company_result:
                company_data = {
                    "cnpj_buscado": cnpj_value,
                    "cnpj_basico": cnpj_basico,
                    "razao_social": company_result.razao_social,
                    "capital_social": company_result.capital_social,
                    "ente_federativo_responsavel": company_result.ente_federativo_responsavel,
                    "porte_empresa": company_result.porte_empresa,
                    "natureza_juridica": company_result.natureza_juridica_descricao
                }

                query_socios_sql = text("""
                    SELECT s.cnpj_cpf_socio, s.nome_socio, s.data_entrada_sociedade, s.nome_representante, qr.descricao AS qualificacao_representante_legal, qs.descricao AS qualificacao_socio_descricao
                    FROM socios s
                    JOIN qualificacao_socio qs ON s.qualificacao_socio = qs.codigo
                    JOIN qualificacao_socio qr ON s.qualificacao_representante_legal = qr.codigo
                    WHERE s.cnpj_basico = :cnpj_basico LIMIT 100
                """)
                socios_results = connection.execute(query_socios_sql, {"cnpj_basico": cnpj_basico}).fetchall()
                list_of_socios = []
                for socio in socios_results:
                    cpf_data = None
                    try:
                        with search_CPFdb_engine.connect() as connection:
                            cpf_query_sql = text("SELECT cpf, sexo, nasc FROM cpf WHERE nome = :nome")
                            cpf_result = connection.execute(cpf_query_sql, { "nome": socio.nome_socio}).fetchone()
                            if cpf_result:
                                cpf_data = {
                                    "cpf": cpf_result.cpf,
                                    "sexo": cpf_result.sexo,
                                    "nasc": cpf_result.nasc
                                }
                    except Exception as cpf_err:
                        print(f"[ERRO] Falha ao consultar CPF {socio.cnpj_cpf_socio}: {cpf_err}")


                    list_of_socios.append({
                        "nome_socio": socio.nome_socio,
                        "data_entrada_sociedade": socio.data_entrada_sociedade,
                        "qualificacao_socio_descricao": socio.qualificacao_socio_descricao,
                        "nome_representante_legal": socio.nome_representante,
                        "cnpj_cpf_socio": cpf_data["cpf"] if cpf_data else socio.cnpj_cpf_socio,
                        "sexo": cpf_data["sexo"] if cpf_data else None,
                        "nasc": cpf_data["nasc"] if cpf_data else None,
                        "qualificacao_representante_legal": socio.qualificacao_representante_legal
                    })
                    company_data["socios"] = list_of_socios
            else:
                return jsonify({"msg": "Razão social não encontrada para o CNPJ básico fornecido."}), 200

    except Exception as e:
        print(f"Erro ao consultar Banco de Dados de CNPJ: {e}")
        return jsonify({"msg": f"Erro interno ao consultar Banco de Dados de CNPJ: {str(e)}"}), 500

    print(f"[MAIN] PID do processo principal: {os.getpid()}")

    return jsonify({"results": [company_data]}), 200


def run_flask_server(port, CPFdb_path, CNPJdb_path):
    global db
    global search_CPFdb_engine, search_CNPJdb_engine

    db.init_app(app)
    with app.app_context():
        db.create_all()

    try:
        if CPFdb_path and os.path.exists(CPFdb_path):
            app.config['SEARCH_CPFdb_URI'] = f'sqlite:///{CPFdb_path}'
            search_CPFdb_engine = create_engine(app.config['SEARCH_CPFdb_URI'])
            print(f"Banco de Dados de CPF configurado: {CPFdb_path}")
        else:
            print(f"Caminho do Banco de Dados de CPF inválido ou arquivo não encontrado: {CPFdb_path}")
            search_CPFdb_engine = None

        if CNPJdb_path and os.path.exists(CNPJdb_path):
            app.config['SEARCH_CNPJdb_URI'] = f'sqlite:///{CNPJdb_path}'
            search_CNPJdb_engine = create_engine(app.config['SEARCH_CNPJdb_URI'])
            print(f"Banco de Dados de CNPJ configurado: {CNPJdb_path}")
        else:
            print(f"Caminho do Banco de Dados de CNPJ inválido ou arquivo não encontrado: {CNPJdb_path}")
            search_CNPJdb_engine = None

    except Exception as e:
        print(f"Erro ao configurar bancos de dados de pesquisa: {e}")
        search_CPFdb_engine = None
        search_CNPJdb_engine = None

    try:
        print(f"Iniciando servidor com Waitress em http://0.0.0.0:{port}")
        serve(app, host="0.0.0.0", port=port, threads=8)
    except Exception as e:
        print(f"Erro ao iniciar o servidor Flask: {e}")

    print(f"[MAIN] PID do processo principal: {os.getpid()}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Configuração do Servidor Flask")
        master.geometry("450x300")

        self.server_process = None
        self.local_ip = get_local_ip()

        port_frame = tk.Frame(master)
        port_frame.pack(pady=5)
        self.port_label = tk.Label(port_frame, text="Porta do Servidor:")
        self.port_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(port_frame)
        self.port_entry.insert(0, "5000")
        self.port_entry.pack(side=tk.LEFT, padx=5)

        CPFdb_frame = tk.Frame(master)
        CPFdb_frame.pack(pady=5)
        self.CPFdb_label = tk.Label(CPFdb_frame, text="Caminho BD CPF:")
        self.CPFdb_label.pack(side=tk.LEFT)
        self.CPFdb_path_entry = tk.Entry(CPFdb_frame, width=40)
        self.CPFdb_path_entry.pack(side=tk.LEFT, padx=5)
        self.CPFdb_browse_button = tk.Button(CPFdb_frame, text="Procurar", command=lambda: self.browse_file(self.CPFdb_path_entry))
        self.CPFdb_browse_button.pack(side=tk.LEFT)

        CNPJdb_frame = tk.Frame(master)
        CNPJdb_frame.pack(pady=5)
        self.CNPJdb_label = tk.Label(CNPJdb_frame, text="Caminho BD CNPJ:")
        self.CNPJdb_label.pack(side=tk.LEFT)
        self.CNPJdb_path_entry = tk.Entry(CNPJdb_frame, width=40)
        self.CNPJdb_path_entry.pack(side=tk.LEFT, padx=5)
        self.CNPJdb_browse_button = tk.Button(CNPJdb_frame, text="Procurar", command=lambda: self.browse_file(self.CNPJdb_path_entry))
        self.CNPJdb_browse_button.pack(side=tk.LEFT)

        self.start_button = tk.Button(master, text="Iniciar Servidor", command=self.start_server)
        self.start_button.pack(pady=10)

        self.status_label = tk.Label(master, text="Status: Aguardando...", fg="blue")
        self.status_label.pack(pady=5)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def browse_file(self, entry_widget):
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo do Banco de Dados",
            filetypes=[("Arquivos de Banco de Dados SQLite", "*.db"), ("Todos os arquivos", "*.*")]
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def start_server(self):
        port_str = self.port_entry.get()
        CPFdb_path = self.CPFdb_path_entry.get()
        CNPJdb_path = self.CNPJdb_path_entry.get()

        try:
            port = int(port_str)
            if not (1024 <= port <= 65535):
                messagebox.showerror("Erro de Porta", "A porta deve ser um número entre 1024 e 65535.")
                return
        except ValueError:
            messagebox.showerror("Erro de Porta", "Por favor, insira um número de porta válido.")
            return

        if not CPFdb_path or not os.path.exists(CPFdb_path):
            messagebox.showwarning("Caminho Inválido", "Por favor, selecione um caminho válido para o Banco de Dados CPF.")
            return
        if not CNPJdb_path or not os.path.exists(CNPJdb_path):
            messagebox.showwarning("Caminho Inválido", "Por favor, selecione um caminho válido para o Banco de Dados CNPJ.")
            return

        if self.server_process and self.server_process.is_alive():
            messagebox.showinfo("Servidor Ativo", "O servidor já está em execução.")
            return

        self.status_label.config(text=f"Status: Iniciando servidor na porta {port}...", fg="orange")
        self.master.update_idletasks()

        self.server_process = multiprocessing.Process(
            target=run_flask_server,
            args=(port, CPFdb_path, CNPJdb_path,)
        )
        self.server_process.start()

        time.sleep(1)

        if self.server_process.is_alive():
            self.status_label.config(text=f"Status: Servidor ativo em http://{self.local_ip}:{port}", fg="green")
            print(f"Servidor Flask iniciado com PID: {self.server_process.pid}")
            print(f"Acesse em http://{self.local_ip}:{port}")
            print(f"Bancos de dados de pesquisa configurados:")
            print(f"   CPF BD: {CPFdb_path}")
            print(f"   CNPJ BD: {CNPJdb_path}")
        else:
            self.status_label.config(text="Status: Falha ao iniciar o servidor.", fg="red")
            messagebox.showerror("Erro", "Não foi possível iniciar o servidor. Verifique o console para detalhes.")

    def on_closing(self):
        if self.server_process and self.server_process.is_alive():
            print("Encerrando processo do servidor Flask...")
            self.server_process.terminate()
            self.server_process.join(timeout=5)
            if self.server_process.is_alive():
                print("Processo do servidor não encerrou. Matando...")
                self.server_process.kill()
            print("Servidor Flask encerrado.")
        self.master.destroy()

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
        multiprocessing.set_start_method('spawn', force=True)

    db = SQLAlchemy()

    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()