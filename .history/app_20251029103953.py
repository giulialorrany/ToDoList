# app.py
from flask import Flask, request, jsonify, render_template
from database import get_db_connection

app = Flask(__name__, template_folder='templates')

# ======================
# ROTA PRINCIPAL
# ======================

@app.route('/')
def index():
    return render_template('index.html')

# ======================
# API: LISTAS
# ======================

@app.route('/api/listas', methods=['GET'])
def get_listas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.id, l.nome, l.icone,
               COUNT(t.id) as total_tarefas
        FROM listas l
        LEFT JOIN tarefas t ON l.id = t.lista_id
        GROUP BY l.id
    """)
    listas = cursor.fetchall()
    conn.close()
    return jsonify(listas)

@app.route('/api/listas', methods=['POST'])
def create_lista():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO listas (nome) VALUES (%s)", (nome.strip(),))
    conn.commit()
    lista_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': lista_id, 'nome': nome, 'icone': 'casa'}), 201

# ======================
# API: TAREFAS
# ======================

@app.route('/api/listas/<int:lista_id>/tarefas', methods=['GET'])
def get_tarefas(lista_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, texto, concluida, favoritada, data_conclusao
        FROM tarefas 
        WHERE lista_id = %s
        ORDER BY concluida ASC, criada_em DESC
    """, (lista_id,))
    tarefas = cursor.fetchall()
    conn.close()

    ativas = [t for t in tarefas if not t['concluida']]
    concluidas = [t for t in tarefas if t['concluida']]
    return jsonify({'ativas': ativas, 'concluidas': concluidas})

@app.route('/api/tarefas', methods=['POST'])
def create_tarefa():
    data = request.get_json()
    lista_id = data.get('lista_id')
    texto = data.get('texto')
    data_conclusao = data.get('data_conclusao')  # '2025-04-05'

    if not lista_id or not texto:
        return jsonify({'erro': 'lista_id e texto são obrigatórios'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefas (lista_id, texto, data_conclusao)
        VALUES (%s, %s, %s)
    """, (lista_id, texto, data_conclusao))
    conn.commit()
    tarefa_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': tarefa_id}), 201

@app.route('/api/tarefas/<int:tarefa_id>', methods=['PATCH'])
def update_tarefa(tarefa_id):
    data = request.get_json()
    campos = []
    valores = []

    if 'concluida' in data:
        campos.append("concluida = %s")
        valores.append(1 if data['concluida'] else 0)
    if 'favoritada' in data:
        campos.append("favoritada = %s")
        valores.append(1 if data['favoritada'] else 0)
    if 'data_conclusao' in data:
        campos.append("data_conclusao = %s")
        valores.append(data['data_conclusao'] if data['data_conclusao'] else None)
    if 'texto' in data:
        campos.append("texto = %s")
        valores.append(data['texto'])

    if not campos:
        return jsonify({'erro': 'Nenhum campo para atualizar'}), 400

    valores.append(tarefa_id)
    query = f"UPDATE tarefas SET {', '.join(campos)} WHERE id = %s"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, valores)
    conn.commit()
    conn.close()
    return jsonify({'sucesso': True})

# ======================
# INICIAR
# ======================

if __name__ == '__main__':
    app.run(debug=True, port=5000)