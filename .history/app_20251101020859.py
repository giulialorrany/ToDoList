from flask import Flask, request, jsonify, render_template
from database import get_db_connection

app = Flask(__name__, template_folder='templates')

# -------------------------------------------------
# FUNÇÃO AUXILIAR: conexão segura com tratamento
# -------------------------------------------------
def db():
    conn = get_db_connection()
    if not conn:
        return None, jsonify({'erro': 'Falha na conexão com o MySQL'}), 500
    return conn, None, None

# -------------------------------------------------
# SEED: insere listas padrão se o banco estiver vazio
# -------------------------------------------------
def seed_default_lists():
    conn = get_db_connection()
    if not conn:
        print("Aviso: Não foi possível conectar ao MySQL para inserir listas padrão.")
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM listas")
        if cur.fetchone()[0] == 0:
            defaults = [
                ('Meu Dia', 'sol'),
                ('Importante', 'estrela'),
                ('Planejado', 'calendario')
            ]
            cur.executemany("INSERT INTO listas (nome, icone) VALUES (%s, %s)", defaults)
            conn.commit()
            print("Listas padrão inseridas: Meu Dia, Importante, Planejado")
        cur.close()
    except Exception as e:
        print(f"Erro ao inserir listas padrão: {e}")
    finally:
        conn.close()

# -------------------------------------------------
# ROTA PRINCIPAL
# -------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ======================
# CRUD: LISTAS
# ======================

@app.route('/api/listas', methods=['GET'])
def get_listas():
    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT l.id, l.nome, l.icone,
               COUNT(t.id) AS total_tarefas
        FROM listas l
        LEFT JOIN tarefas t ON l.id = t.lista_id
        GROUP BY l.id
        ORDER BY l.nome
    """)
    listas = cur.fetchall()
    conn.close()
    return jsonify(listas)

@app.route('/api/listas', methods=['POST'])
def create_lista():
    data = request.get_json()
    nome = data.get('nome', '').strip()
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute("INSERT INTO listas (nome, icone) VALUES (%s, %s)", (nome, 'casa'))
    conn.commit()
    lista_id = cur.lastrowid
    conn.close()
    return jsonify({'id': lista_id, 'nome': nome, 'icone': 'casa'}), 201

@app.route('/api/listas/<int:lista_id>', methods=['PATCH'])
def update_lista(lista_id):
    data = request.get_json()
    nome = data.get('nome', '').strip()
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute("UPDATE listas SET nome = %s WHERE id = %s", (nome, lista_id))
    afetados = cur.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

@app.route('/api/listas/<int:lista_id>', methods=['DELETE'])
def delete_lista(lista_id):
    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute("DELETE FROM listas WHERE id = %s", (lista_id,))
    afetados = cur.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# ======================
# CRUD: TAREFAS
# ======================

@app.route('/api/listas/<int:lista_id>/tarefas', methods=['GET'])
def get_tarefas(lista_id):
    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, texto, concluida, favoritada
        FROM tarefas
        WHERE lista_id = %s
        ORDER BY concluida ASC, criada_em DESC
    """, (lista_id,))
    tarefas = cur.fetchall()
    conn.close()

    ativas = [t for t in tarefas if not t['concluida']]
    concluidas = [t for t in tarefas if t['concluida']]
    return jsonify({'ativas': ativas, 'concluidas': concluidas})

@app.route('/api/tarefas', methods=['POST'])
def create_tarefa():
    data = request.get_json()
    lista_id = data.get('lista_id')
    texto = data.get('texto', '').strip()

    if not lista_id or not texto:
        return jsonify({'erro': 'lista_id e texto são obrigatórios'}), 400

    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tarefas (lista_id, texto)
        VALUES (%s, %s)
    """, (lista_id, texto))
    conn.commit()
    tarefa_id = cur.lastrowid
    conn.close()
    return jsonify({'id': tarefa_id}), 201

@app.route('/api/tarefas/<int:tarefa_id>', methods=['PATCH'])
def update_tarefa(tarefa_id):
    data = request.get_json()
    campos, valores = [], []

    if 'concluida' in data:
        campos.append("concluida = %s")
        valores.append(1 if data['concluida'] else 0)
    if 'favoritada' in data:
        campos.append("favoritada = %s")
        valores.append(1 if data['favoritada'] else 0)
    if 'texto' in data:
        texto = data['texto'].strip()
        if not texto:
            return jsonify({'erro': 'Texto não pode ser vazio'}), 400
        campos.append("texto = %s")
        valores.append(texto)
    if 'data_conclusao' in data:
        campos.append("data_conclusao = %s")
        valores.append(data['data_conclusao'] if data['data_conclusao'] else None)

    if not campos:
        return jsonify({'erro': 'Nenhum campo para atualizar'}), 400

    valores.append(tarefa_id)
    sql = f"UPDATE tarefas SET {', '.join(campos)} WHERE id = %s"

    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute(sql, valores)
    afetados = cur.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

@app.route('/api/tarefas/<int:tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):
    conn, err_resp, err_code = db()
    if err_resp:
        return err_resp, err_code

    cur = conn.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = %s", (tarefa_id,))
    afetados = cur.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# -------------------------------------------------
# INICIAR SERVIDOR
# -------------------------------------------------
if __name__ == '__main__':
    seed_default_lists()  # Cria listas padrão na primeira execução
    print("Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)