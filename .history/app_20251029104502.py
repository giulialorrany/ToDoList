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
# CRUD: LISTAS
# ======================

# READ - Listar todas
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
        ORDER BY l.nome
    """)
    listas = cursor.fetchall()
    conn.close()
    return jsonify(listas)

# CREATE - Criar nova
@app.route('/api/listas', methods=['POST'])
def create_lista():
    data = request.get_json()
    nome = data.get('nome', '').strip()
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO listas (nome, icone) VALUES (%s, %s)", (nome, 'casa'))
    conn.commit()
    lista_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': lista_id, 'nome': nome, 'icone': 'casa'}), 201

# UPDATE - Renomear
@app.route('/api/listas/<int:lista_id>', methods=['PATCH'])
def update_lista(lista_id):
    data = request.get_json()
    nome = data.get('nome', '').strip()
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE listas SET nome = %s WHERE id = %s", (nome, lista_id))
    afetados = cursor.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# DELETE - Excluir
@app.route('/api/listas/<int:lista_id>', methods=['DELETE'])
def delete_lista(lista_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM listas WHERE id = %s", (lista_id,))
    afetados = cursor.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# ======================
# CRUD: TAREFAS
# ======================

# READ - Por lista
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

# CREATE
@app.route('/api/tarefas', methods=['POST'])
def create_tarefa():
    data = request.get_json()
    lista_id = data.get('lista_id')
    texto = data.get('texto', '').strip()
    data_conclusao = data.get('data_conclusao')

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

# UPDATE (concluída, favoritada, texto, data)
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
    query = f"UPDATE tarefas SET {', '.join(campos)} WHERE id = %s"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, valores)
    afetados = cursor.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# DELETE
@app.route('/api/tarefas/<int:tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = %s", (tarefa_id,))
    afetados = cursor.rowcount
    conn.commit()
    conn.close()
    return jsonify({'sucesso': afetados > 0})

# ======================
# INICIAR
# ======================
if __name__ == '__main__':
    app.run(debug=True, port=5000)