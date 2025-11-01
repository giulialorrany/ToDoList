CREATE DATABASE ToDoList CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE todolist;

-- Tabela: Listas
CREATE TABLE listas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    icone VARCHAR(50) DEFAULT 'House',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tabela: Tarefas
CREATE TABLE tarefas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lista_id INT NOT NULL,
    texto TEXT NOT NULL,
    concluida TINYINT(1) DEFAULT 0,
    favoritada TINYINT(1) DEFAULT 0,
    data_conclusao DATE NULL,  -- DATA DE CONCLUSÃO FUNCIONAL
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lista_id) REFERENCES listas(id) ON DELETE CASCADE
);